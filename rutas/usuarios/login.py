from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy import join
from utiles.conexion import engine
from esquemas.usuarios.login import DataUser
from modelos.usuario.usuarios import usuarios, modo_frontends
from modelos.usuario.login import sesiones
from werkzeug.security import check_password_hash                    # Sirve para la encriptación de las password
from middlewares.acceso_token_rutas import VerifyTokenRoute

rutasLogIn = APIRouter(prefix="/login")
rutasLogOut = APIRouter(route_class=VerifyTokenRoute, prefix="/logout")
#rutasLogOut = APIRouter(prefix="/logout")

@rutasLogIn.post("/")
async def login(request: Request):
    datos = await request.json()
    data_user = DataUser(**datos)
    #print(data_user.username)                                                                                                           # Debug
    token = JSONResponse(content={"message": "Credenciales invalidas"}, status_code=401)
    with engine.connect() as conn:
        resultado = conn.execute(join(usuarios, modo_frontends).select().where(usuarios.c.username == data_user.username)).first()       # Verifica si el usuario existe
        #return resultado[0]                                                                                                             # Debug
        if resultado:
            check_password = check_password_hash(resultado[8],data_user.password)                                                        # Verifica la password
            if resultado != None and check_password is True:
                if resultado[2] == 2:                                                                                                    # Verifica si el usuario esta inhabilitado
                    token = JSONResponse(content={"message": "Usuario inhabilitado para operar"}, status_code=403)
                else:
                    #with engine.connect() as conn:
                    id_usuario = resultado[0]
                    sesion = conn.execute(sesiones.select().where(sesiones.c.id_usuario == id_usuario).where(sesiones.c.id_estado == 1)).first()
                    #print(sesion.count)
                    if not sesion:
                        datos = data_user.datos_sesion(data_user, resultado)
                        #with engine.connect() as conn:
                        alta = conn.execute(sesiones.insert().values(datos))
                        conn.commit()
                        ultima_sesion = conn.execute(sesiones.select().where(sesiones.c.id_usuario == datos['id_usuario']).order_by(sesiones.c.id_sesion.desc())).first()              
                        token = data_user.crear_token(ultima_sesion, resultado, logout=False)
                    else:
                        token = data_user.crear_token(sesion, resultado, logout=True)
                        return JSONResponse(content={
                            "message": "Posee sesiones iniciadas",
                            "token": token 
                            }, status_code=401)
    return token

@rutasLogOut.put("/")
def logout(Authorization: str = Header(None), data_user = DataUser()):
    token = Authorization.split(" ")[1]                         # Obtiene el valor del campo Authorization de la cabecera
    info = data_user.validar_token(token, salida=True)
    mensaje = JSONResponse(content={"message": "No se pudo realizar el logout"}, status_code=400)
    with engine.connect() as conn:
        respuesta = conn.execute(sesiones.update().values(id_estado=2).where(sesiones.c.id_sesion == info['id_sesion']))
        conn.commit()
        #print(respuesta.rowcount) # Da como resultado la cantidad de lineas que machearon con las condiciones del where. SI da 0, no existe ninguna
    if respuesta.rowcount !=0:
        mensaje = JSONResponse(content={"message": "Logout exitoso"}, status_code=200)
    return mensaje


