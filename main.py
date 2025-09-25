import os, uvicorn, socket, ssl
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI
#from fastapi.routing import APIRoute, APIWebSocketRoute
from fastapi.middleware.cors import CORSMiddleware
from rutas.usuarios import login
from rutas.dispositivos import onu



env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
load_dotenv(override=True)

app = FastAPI()                          

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)                                           # Evita que el frontend dé problemas por enviar un post con Body


 
# Se agregan las rutas
app.include_router(login.rutasLogIn)                       
app.include_router(login.rutasLogOut)                    
app.include_router(onu.rutasOnu)                         



@app.get("/")
async def root():
    return "El servidor funciona"

# Configura el contexto SSL
certificado = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
certificado.load_cert_chain("./certificados/all_in_one.crt", keyfile="./certificados/privatekey.key")

if __name__ == "__main__":
    hostname = socket.gethostname()                                                                         # Obtiene el hostname
    ip_address = socket.gethostbyname(hostname)                                                             # Obtiene la ip asociada al hostname
    uvicorn.run("main:app", 
                host=ip_address, 
                port=int(os.getenv('PUERTO')),
                #ssl_keyfile="./certificados/privatekey.key",
                #ssl_certfile="./certificados/all_in_one.crt",
                workers=4, 
                reload=True)


