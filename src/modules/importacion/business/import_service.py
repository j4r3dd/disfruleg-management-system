# -*- coding: utf-8 -*-
"""
Import Service - Business Logic
Handles the core import workflow
NO direct database access - uses repositories only!
"""

from typing import List, Tuple
from decimal import Decimal
from datetime import datetime
from pathlib import Path

from ..data.repositories import (
    IProductRepository,
    IPriceRepository,
    ISystemRepository
)
from ..domain.models import (
    ExtractedProduct,
    ProductChange,
    ImportReport,
    SystemIntegrityCheck
)
from ..domain.exceptions import (
    PriceApplicationError,
    SystemIntegrityError
)


class ImportService:
    """
    Import service - orchestrates the import workflow
    Coordinates between repositories to manage imports
    """

    def __init__(
        self,
        product_repo: IProductRepository,
        price_repo: IPriceRepository,
        system_repo: ISystemRepository
    ):
        """
        Initialize service with injected dependencies

        Args:
            product_repo: Product repository
            price_repo: Price repository
            system_repo: System repository
        """
        self.product_repo = product_repo
        self.price_repo = price_repo
        self.system_repo = system_repo

    def validate_system_integrity(self) -> SystemIntegrityCheck:
        """
        Validate system integrity before import

        Returns:
            SystemIntegrityCheck with results

        Raises:
            SystemIntegrityError: If check fails
        """
        return self.system_repo.check_integrity()

    def generate_changes(
        self,
        extracted_products: List[ExtractedProduct],
        actualizar_existentes: bool,
        agregar_nuevos: bool
    ) -> Tuple[List[ProductChange], List[ExtractedProduct]]:
        """
        Generate proposed changes from extracted products

        Args:
            extracted_products: Products extracted from PDF
            actualizar_existentes: Whether to update existing products
            agregar_nuevos: Whether to add new products

        Returns:
            Tuple of (changes list, products without price)

        Raises:
            ValueError: If validation fails
        """
        # Fail fast: Validate inputs
        if not extracted_products:
            raise ValueError("Extracted products list cannot be empty")

        cambios = []
        productos_sin_precio = []

        for prod_pdf in extracted_products:
            # Search for matching product in database
            producto_bd = self.product_repo.search_similar(
                prod_pdf.nombre,
                prod_pdf.unidad
            )

            if producto_bd:
                # Product exists - update if enabled
                if actualizar_existentes:
                    cambio = ProductChange(
                        tipo='actualizar',
                        id_producto=producto_bd.id,
                        nombre=producto_bd.nombre,
                        unidad=producto_bd.unidad,
                        precio_nuevo=prod_pdf.precio,
                        tiene_precio=prod_pdf.tiene_precio,
                        stock=producto_bd.stock
                    )
                    cambios.append(cambio)

                    if not prod_pdf.tiene_precio:
                        productos_sin_precio.append(prod_pdf)
            else:
                # New product - add if enabled
                if agregar_nuevos:
                    cambio = ProductChange(
                        tipo='nuevo',
                        nombre=prod_pdf.nombre,
                        unidad=prod_pdf.unidad,
                        precio_nuevo=prod_pdf.precio,
                        tiene_precio=prod_pdf.tiene_precio,
                        stock=Decimal('0')
                    )
                    cambios.append(cambio)

                    if not prod_pdf.tiene_precio:
                        productos_sin_precio.append(prod_pdf)

        return cambios, productos_sin_precio

    def apply_changes(
        self,
        cambios: List[ProductChange],
        usuario: str,
        target_group_id: int
    ) -> Tuple[int, List[int]]:
        """
        Apply proposed changes to database for a specific group

        Args:
            cambios: List of changes to apply
            usuario: Username performing the import
            target_group_id: ID of the group to apply prices to

        Returns:
            Tuple of (successful changes count, list of created product IDs)

        Raises:
            PriceApplicationError: If application fails
            ValueError: If validation fails
        """
        # Fail fast: Validate inputs
        if not cambios:
            raise ValueError("Changes list cannot be empty")

        if not usuario or not usuario.strip():
            raise ValueError("Usuario cannot be empty")

        if target_group_id <= 0:
            raise ValueError("target_group_id must be positive")

        # Validate target group exists
        grupos = self.price_repo.get_all_groups_with_discounts()
        # Handle both dict and tuple formats
        group_ids = [g['id_grupo'] if isinstance(g, dict) else g[0] for g in grupos]
        if target_group_id not in group_ids:
            raise PriceApplicationError(f"Target group {target_group_id} not found")

        cambios_exitosos = 0
        productos_creados = []

        try:
            for cambio in cambios:
                precio_base = cambio.precio_nuevo

                if cambio.tipo == 'nuevo':
                    # Create new product
                    nuevo_id = self.product_repo.create_product(
                        nombre=cambio.nombre,
                        unidad=cambio.unidad,
                        stock=Decimal('0'),
                        es_especial=False
                    )

                    productos_creados.append(nuevo_id)

                    # Apply price to target group only
                    self.price_repo.set_price_for_group(
                        product_id=nuevo_id,
                        group_id=target_group_id,
                        precio_base=precio_base
                    )

                    cambios_exitosos += 1

                elif cambio.tipo == 'actualizar':
                    # Update existing product price for target group only
                    self.price_repo.set_price_for_group(
                        product_id=cambio.id_producto,
                        group_id=target_group_id,
                        precio_base=precio_base
                    )

                    cambios_exitosos += 1

            # Get target group info for log
            if grupos and isinstance(grupos[0], dict):
                target_group = next((g for g in grupos if g['id_grupo'] == target_group_id), None)
                group_name = target_group['clave_grupo'] if target_group else f"ID {target_group_id}"
            else:
                target_group = next((g for g in grupos if g[0] == target_group_id), None)
                group_name = target_group[1] if target_group else f"ID {target_group_id}"

            # Log the operation
            detalle_log = (
                f"Importación: {cambios_exitosos} cambios aplicados "
                f"al grupo '{group_name}'"
            )
            self.system_repo.log_import_operation(usuario, detalle_log)

            return cambios_exitosos, productos_creados

        except Exception as e:
            raise PriceApplicationError(f"Error applying changes: {e}")

    def get_statistics(
        self,
        cambios: List[ProductChange]
    ) -> Tuple[int, int, int]:
        """
        Get statistics about proposed changes

        Args:
            cambios: List of changes

        Returns:
            Tuple of (total, new, updated)
        """
        total = len(cambios)
        nuevos = sum(1 for c in cambios if c.tipo == 'nuevo')
        actualizados = sum(1 for c in cambios if c.tipo == 'actualizar')

        return total, nuevos, actualizados
