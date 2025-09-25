from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
#from modelos.dispositivo.dispositivos import tipo_dispositivos
from modelos.dispositivo.marcas import modelos
from modelos.localidad.localidades import hubs
from utiles.conexion import meta_data

bases_de_datos = Table("bases_de_datos", meta_data,
                Column("id_db", Integer, primary_key=True, autoincrement=True),
                Column("db", String(25), nullable=False))          # Estructura de la tabla Base de datos
