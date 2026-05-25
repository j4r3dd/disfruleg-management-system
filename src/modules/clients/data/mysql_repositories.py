# -*- coding: utf-8 -*-
"""
Data Layer - MySQL Repository Implementations
These implement the repository interfaces for MySQL database.
"""

from typing import List, Optional
from decimal import Decimal
import pymysql.cursors
from ..domain.models import Client, Group, ClientType, ClientSearchCriteria
from .repositories import IClientRepository, IGroupRepository, IClientTypeRepository


class MySQLClientRepository:
    """MySQL implementation of client repository"""

    def __init__(self, connection):
        """
        Initialize with database connection

        Args:
            connection: MySQL database connection
        """
        if connection is None:
            raise ValueError("Database connection cannot be None")
        self.conn = connection
        self.cursor = connection.cursor()

    def get_by_id(self, client_id: int) -> Optional[Client]:
        """Get client by ID"""
        if client_id is None or client_id <= 0:
            return None

        self.cursor.execute("""
            SELECT c.id_cliente, c.nombre_cliente, c.telefono, c.correo,
                   c.rfc, c.razon_social, c.regimen_fiscal, c.codigo_postal,
                   c.direccion_fiscal, c.activo, c.notas, c.id_grupo,
                   g.clave_grupo, tc.nombre_tipo, tc.descuento
            FROM cliente c
            JOIN grupo g ON c.id_grupo = g.id_grupo
            JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
            WHERE c.id_cliente = %s
        """, (client_id,))

        row = self.cursor.fetchone()
        return self._map_to_client(row) if row else None

    def get_all(self) -> List[Client]:
        """Get all clients"""
        self.cursor.execute("""
            SELECT c.id_cliente, c.nombre_cliente, c.telefono, c.correo,
                   c.rfc, c.razon_social, c.regimen_fiscal, c.codigo_postal,
                   c.direccion_fiscal, c.activo, c.notas, c.id_grupo,
                   g.clave_grupo, tc.nombre_tipo, tc.descuento
            FROM cliente c
            JOIN grupo g ON c.id_grupo = g.id_grupo
            JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
            ORDER BY c.nombre_cliente
        """)

        rows = self.cursor.fetchall()
        return [self._map_to_client(row) for row in rows]

    def search(self, criteria: ClientSearchCriteria) -> List[Client]:
        """Search clients with filters"""
        # Get all clients first
        clients = self.get_all()

        # Apply filters
        if criteria.search_text:
            search_lower = criteria.search_text.lower()
            clients = [c for c in clients if (
                search_lower in (c.nombre_cliente or '').lower() or
                search_lower in (c.telefono or '').lower() or
                search_lower in (c.correo or '').lower() or
                search_lower in (c.rfc or '').lower()
            )]

        if criteria.group_filter and criteria.group_filter != "Todos":
            clients = [c for c in clients if c.clave_grupo == criteria.group_filter]

        if criteria.status_filter == "Activos":
            clients = [c for c in clients if c.activo]
        elif criteria.status_filter == "Inactivos":
            clients = [c for c in clients if not c.activo]

        if criteria.discount_filter and criteria.discount_filter != "Todos":
            clients = self._apply_discount_filter(clients, criteria.discount_filter)

        return clients

    def _apply_discount_filter(self, clients: List[Client], filter_value: str) -> List[Client]:
        """Apply discount filter to client list"""
        filtered = []
        for client in clients:
            discount = float(client.descuento or 0)
            if filter_value == "Sin descuento" and discount == 0:
                filtered.append(client)
            elif filter_value == "1-10%" and 1 <= discount <= 10:
                filtered.append(client)
            elif filter_value == "11-20%" and 11 <= discount <= 20:
                filtered.append(client)
            elif filter_value == "21-50%" and 21 <= discount <= 50:
                filtered.append(client)
            elif filter_value == "51%+" and discount > 50:
                filtered.append(client)
        return filtered

    def create(self, client: Client) -> int:
        """Create a new client, returns the new client ID"""
        self.cursor.execute("""
            INSERT INTO cliente
            (nombre_cliente, telefono, correo, rfc, razon_social,
             regimen_fiscal, codigo_postal, direccion_fiscal, notas,
             activo, id_grupo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            client.nombre_cliente,
            client.telefono,
            client.correo,
            client.rfc,
            client.razon_social,
            client.regimen_fiscal,
            client.codigo_postal,
            client.direccion_fiscal,
            client.notas,
            client.activo,
            client.id_grupo
        ))

        self.conn.commit()
        return self.cursor.lastrowid

    def update(self, client: Client) -> None:
        """Update existing client"""
        if client.id_cliente is None:
            raise ValueError("Cannot update client without ID")

        self.cursor.execute("""
            UPDATE cliente
            SET nombre_cliente = %s, telefono = %s, correo = %s,
                rfc = %s, razon_social = %s, regimen_fiscal = %s,
                codigo_postal = %s, direccion_fiscal = %s, notas = %s,
                id_grupo = %s
            WHERE id_cliente = %s
        """, (
            client.nombre_cliente,
            client.telefono,
            client.correo,
            client.rfc,
            client.razon_social,
            client.regimen_fiscal,
            client.codigo_postal,
            client.direccion_fiscal,
            client.notas,
            client.id_grupo,
            client.id_cliente
        ))

        self.conn.commit()

    def delete(self, client_id: int) -> None:
        """Delete client and all related records"""
        if client_id is None or client_id <= 0:
            raise ValueError("Invalid client ID")

        # Start transaction
        self.conn.autocommit = False

        try:
            # Delete related records in order
            self.cursor.execute("""
                DELETE df FROM detalle_factura df
                JOIN factura f ON df.id_factura = f.id_factura
                WHERE f.id_cliente = %s
            """, (client_id,))

            self.cursor.execute("""
                DELETE sf FROM seccion_factura sf
                JOIN factura f ON sf.id_factura = f.id_factura
                WHERE f.id_cliente = %s
            """, (client_id,))

            self.cursor.execute("""
                DELETE fm FROM factura_metadata fm
                JOIN factura f ON fm.id_factura = f.id_factura
                WHERE f.id_cliente = %s
            """, (client_id,))

            self.cursor.execute("DELETE FROM deudas WHERE id_cliente = %s", (client_id,))
            self.cursor.execute("DELETE FROM ordenes_guardadas WHERE id_cliente = %s", (client_id,))
            self.cursor.execute("DELETE FROM factura WHERE id_cliente = %s", (client_id,))
            self.cursor.execute("DELETE FROM cliente WHERE id_cliente = %s", (client_id,))

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.conn.autocommit = True

    def toggle_status(self, client_id: int, active: bool) -> None:
        """Toggle client active/inactive status"""
        if client_id is None or client_id <= 0:
            raise ValueError("Invalid client ID")

        self.cursor.execute("""
            UPDATE cliente
            SET activo = %s
            WHERE id_cliente = %s
        """, (active, client_id))

        self.conn.commit()

    def count_by_group(self, group_id: int) -> int:
        """Count clients in a group"""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM cliente WHERE id_grupo = %s",
            (group_id,)
        )
        result = self.cursor.fetchone()
        return result['count'] if result else 0

    def has_invoices(self, client_id: int) -> tuple[bool, int]:
        """Check if client has invoices, returns (has_invoices, count)"""
        self.cursor.execute("""
            SELECT COUNT(*) as count
            FROM factura
            WHERE id_cliente = %s
        """, (client_id,))

        result = self.cursor.fetchone()
        count = result['count'] if result else 0
        return (count > 0, count)

    def _map_to_client(self, row: dict) -> Client:
        """Map database row to Client entity"""
        return Client(
            id_cliente=row['id_cliente'],
            nombre_cliente=row['nombre_cliente'],
            telefono=row.get('telefono'),
            correo=row.get('correo'),
            rfc=row.get('rfc'),
            razon_social=row.get('razon_social'),
            regimen_fiscal=row.get('regimen_fiscal'),
            codigo_postal=row.get('codigo_postal'),
            direccion_fiscal=row.get('direccion_fiscal'),
            activo=row['activo'],
            notas=row.get('notas'),
            id_grupo=row['id_grupo'],
            clave_grupo=row.get('clave_grupo'),
            nombre_tipo=row.get('nombre_tipo'),
            descuento=row.get('descuento')
        )


class MySQLGroupRepository:
    """MySQL implementation of group repository"""

    def __init__(self, connection):
        """Initialize with database connection"""
        if connection is None:
            raise ValueError("Database connection cannot be None")
        self.conn = connection
        self.cursor = connection.cursor()

    def get_by_id(self, group_id: int) -> Optional[Group]:
        """Get group by ID"""
        if group_id is None or group_id <= 0:
            return None

        self.cursor.execute("""
            SELECT g.id_grupo, g.clave_grupo, g.descripcion, g.id_tipo_cliente,
                   tc.nombre_tipo, tc.descuento
            FROM grupo g
            LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
            WHERE g.id_grupo = %s
        """, (group_id,))

        row = self.cursor.fetchone()
        return self._map_to_group(row) if row else None

    def get_all(self) -> List[Group]:
        """Get all groups with type information"""
        self.cursor.execute("""
            SELECT g.id_grupo, g.clave_grupo, g.descripcion, g.id_tipo_cliente,
                   tc.nombre_tipo, tc.descuento
            FROM grupo g
            LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
            ORDER BY g.clave_grupo
        """)

        rows = self.cursor.fetchall()
        return [self._map_to_group(row) for row in rows]

    def create(self, group: Group) -> int:
        """Create a new group, returns the new group ID"""
        self.cursor.execute("""
            INSERT INTO grupo (clave_grupo, descripcion, id_tipo_cliente)
            VALUES (%s, %s, %s)
        """, (group.clave_grupo, group.descripcion, group.id_tipo_cliente))

        self.conn.commit()
        return self.cursor.lastrowid

    def update(self, group: Group) -> None:
        """Update existing group"""
        if group.id_grupo is None:
            raise ValueError("Cannot update group without ID")

        self.cursor.execute("""
            UPDATE grupo
            SET clave_grupo = %s, descripcion = %s, id_tipo_cliente = %s
            WHERE id_grupo = %s
        """, (group.clave_grupo, group.descripcion, group.id_tipo_cliente, group.id_grupo))

        self.conn.commit()

    def delete(self, group_id: int) -> None:
        """Delete group"""
        if group_id is None or group_id <= 0:
            raise ValueError("Invalid group ID")

        self.cursor.execute("DELETE FROM grupo WHERE id_grupo = %s", (group_id,))
        self.conn.commit()

    def is_in_use(self, group_id: int) -> tuple[bool, int]:
        """Check if group is used by clients, returns (in_use, count)"""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM cliente WHERE id_grupo = %s",
            (group_id,)
        )
        result = self.cursor.fetchone()
        count = result['count'] if result else 0
        return (count > 0, count)

    def _map_to_group(self, row: dict) -> Group:
        """Map database row to Group entity"""
        return Group(
            id_grupo=row['id_grupo'],
            clave_grupo=row['clave_grupo'],
            descripcion=row.get('descripcion'),
            id_tipo_cliente=row['id_tipo_cliente'],
            nombre_tipo=row.get('nombre_tipo'),
            descuento=row.get('descuento')
        )


class MySQLClientTypeRepository:
    """MySQL implementation of client type repository"""

    def __init__(self, connection):
        """Initialize with database connection"""
        if connection is None:
            raise ValueError("Database connection cannot be None")
        self.conn = connection
        self.cursor = connection.cursor()

    def get_by_id(self, type_id: int) -> Optional[ClientType]:
        """Get client type by ID"""
        if type_id is None or type_id <= 0:
            return None

        self.cursor.execute("""
            SELECT id_tipo_cliente, nombre_tipo, descuento
            FROM tipo_cliente
            WHERE id_tipo_cliente = %s
        """, (type_id,))

        row = self.cursor.fetchone()
        return self._map_to_client_type(row) if row else None

    def get_all(self) -> List[ClientType]:
        """Get all client types"""
        self.cursor.execute("""
            SELECT id_tipo_cliente, nombre_tipo, descuento
            FROM tipo_cliente
            ORDER BY nombre_tipo
        """)

        rows = self.cursor.fetchall()
        return [self._map_to_client_type(row) for row in rows]

    def create(self, client_type: ClientType) -> int:
        """Create a new client type, returns the new type ID"""
        self.cursor.execute(
            "INSERT INTO tipo_cliente (nombre_tipo, descuento) VALUES (%s, %s)",
            (client_type.nombre_tipo, client_type.descuento)
        )

        self.conn.commit()
        return self.cursor.lastrowid

    def update(self, client_type: ClientType) -> None:
        """Update existing client type"""
        if client_type.id_tipo_cliente is None:
            raise ValueError("Cannot update client type without ID")

        self.cursor.execute("""
            UPDATE tipo_cliente
            SET nombre_tipo = %s, descuento = %s
            WHERE id_tipo_cliente = %s
        """, (client_type.nombre_tipo, client_type.descuento, client_type.id_tipo_cliente))

        self.conn.commit()

    def delete(self, type_id: int) -> None:
        """Delete client type"""
        if type_id is None or type_id <= 0:
            raise ValueError("Invalid client type ID")

        self.cursor.execute(
            "DELETE FROM tipo_cliente WHERE id_tipo_cliente = %s",
            (type_id,)
        )
        self.conn.commit()

    def is_in_use(self, type_id: int) -> tuple[bool, int]:
        """Check if type is used by groups, returns (in_use, count)"""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM grupo WHERE id_tipo_cliente = %s",
            (type_id,)
        )
        result = self.cursor.fetchone()
        count = result['count'] if result else 0
        return (count > 0, count)

    def _map_to_client_type(self, row: dict) -> ClientType:
        """Map database row to ClientType entity"""
        return ClientType(
            id_tipo_cliente=row['id_tipo_cliente'],
            nombre_tipo=row['nombre_tipo'],
            descuento=row['descuento']
        )
