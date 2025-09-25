from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from modelos.dispositivo.marcas import modelos
from utiles.conexion import meta_data

firmware = Table("firmware", meta_data,
                Column("id_firmware", Integer, primary_key=True, autoincrement=True),
                Column("firmware", String(20), nullable=False))       # Estructura de la tabla Firmwares

parametros = Table("parametros", meta_data,
                Column("id_parametro", Integer, primary_key=True, autoincrement=True),
                Column("id_modelo", ForeignKey("modelos.id_modelo"), nullable=False),
                Column("id_firmware", ForeignKey("firmware.id_firmware"), nullable=False),
                Column("parametro", String(255), nullable=False),
                Column("descripcion", String(25), nullable=True),
                Column("tipo_dato", String(15), default=None ,nullable=True))       # Estructura de la tabla parametros

