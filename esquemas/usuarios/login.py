from pydantic import BaseModel
from typing import Optional
import os
from jwt import encode, decode, exceptions
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

#env_path = Path('.') / '.env'
#load_dotenv(dotenv_path=env_path)

class DataUser(BaseModel):
    
    # Atributos  
    id_usuario: Optional[int] = 0
    username: str = " "
    password: str = " "
    id_dispositivo: str = " "
    
    # Metodos
    def __init__(self, **datos):
        super().__init__(**datos)
    
    def token_expiracion(self, horas: int):
        fecha = datetime.now()
        fecha_expiracion = fecha + timedelta(hours=horas)
        #print(fecha)
        return fecha_expiracion

    def datos_sesion(self, usuario: str, consulta: str):
        datos = dict(usuario)
        datos.pop('password')
        datos.pop('username')
        datos['id_usuario'] = consulta[0]
        datos['id_estado'] = 1
        #print(datos)
        return datos

    def crear_token(self, sesion: str, resultado: str, logout = False):
        #clave = self.generar_clave()
        datos = dict(
            id_sesion = sesion[0],
            id_dispositivo = sesion[1],
            id_usuario = sesion[2],
            username = resultado[7], 
            id_modo_frontend = resultado[11],
            modo_frontend = resultado[12],
            logout = logout
            )
        token = encode(payload={**datos, "exp": self.token_expiracion(int(os.getenv('EXPIRATION_TOKEN')))}, key=os.getenv('KEY_TOKEN'), algorithm="HS256")
        return token 

    def validar_token(self,token, salida = False):
        try:
            if salida:
                salida = decode(token, key=os.getenv('KEY_TOKEN'), algorithms="HS256")
                return salida
            respuesta = decode(token, key=os.getenv('KEY_TOKEN'), algorithms="HS256")
            #print(f"decode: {respuesta['logout']}")
            return respuesta['logout']                                                    #Devuelve True o False
        except exceptions.DecodeError:
            return JSONResponse(content={"message": "Token invalido"}, status_code=401)
        except exceptions.ExpiredSignatureError:
            return JSONResponse(content={"message": "Token expirado"}, status_code=401)






