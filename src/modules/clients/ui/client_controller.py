# -*- coding: utf-8 -*-
"""
Capa de UI - Controlador de Clientes
Orquesta las interacciones del usuario, delega lógica de negocio a servicios.
"""
from typing import List, Optional
from tkinter import messagebox
from ..domain.models import (
    Client,
    Group,
    ClientType,
    ClientSearchCriteria,
    BusinessLogicError,
    ClientNotFoundError,
    ClientHasInvoicesError,
    GroupNotFoundError,
    GroupInUseError,
    ClientTypeNotFoundError,
    ClientTypeInUseError,
)
from ..business import ClientService, GroupService, ClientTypeService
class ClientController:
    """
    Controlador para la UI de gestión de clientes.
    Maneja acciones del usuario y orquesta servicios.
    """
    def __init__(
        self,
        client_service: ClientService,
        group_service: GroupService,
        client_type_service: ClientTypeService
    ):
        """Inicializar controlador con servicios"""
        if client_service is None:
            raise ValueError("El servicio de clientes no puede ser None")
        if group_service is None:
            raise ValueError("El servicio de grupos no puede ser None")
        if client_type_service is None:
            raise ValueError("El servicio de tipos de cliente no puede ser None")
        self.client_service = client_service
        self.group_service = group_service
        self.client_type_service = client_type_service
    # Operaciones de clientes
    def get_all_clients(self) -> List[Client]:
        """Obtener todos los clientes"""
        try:
            return self.client_service.get_all_clients()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar clientes: {str(e)}")
            return []
    def search_clients(self, criteria: ClientSearchCriteria) -> List[Client]:
        """Buscar clientes con filtros"""
        try:
            return self.client_service.search_clients(criteria)
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clientes: {str(e)}")
            return []
    def create_client(self, client_data: dict) -> Optional[Client]:
        """Crear un nuevo cliente"""
        try:
            client = self.client_service.create_client(
                nombre_cliente=client_data['nombre_cliente'],
                id_grupo=client_data['id_grupo'],
                telefono=client_data.get('telefono'),
                correo=client_data.get('correo'),
                rfc=client_data.get('rfc'),
                razon_social=client_data.get('razon_social'),
                regimen_fiscal=client_data.get('regimen_fiscal'),
                codigo_postal=client_data.get('codigo_postal'),
                direccion_fiscal=client_data.get('direccion_fiscal'),
                notas=client_data.get('notas')
            )
            messagebox.showinfo("Éxito", f"Cliente '{client.nombre_cliente}' creado exitosamente")
            return client
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
            return None
        except BusinessLogicError as e:
            messagebox.showerror("Error de Negocio", str(e))
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear cliente: {str(e)}")
            return None
    def update_client(self, client_id: int, client_data: dict) -> Optional[Client]:
        """Actualizar cliente existente"""
        try:
            client = self.client_service.update_client(
                client_id=client_id,
                nombre_cliente=client_data['nombre_cliente'],
                id_grupo=client_data['id_grupo'],
                telefono=client_data.get('telefono'),
                correo=client_data.get('correo'),
                rfc=client_data.get('rfc'),
                razon_social=client_data.get('razon_social'),
                regimen_fiscal=client_data.get('regimen_fiscal'),
                codigo_postal=client_data.get('codigo_postal'),
                direccion_fiscal=client_data.get('direccion_fiscal'),
                notas=client_data.get('notas')
            )
            messagebox.showinfo("Éxito", f"Cliente '{client.nombre_cliente}' actualizado exitosamente")
            return client
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
            return None
        except ClientNotFoundError as e:
            messagebox.showerror("No Encontrado", str(e))
            return None
        except BusinessLogicError as e:
            messagebox.showerror("Error de Negocio", str(e))
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar cliente: {str(e)}")
            return None
    def toggle_client_status(self, client_id: int) -> Optional[Client]:
        """Alternar estado activo/inactivo del cliente"""
        try:
            # Obtener cliente actual para determinar acción
            client = self.client_service.get_client_by_id(client_id)
            action = "desactivar" if client.activo else "activar"
            if not messagebox.askyesno(
                "Confirmar",
                f"¿Está seguro que desea {action} este cliente?"
            ):
                return None
            updated_client = self.client_service.toggle_client_status(client_id)
            status = "activado" if updated_client.activo else "desactivado"
            messagebox.showinfo("Éxito", f"Cliente {status} exitosamente")
            return updated_client
        except ClientNotFoundError as e:
            messagebox.showerror("No Encontrado", str(e))
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")
            return None

    def deactivate_client(self, client_id: int) -> bool:
        """Desactivar cliente (soft delete)"""
        try:
            client = self.client_service.get_client_by_id(client_id)
            self.client_service.deactivate_client(client_id)
            messagebox.showinfo("Éxito", f"Cliente '{client.nombre_cliente}' desactivado exitosamente")
            return True
        except ClientNotFoundError as e:
            messagebox.showerror("No Encontrado", str(e))
            return False
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error al desactivar cliente: {str(e)}")
            return False

    def activate_client(self, client_id: int) -> bool:
        """Activar cliente previamente desactivado"""
        try:
            client = self.client_service.get_client_by_id(client_id)
            self.client_service.activate_client(client_id)
            messagebox.showinfo("Éxito", f"Cliente '{client.nombre_cliente}' activado exitosamente")
            return True
        except ClientNotFoundError as e:
            messagebox.showerror("No Encontrado", str(e))
            return False
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error al activar cliente: {str(e)}")
            return False

    def delete_client(self, client_id: int) -> bool:
        """Eliminar cliente"""
        try:
            # Obtener info del cliente para confirmación
            client = self.client_service.get_client_by_id(client_id)
            has_invoices, count = self.client_service.get_client_invoice_info(client_id)
            # Construir mensaje de confirmación
            if has_invoices:
                message = (
                    f"⚠️ ADVERTENCIA: El cliente '{client.nombre_cliente}' tiene {count} facturas.\n\n"
                    f"Eliminar este cliente:\n"
                    f"• Eliminará TODAS las facturas\n"
                    f"• Eliminará TODOS los detalles de factura\n"
                    f"• Eliminará TODAS las deudas\n"
                    f"• Esta acción NO SE PUEDE DESHACER\n\n"
                    f"¿Está COMPLETAMENTE SEGURO?"
                )
            else:
                message = f"¿Está seguro que desea eliminar al cliente '{client.nombre_cliente}'?\n\nEsta acción no se puede deshacer."
            if not messagebox.askyesno("⚠️ Confirmar Eliminación", message):
                return False
            # Confirmación doble para clientes con facturas
            if has_invoices:
                if not messagebox.askyesno(
                    "⚠️ Confirmación Final",
                    f"Esta es su última oportunidad.\n\n¿REALMENTE desea eliminar '{client.nombre_cliente}' y {count} facturas?"
                ):
                    return False
            self.client_service.delete_client(client_id)
            messagebox.showinfo("Éxito", f"Cliente '{client.nombre_cliente}' eliminado exitosamente")
            return True
        except ClientNotFoundError as e:
            messagebox.showerror("No Encontrado", str(e))
            return False
        except ClientHasInvoicesError as e:
            messagebox.showerror("No se Puede Eliminar", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar cliente: {str(e)}")
            return False
    # Operaciones de grupos
    def get_all_groups(self) -> List[Group]:
        """Obtener todos los grupos"""
        try:
            return self.group_service.get_all_groups()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar grupos: {str(e)}")
            return []
    def create_group(self, group_data: dict) -> Optional[Group]:
        """Crear un nuevo grupo"""
        try:
            group = self.group_service.create_group(
                clave_grupo=group_data['clave_grupo'],
                id_tipo_cliente=group_data['id_tipo_cliente'],
                descripcion=group_data.get('descripcion')
            )
            messagebox.showinfo("Éxito", f"Grupo '{group.clave_grupo}' creado exitosamente")
            return group
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
            return None
        except BusinessLogicError as e:
            messagebox.showerror("Error de Negocio", str(e))
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear grupo: {str(e)}")
            return None
    def update_group(self, group_id: int, group_data: dict) -> Optional[Group]:
        """Actualizar grupo existente"""
        try:
            group = self.group_service.update_group(
                group_id=group_id,
                clave_grupo=group_data['clave_grupo'],
                id_tipo_cliente=group_data['id_tipo_cliente'],
                descripcion=group_data.get('descripcion')
            )
            messagebox.showinfo("Éxito", f"Grupo '{group.clave_grupo}' actualizado exitosamente")
            return group
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
            return None
        except GroupNotFoundError as e:
            messagebox.showerror("No Encontrado", str(e))
            return None
        except BusinessLogicError as e:
            messagebox.showerror("Error de Negocio", str(e))
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar grupo: {str(e)}")
            return None
    def delete_group(self, group_id: int) -> bool:
        """Eliminar grupo"""
        try:
            group = self.group_service.get_group_by_id(group_id)
            in_use, count = self.group_service.get_group_usage_info(group_id)
            if in_use:
                messagebox.showerror(
                    "No se Puede Eliminar",
                    f"El grupo '{group.clave_grupo}' está siendo usado por {count} clientes.\n"
                    f"Reasigne o elimine estos clientes primero."
                )
                return False
            if not messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Está seguro que desea eliminar el grupo '{group.clave_grupo}'?"
            ):
                return False
            self.group_service.delete_group(group_id)
            messagebox.showinfo("Éxito", f"Grupo '{group.clave_grupo}' eliminado exitosamente")
            return True
        except GroupNotFoundError as e:
            messagebox.showerror("No Encontrado", str(e))
            return False
        except GroupInUseError as e:
            messagebox.showerror("No se Puede Eliminar", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar grupo: {str(e)}")
            return False
    # Operaciones de tipos de cliente
    def get_all_client_types(self) -> List[ClientType]:
        """Obtener todos los tipos de cliente"""
        try:
            return self.client_type_service.get_all_client_types()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar tipos de cliente: {str(e)}")
            return []
    def create_client_type(self, type_data: dict) -> Optional[ClientType]:
        """Crear un nuevo tipo de cliente"""
        try:
            client_type = self.client_type_service.create_client_type(
                nombre_tipo=type_data['nombre_tipo'],
                descuento=type_data['descuento']
            )
            messagebox.showinfo("Éxito", f"Tipo de cliente '{client_type.nombre_tipo}' creado exitosamente")
            return client_type
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear tipo de cliente: {str(e)}")
            return None
    def update_client_type(self, type_id: int, type_data: dict) -> Optional[ClientType]:
        """Actualizar tipo de cliente existente"""
        try:
            client_type = self.client_type_service.update_client_type(
                type_id=type_id,
                nombre_tipo=type_data['nombre_tipo'],
                descuento=type_data['descuento']
            )
            messagebox.showinfo("Éxito", f"Tipo de cliente '{client_type.nombre_tipo}' actualizado exitosamente")
            return client_type
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
            return None
        except ClientTypeNotFoundError as e:
            messagebox.showerror("No Encontrado", str(e))
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar tipo de cliente: {str(e)}")
            return None
    def delete_client_type(self, type_id: int) -> bool:
        """Eliminar tipo de cliente"""
        try:
            client_type = self.client_type_service.get_client_type_by_id(type_id)
            in_use, count = self.client_type_service.get_client_type_usage_info(type_id)
            if in_use:
                messagebox.showerror(
                    "No se Puede Eliminar",
                    f"El tipo de cliente '{client_type.nombre_tipo}' está siendo usado por {count} grupos.\n"
                    f"Reasigne o elimine estos grupos primero."
                )
                return False
            if not messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Está seguro que desea eliminar el tipo de cliente '{client_type.nombre_tipo}'?"
            ):
                return False
            self.client_type_service.delete_client_type(type_id)
            messagebox.showinfo("Éxito", f"Tipo de cliente '{client_type.nombre_tipo}' eliminado exitosamente")
            return True
        except ClientTypeNotFoundError as e:
            messagebox.showerror("No Encontrado", str(e))
            return False
        except ClientTypeInUseError as e:
            messagebox.showerror("No se Puede Eliminar", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar tipo de cliente: {str(e)}")
            return False