from sqlalchemy import Table, Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Integer, String
from utiles.conexion import meta_data

localidades = Table("localidades", meta_data,
                    Column("id_localidad", Integer, primary_key=True, autoincrement=True),
                    Column("localidad", String(25), nullable=False))       # Estructura de la tabla Localidades

ciudades = Table("ciudades", meta_data,
                    Column("id_ciudad", Integer, primary_key=True, autoincrement=True),
                    Column("id_localidad", ForeignKey("localidades.id_localidad"), nullable=False),
                    Column("ciudad", String(25), nullable=False),
                    Column("id_ciudad_siga", Integer, nullable=False))       # Estructura de la tabla ciudades

hubs = Table("hubs", meta_data,
                    Column("id_hub", Integer, primary_key=True, autoincrement=True),
                    Column("id_localidad", ForeignKey("localidades.id_localidad"), nullable=False),
                    Column("hub", String(25), nullable=False))       # Estructura de la tabla hubs

#meta_data.create_all(engine)                                 # Crea las tablas