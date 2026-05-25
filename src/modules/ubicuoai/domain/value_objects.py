# -*- coding: utf-8 -*-
"""
Value Objects - Domain Layer
Immutable value objects for ubicuoai module
"""

from enum import Enum
from typing import Dict, List


class MatchMethod(Enum):
    """Method used to match a product"""
    EXACT = "exact"
    LEARNED = "learned"
    FUZZY = "fuzzy"
    MANUAL = "manual"
    NONE = "none"


class Unit(Enum):
    """Product units - Values match database exactly"""
    # Weight units
    KG = "kg"
    G = "g"

    # Volume units
    LT = "lt"

    # Count units
    PZ = "pz"
    DOCENA = "docena"

    # Container units
    MJO = "mjo"  # manojo
    CAJA = "caja"
    BOLSA = "bolsa"
    PAQ = "paq"  # paquete
    BOTE = "bote"
    BOTELLA = "botella"
    LATA = "lata"
    CUBETA = "cubeta"
    ROLLO = "rollo"
    TABLETA = "tableta"
    BURBUJA = "burbuja"

    # Special units
    GRANEL = "granel"
    SECCION = "seccion"  # Special unit for section headers

    @classmethod
    def normalize(cls, unit_str: str) -> 'Unit':
        """
        Normalize a unit string to standard Unit enum

        Args:
            unit_str: Unit string to normalize (e.g., 'kgs', 'kilos', 'kg')

        Returns:
            Unit enum value

        Raises:
            ValueError: If unit cannot be normalized
        """
        unit_map: Dict[str, Unit] = {
            # KG variants (weight)
            'kg': cls.KG, 'kgs': cls.KG, 'k': cls.KG,
            'kilo': cls.KG, 'kilos': cls.KG, 'kilogramo': cls.KG, 'kilogramos': cls.KG,

            # G variants (weight)
            'g': cls.G, 'gr': cls.G, 'grs': cls.G,
            'gramo': cls.G, 'gramos': cls.G,

            # LT variants (volume)
            'lt': cls.LT, 'lts': cls.LT, 'l': cls.LT,
            'litro': cls.LT, 'litros': cls.LT,

            # PZ variants (count)
            'pz': cls.PZ, 'pza': cls.PZ, 'pzs': cls.PZ,
            'pieza': cls.PZ, 'piezas': cls.PZ,
            'unidad': cls.PZ, 'unidades': cls.PZ,

            # DOCENA variants (count)
            'docena': cls.DOCENA, 'docenas': cls.DOCENA, 'dz': cls.DOCENA,

            # MJO variants (container)
            'mjo': cls.MJO, 'manojo': cls.MJO, 'manojos': cls.MJO,
            'ramo': cls.MJO, 'ramos': cls.MJO,

            # CAJA variants (container)
            'caja': cls.CAJA, 'cajas': cls.CAJA,
            'charola': cls.CAJA, 'charolas': cls.CAJA,

            # BOLSA variants (container)
            'bolsa': cls.BOLSA, 'bolsas': cls.BOLSA,

            # PAQ variants (container)
            'paq': cls.PAQ, 'paqs': cls.PAQ,
            'paquete': cls.PAQ, 'paquetes': cls.PAQ,

            # BOTE variants (container)
            'bote': cls.BOTE, 'botes': cls.BOTE,
            'frasco': cls.BOTE, 'frascos': cls.BOTE,

            # BOTELLA variants (container)
            'botella': cls.BOTELLA, 'botellas': cls.BOTELLA,

            # LATA variants (container)
            'lata': cls.LATA, 'latas': cls.LATA,

            # CUBETA variants (container)
            'cubeta': cls.CUBETA, 'cubetas': cls.CUBETA,

            # ROLLO variants (container)
            'rollo': cls.ROLLO, 'rollos': cls.ROLLO,

            # TABLETA variants (container)
            'tableta': cls.TABLETA, 'tabletas': cls.TABLETA,
            'barra': cls.TABLETA, 'barras': cls.TABLETA,

            # BURBUJA variants (container)
            'burbuja': cls.BURBUJA, 'burbujas': cls.BURBUJA,

            # GRANEL (special)
            'granel': cls.GRANEL
        }

        normalized_str = unit_str.strip().lower()

        if normalized_str in unit_map:
            return unit_map[normalized_str]

        raise ValueError(f"Cannot normalize unit: {unit_str}")

    @classmethod
    def get_variants(cls, unit: 'Unit') -> List[str]:
        """
        Get all string variants for a unit

        Args:
            unit: Unit enum value

        Returns:
            List of string variants for this unit
        """
        variants_map: Dict[Unit, List[str]] = {
            cls.KG: ['kg', 'kgs', 'k', 'kilo', 'kilos', 'kilogramo', 'kilogramos'],
            cls.G: ['g', 'gr', 'grs', 'gramo', 'gramos'],
            cls.LT: ['lt', 'lts', 'l', 'litro', 'litros'],
            cls.PZ: ['pz', 'pza', 'pzs', 'pieza', 'piezas', 'unidad', 'unidades'],
            cls.DOCENA: ['docena', 'docenas', 'dz'],
            cls.MJO: ['mjo', 'manojo', 'manojos', 'ramo', 'ramos'],
            cls.CAJA: ['caja', 'cajas', 'charola', 'charolas'],
            cls.BOLSA: ['bolsa', 'bolsas'],
            cls.PAQ: ['paq', 'paqs', 'paquete', 'paquetes'],
            cls.BOTE: ['bote', 'botes', 'frasco', 'frascos'],
            cls.BOTELLA: ['botella', 'botellas'],
            cls.LATA: ['lata', 'latas'],
            cls.CUBETA: ['cubeta', 'cubetas'],
            cls.ROLLO: ['rollo', 'rollos'],
            cls.TABLETA: ['tableta', 'tabletas', 'barra', 'barras'],
            cls.BURBUJA: ['burbuja', 'burbujas'],
            cls.GRANEL: ['granel']
        }

        return variants_map.get(unit, [])

    @classmethod
    def are_equivalent(cls, unit1: str, unit2: str) -> bool:
        """
        Check if two unit strings are equivalent

        Args:
            unit1: First unit string
            unit2: Second unit string

        Returns:
            True if units are equivalent
        """
        try:
            normalized1 = cls.normalize(unit1)
            normalized2 = cls.normalize(unit2)
            return normalized1 == normalized2
        except ValueError:
            return False
