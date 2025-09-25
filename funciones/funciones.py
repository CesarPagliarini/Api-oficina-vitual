from utiles.conexion import engine
from sqlalchemy import text
from modelos.parametro.parametros import parametros, firmware
from utiles.config import DatosConexionInfluxRosario, DatosConexionInfluxSalta, DatosConexionInfluxSantiago, DatosConexionInfluxSanNicolas, DatosConexionMongoRosario, DatosConexionMongoSalta, DatosConexionMongoSantiago, DatosConexionMongoSanNicolas, DatosAcsRosario, DatosAcsSalta, DatosAcsSantiago, DatosAcsSanNicolas
from pysnmp.hlapi import *                                                                  # Funciones para las consultas SNMP
from datetime import datetime, timedelta
from pymongo import MongoClient, DESCENDING, ASCENDING
from typing import Optional
import requests, os, json, re, pytz, paramiko, time, base64, platform, subprocess


def canalesPosibles(red: str):
    if red == '2.4':
        canales = '1,2,3,4,5,6,7,8,9,10,11'
    elif red == '5.8':
        canales = '36,40,44,48,52,56,60,64,100,104,108,112,149,153,157,161'
    #print(canales)                                                                        # Debug
    return canales


def normalizarCanalesPosibles(canales, red):                                # Meti un cambio el 25/09, una Calix solo devolvia un entero en la variable canales
    if "-" in canales:
        partes = canales.split("-")
    else:
        partes = [canales, int(canales)+28]
    lista_canales = []
    if red == "2.4":
        salto = 1
    elif red == "5.8":
        salto = 4
    for i in range(int(partes[0]),int(partes[1])+1, salto):
        lista_canales.append(i)
    #print(lista_canales)                                                                 # Debug
    return ",".join(map(str, lista_canales))
    
def obtenerSerial(_id: str):
    serial = _id.split("-")[2]
    return serial

def normalizarSerial(serie: str):                   # QUEDA
    vendor = serie[:4]                                                                    # Separa la parte del Vendor
    serie_parcial = serie[4:]                                                             # Quita el vendor
    serie_normalizada = serie_parcial.lower()                                             # Pasa a minúscula las letras
    serial = vendor + serie_normalizada                                                   # Une ambas partes
    return vendor, serial

async def firmwareOlt(ip: str, comunidad: str, id_modelo: int):
    consulta = parametros.select().distinct().where(parametros.c.descripcion == 'Firmware version').where(parametros.c.id_modelo == id_modelo)
    respuestas = consultaMysql(consulta, "fetchall")
    for respuesta in respuestas:
        mib = respuesta[3]
        version_firmware = await consultaSnmp(mib, ip, comunidad)
        #print(f"La version de firmware es: {version_firmware}")                                                          # Debug
        if version_firmware != "Error en la consulta SNMP":
            consulta = firmware.select().where(firmware.c.firmware == version_firmware)
            respuestas = consultaMysql(consulta, "fetchone")
            if respuestas:
                id_firmware = respuestas[0]
                #print(f"id de firmare: {id_firmware}")                                                                   # Debug
                return int(id_firmware)                                                                                                   
                                                                                    
    return "No se logro obtener la version de firmware"
    
async def consultaSnmp(oid: str, ip: str, comunidad: str):                                # Ocurre la magia de la consulta SNMP
    #print(oid)                                                                           # Debug
    #print(ip)                                                                            # Debug
    #print(comunidad)                                                                     # Debug
    try:
        # Configurar la solicitud SNMP
        errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(
            SnmpEngine(),
            CommunityData(comunidad, mpModel=1),
            UdpTransportTarget((ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        ))
        #print(f"oid: {varBinds}")                                                        # Debug
        for res in varBinds:                                        
            valor = res[1]                                      
            #print(f"resultado de la consulta snmp: {valor}")                             # Debug
            return valor

    except Exception as e:
        return f"Error en la consulta SNMP"

      
    
def convertirTipoSnmp(valor):                                                      # Convierte un valor Python al tipo SNMP correspondiente.
    if isinstance(valor, int):
        return Integer(valor)
    elif isinstance(valor, str):
        return OctetString(valor)
    elif isinstance(valor, bytes):
        return OctetString(valor.decode('utf-8'))
    elif isinstance(valor, tuple) and len(valor) == 4:
        return IpAddress(".".join(map(str, valor)))                                # Maneja direcciones IP en formato de tupla (Ejemplo: (192, 168, 1, 1))
    else:
        raise ValueError(f"Tipo de dato {type(valor)} no soportado para SNMP SET.")
     
                                       
                        
def uptime(tiempo:str):
    formato=("%Y-%m-%d %H:%M:%S")
    try:
        fecha_referencia = datetime.strptime(tiempo, formato)
    except ValueError:
        return tiempo
    fecha_actual = datetime.now()
    diferencia =  fecha_actual - fecha_referencia
    
    # Convertir la diferencia a un formato legible
    dias = int(diferencia.days)                                                         # Extrae la cantidad de días (solo los días)
    segundos_restantes = int(diferencia.seconds)                                        # Extrae los segundos sobrantes
    horas, segundos_restantes = divmod(segundos_restantes, 3600)                        # Convierte en Horas y guarda los segundos sobrantes
    minutos, segundos = divmod(segundos_restantes, 60)                                  # Convierte en minutos y guarda los segundos sobrantes
    return f"{dias} days, {horas}:{minutos:02d}:{segundos:02d}"


def baseDeDatos(operacion: str, db: str):               # QUEDA
    if operacion == 'rosario':
        if db == 'influx':
            return DatosConexionInfluxRosario
        elif db == 'mongo':
            return DatosConexionMongoRosario
        elif db == 'acs':
            return DatosAcsRosario
    elif operacion == 'salta':
        if db == 'influx':
            return DatosConexionInfluxSalta
        elif db == 'mongo':
            return DatosConexionMongoSalta
        elif db == 'acs':
            return DatosAcsSalta
    elif operacion == 'santiago':
        if db == 'influx':
            return DatosConexionInfluxSantiago
        elif db == 'mongo':
            return DatosConexionMongoSantiago
        elif db == 'acs':
            return DatosAcsSantiago
    elif operacion == 'san nicolas':
        if db == 'influx':
            return DatosConexionInfluxSanNicolas
        elif db == 'mongo':
            return DatosConexionMongoSanNicolas
        elif db == 'acs':
            return DatosAcsSanNicolas
   
   
def estado(status):                     # QUEDA
    if status == 'UP':
        return "online"
    elif status == 'enable':
        return "online"
    elif status == 'enabled':
        return "online"
    elif status == 'DOWN':
        return "offline"
    else:
        return status
    

def placaPuertoId(interfaz:str):
        partes = interfaz.split('/')
        placaPuerto = partes[0] + "/" + partes[1]
        id = partes[2] if len(partes) > 2 else ' '
        return placaPuerto, id
    
    
def nombreOlt(olt: str):
        resultado = olt
        partes = olt.split("-")
        if len(partes) > 2:
            resultado = "-".join(partes[1:])
            #print(resultado)
        return resultado    
    

def normalizarNroSuscriptor(id_localidad: str, nro_suscriptor: str):
    ceros_a_agregar = 7 - (len(id_localidad) + len(nro_suscriptor))
    if ceros_a_agregar > 0:
        id_cliente = f"{id_localidad}{'0' * ceros_a_agregar}{nro_suscriptor}"
    else:
        id_cliente = f"{id_localidad}{nro_suscriptor}"
    return id_cliente


def definirLocalidad(conexion: int):
    if len(str(conexion)) == 7:
        id_localidad = int(str(conexion)[0])
        if id_localidad == 1:
            return "Rosario"
        elif id_localidad == 2:
            return "Salta"
        elif id_localidad == 3:
            return "Santiago del Estero"
        elif id_localidad == 4:
            return "San Nicolas"
    else:
        return "Localidad incorrecta"


###################### SECCION MYSQL DB ###############################

def consultaMysql(consulta, fetch: str):                            # QUEDA
    with engine.connect() as conn:                                                        # El entorno with se asegura de cerrar la conexión una vez finalizada la operación
        respuestas = conn.execute(consulta)
        conn.commit() 
    if respuestas.rowcount > 0:
        if fetch == "fetchall":
            return respuestas.fetchall()
        elif fetch == "fetchone":
            return respuestas.fetchone()
        elif fetch == "first":
            return respuestas.first()
        elif fetch == "simple":
            return respuestas
        
def limites():
    query = text("""SELECT * FROM `limites`""" )
    respuesta = consultaMysql(query, 'fetchall')     
    if respuesta:
        diccionario = {result[2]: result[1] for result in respuesta}                    # Campo 2 como clave, campo 1 como valor
        return diccionario
    else:
        #print("No se encontraron resultados en la base de datos")
        return {}
    
def parametroDb(id_firmware: int, id_modelo: int, descripcion: str):       # QUEDA                                # Devuelve el parametro (dataModel) solicitado
    #print(id_firmware, id_modelo,descripcion)
    consulta = parametros.select().where((parametros.c.id_firmware == id_firmware)&(parametros.c.id_modelo == id_modelo)&(parametros.c.descripcion == descripcion))
    #print(consulta)
    resultado = consultaMysql(consulta, 'first')
    #print(f"Resultado: " + resultado)
    if resultado:
        #print(resultado[3])                                                                                                            # Debug
        return resultado[3], resultado[5]
    else:
        #print("Salio por el no")
        return "No existe el parametro requerido"
    
        
