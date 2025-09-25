import os
from fastapi import Request, HTTPException
from sqlalchemy import join
from modelos.usuario.usuarios import usuarios, usuario_roles
from utiles.conexion import engine
from jwt import decode
        

def verificacionRol(ruta: str = None):
    async def verificarTipoCliente(request: Request):
        username = getUsername(request)
        with engine.connect() as conn:                 
            usuario = conn.execute(
                join(usuarios, usuario_roles, usuarios.c.id_usuario == usuario_roles.c.id_usuario)
                .select().where(usuarios.c.username == username)
            ).fetchall()
        if usuario:
            ultimo_valor = usuario[0][12]               # Obtiene el dato de id_rol
            if (ruta == 'externa' and ultimo_valor == 1) or (ruta is None and ultimo_valor != 1):             # Verificación de la ruta y rol
                return
            else:
                raise HTTPException(status_code=403, detail="Acceso denegado")
        else:
            raise HTTPException(status_code=404, detail="No existe el usuario")
    return verificarTipoCliente


def getUsername(request: Request):
    token = request.headers["Authorization"].split(" ")[1]
    salida = decode(token, key=os.getenv('KEY_TOKEN'), algorithms="HS256")
    username = salida['username']
    return username

   