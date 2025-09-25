from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Boolean
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from modelos.dispositivo.dispositivos import tipo_dispositivos, modos_operacion
#from modelos.dispositivo.terminales import estado_terminales
from utiles.conexion import meta_data

marcas = Table("marcas", meta_data,
                Column("id_marca", Integer, primary_key=True, autoincrement=True),
                Column("marca", String(25), nullable=False))       # Estructura de la tabla Marcas

modelos = Table("modelos", meta_data,
                Column("id_modelo", Integer, primary_key=True, autoincrement=True),
                Column("id_marca", ForeignKey("marcas.id_marca"), nullable=False),
                Column("id_tipo_dispositivo", ForeignKey("tipo_dispositivos.id_tipo_dispositivo"), nullable=False),
                Column("id_modo", ForeignKey("modos_operacion.id_modo"), nullable=True),                            # Reservado para los dispositivos de tipo dispositivo (ONU o CM)
                Column("modelo", String(25), nullable=False),
                Column("cant_puertos_eth", Integer, nullable=True),
                Column("cant_puertos_telefonia", Integer, nullable=True),
                Column("rf", Boolean, nullable=True),
                Column("wifi24", Boolean, nullable=True),
                Column("wifi58", Boolean, nullable=True),
                #Column("wifi6", Boolean, nullable=True),
                Column("imagen_frontal", MEDIUMTEXT, nullable=True),
                Column("imagen_trasera", MEDIUMTEXT, nullable=True))