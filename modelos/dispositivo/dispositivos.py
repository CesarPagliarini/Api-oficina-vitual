from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, DateTime
from datetime import datetime
#from modelos.dispositivo.marcas import modelos
from utiles.conexion import meta_data

tipo_dispositivos = Table("tipo_dispositivos", meta_data,
                    Column("id_tipo_dispositivo", Integer, primary_key=True, autoincrement=True),
                    Column("tipo_dispositivo", String(20), nullable=False))  # Estructura de la tabla tipo de dispositivos

modos_operacion = Table("modos_operacion", meta_data,
                    Column("id_modo", Integer, primary_key=True, autoincrement=True),
                    Column("modo", String(25), nullable=False))        # Estructura de la tabla Modos de operacion    



