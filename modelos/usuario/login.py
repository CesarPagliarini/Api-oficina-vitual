from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, DateTime, String
from utiles.conexion import meta_data
from datetime import datetime

estado_sesiones = Table("estado_sesiones", meta_data,
                        Column("id_estado", Integer, primary_key=True, autoincrement=True),
                        Column("estado", String(10), nullable=False))

sesiones = Table("sesiones", meta_data,
                 Column("id_sesion", Integer, primary_key=True, autoincrement=True),
                 Column("id_dispositivo", String(50), nullable=False),
                 Column("id_usuario", ForeignKey("usuarios.id_usuario"), nullable=False),
                 Column("id_estado", ForeignKey("estado_sesiones.id_estado"), nullable=False),
                 Column("fecha_login", DateTime(), default=datetime.now, nullable=False))

#meta_data.create_all(engine)                                 # Crea las tablas
