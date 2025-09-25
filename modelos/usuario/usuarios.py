from sqlalchemy import Table, Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Integer, String, DateTime
from utiles.conexion import meta_data, engine
from datetime import datetime
from modelos.usuario.roles import roles
from modelos.localidad.localidades import localidades
from modelos.usuario.login import sesiones

#estado_usuarios = Table("estado_usuarios", meta_data,
#                       Column("id_estado", Integer, primary_key=True),
#                       Column("estado", String(10), nullable=False))

modo_frontends = Table("modo_frontends", meta_data,
                      Column("id_modo_frontend", Integer, primary_key=True),
                      Column("modo_frontend", String(15), nullable=False))

usuarios = Table("usuarios", meta_data,                                                                              # Estructura de la tabla Usuarios
                 Column("id_usuario", Integer, primary_key=True, autoincrement=True),
                 Column("id_localidad", ForeignKey("localidades.id_localidad"), nullable=False),
                 Column("id_estado", ForeignKey("estado_usuarios.id_estado"), nullable=False),
                 Column("id_modo_frontend", ForeignKey("modo_frontends.id_modo_frontend"), nullable=False),
                 Column("nombre", String(25), nullable=False),
                 Column("apellido", String(25), nullable=False),
                 Column("email", String(50), nullable=True), 
                 Column("username", String(25), nullable=False, unique=True),
                 Column("password", String(255), nullable=False),
                 Column("creado", DateTime(), default=datetime.now, nullable=False),
                 Column("modificado", DateTime(), onupdate=datetime.now))   

usuario_roles = Table("usuarios_roles", meta_data,                                                                          
                     Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE", onupdate="CASCADE"), nullable=False),
                     Column("id_rol", Integer, ForeignKey("roles.id_rol", ondelete="CASCADE", onupdate="CASCADE"), nullable=False),
                     PrimaryKeyConstraint("id_usuario", "id_rol"))   

usuario_localidades = Table("usuarios_localidades", meta_data,                                                                          
                           Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE", onupdate="CASCADE"), nullable=False),
                           Column("id_localidad", Integer, ForeignKey("localidades.id_localidad", ondelete="CASCADE", onupdate="CASCADE"), nullable=False),
                           PrimaryKeyConstraint("id_usuario", "id_localidad"))                                   


#meta_data.create_all(engine)                                 # Crea las tablas



