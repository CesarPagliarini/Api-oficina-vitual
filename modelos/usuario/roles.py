from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from utiles.conexion import meta_data, engine


roles = Table("roles", meta_data,
                 Column("id_rol", Integer, primary_key=True, autoincrement=True),
                 Column("rol", String(25), nullable=False))          # Estructura de la tabla Roles


#meta_data.create_all(engine)                                 # Crea las tablas