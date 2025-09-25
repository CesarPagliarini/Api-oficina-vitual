from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
#from funciones.usuarios.login import validar_token
from esquemas.usuarios.login import DataUser


class VerifyTokenRoute(APIRoute):
    def get_route_handler(self):
        ruta_original = super().get_route_handler()
        async def verificar_token_middleware(request:Request, data_user = DataUser()):
            #data_user = DataUser()
            token = request.headers["Authorization"].split(" ")[1]
            respuesta = data_user.validar_token(token, salida=False)
            if respuesta == False:                              # Verifica si el token es exclusivo de LogOut
                return await ruta_original(request)
            elif (respuesta == True):
                #print(f"Respuesta: {request.url.split('/')[3]}")        # Debug
                if str(request.url).split('/')[3] == "logout":
                    return await ruta_original(request)
                else:
                    return JSONResponse(content={"message": "Token solo util para Logout"}, status_code=401)
            else:
                return respuesta                                #Si la función da error por expiración o token incorrecto, muestra el error

        return verificar_token_middleware
    
 
