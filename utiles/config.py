import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class DatosConexion:
    DB_HOST:str = os.getenv('DB_HOST') 
    DB_USUARIO:str = os.getenv('DB_USUARIO')
    DB_PASSWORD:str = os.getenv('DB_PASSWORD')
    DB_PUERTO:str = os.getenv('DB_PUERTO')
    DB_NAME:str = os.getenv('DB_NAME')
    DB_URL= f"mysql+pymysql://{DB_USUARIO}:{DB_PASSWORD}@{DB_HOST}:{DB_PUERTO}/{DB_NAME}"
    #DB_URL = f"mysql+pymysql://scriptUpgraded:n0cTeled1f_@192.168.200.206:3306/automatic_upgraded"     # Debug

    # Debug

    #print(os.getenv('DB_HOST'))
    #print(os.getenv('DB_USUARIO'))
    #print(os.getenv('DB_PASSWORD'))
    #print(os.getenv('DB_PUERTO'))
    #print(os.getenv('DB_NAME'))


# Influx
    
class DatosConexionInfluxRosario:
    DB_HOST:str = os.getenv('DB_HOST_ROSARIO') 
    DB_TOKEN:str = os.getenv('DB_TOKEN_ROSARIO')
    DB_ORGANIZACION:str = os.getenv('DB_ORGANIZACION_ROSARIO')
    DB_PUERTO:str = os.getenv('DB_PUERTO_ROSARIO')
    DB_NAME:str = os.getenv('DB_NAME_ROSARIO')
    DB_URL:str = DB_HOST + ":" + DB_PUERTO
        
class DatosConexionInfluxSalta:
    DB_HOST:str = os.getenv('DB_HOST_SALTA') 
    DB_TOKEN:str = os.getenv('DB_TOKEN_SALTA')
    DB_ORGANIZACION:str = os.getenv('DB_ORGANIZACION_SALTA')
    DB_PUERTO:str = os.getenv('DB_PUERTO_SALTA')
    DB_NAME:str = os.getenv('DB_NAME_SALTA')
    DB_URL:str = DB_HOST + ":" + DB_PUERTO
    
class DatosConexionInfluxSantiago:
    DB_HOST:str = os.getenv('DB_HOST_SANTIAGO') 
    DB_TOKEN:str = os.getenv('DB_TOKEN_SANTIAGO')
    DB_ORGANIZACION:str = os.getenv('DB_ORGANIZACION_SANTIAGO')
    DB_PUERTO:str = os.getenv('DB_PUERTO_SANTIAGO')
    DB_NAME:str = os.getenv('DB_NAME_SANTIAGO')
    DB_URL:str = DB_HOST + ":" + DB_PUERTO

class DatosConexionInfluxSanNicolas:
    DB_HOST:str = os.getenv('DB_HOST_SAN-NICOLAS') 
    DB_TOKEN:str = os.getenv('DB_TOKEN_SAN-NICOLAS')
    DB_ORGANIZACION:str = os.getenv('DB_ORGANIZACION_SAN-NICOLAS')
    DB_PUERTO:str = os.getenv('DB_PUERTO_SAN-NICOLAS')
    DB_NAME:str = os.getenv('DB_NAME_SAN-NICOLAS')
    DB_URL:str = DB_HOST + ":" + DB_PUERTO
    
# Mongo

class DatosConexionMongoRosario:
    pass
    
class DatosConexionMongoSalta:
    pass
    
class DatosConexionMongoSantiago:
    pass

class DatosConexionMongoSanNicolas:
    pass
    
# ACS

class DatosAcsRosario:
    IP_HOST:str = os.getenv('IP_ACS_ROSARIO') 
    
class DatosAcsSalta:
    IP_HOST:str = os.getenv('IP_ACS_SALTA') 

class DatosAcsSantiago:
    IP_HOST:str = os.getenv('IP_ACS_SANTIAGO') 
    
class DatosAcsSanNicolas:
    IP_HOST:str = os.getenv('IP_ACS_SAN_NICOLAS') 
