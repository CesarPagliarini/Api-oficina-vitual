import os, time, asyncio, re, ipaddress
import lxml.etree as ET
import requests, json
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from funciones.funciones import *
from modelos.dispositivo.terminales import bases_de_datos
from typing import Optional
from requests.auth import HTTPBasicAuth                                                     # Función para autenticar contra la API de FDM

  
class Onu(BaseModel):
    
    # Atributos  
    id_sesion: int = 0
    serial: str = " "
    ont_id: int = 0
    olt: str = " "
    
    
    # Metodos
    
    def nombreDb(self, id_localidad: int):                                                          # QUEDA
        consulta = bases_de_datos.select().where(bases_de_datos.c.id_db == id_localidad)
        respuesta = consultaMysql(consulta, 'simple')
        if respuesta.rowcount > 0:
            auxiliar = respuesta.fetchone()
            localidad = auxiliar[1]
            return baseDeDatos(localidad, 'acs')
    
    def normalizarId(self, id_temporal: str):                   # QUEDA
        return id_temporal
            
    def datosACS(self, id_localidad: int, serial: str, parametro1: str, parametro2: str, vendor: str, modificador_serial: str = "si"):          # QUEDA
        datos_db = self.nombreDb(id_localidad)
        #print(datos_db.IP_HOST)
        url_a = f"http://{datos_db.IP_HOST}/devices/?query="
        url_b = '"_deviceId._SerialNumber"'
        url_c = '&projection='
        #print(url_a, url_b, url_c)
        if modificador_serial == "si":
            serial = serial.upper()
        url = url_a + '{' + url_b + ':' + ' ' + '"' + serial + '"' + '}' + url_c + parametro1 + ',' + parametro2
        #print(url)
        response = requests.get(url, data=None, headers=None)
        #print(f"Url {url}")                                        # Debug
        resultado = dict()
        resultado['id'] = ""
        resultado['equipo'] = {}                                    # Inicializa la clave 'equipo' como un diccionario vacío
        resultado['valores'] = {}                                   # Inicializa la clave 'valores' como un diccionario vacío
        #print(response.status_code)                                # Debug
        #print(response.text)                                       # Debug
        if response.status_code == 200 and response.text != "[\n\n]":
            if vendor == "KAON":
                firmware = response.json()[0]["Device"]["DeviceInfo"]["SoftwareVersion"]["_value"]
                modelo = response.json()[0]["Device"]["DeviceInfo"]["ModelName"]["_value"]
            #print(response.json())                                 # Debug
            elif vendor == "CXNK" or vendor == "CIGG":
                firmware = response.json()[0]["InternetGatewayDevice"]["DeviceInfo"]["SoftwareVersion"]["_value"]
                try: 
                    modelo = response.json()[0]["InternetGatewayDevice"]["DeviceInfo"]["ModelName"]["_value"]
                except KeyError:
                    modelo = None
            else:
                firmware = response.json()[0]["InternetGatewayDevice"]["DeviceInfo"]["SoftwareVersion"]["_value"]
                modelo = response.json()[0]["_deviceId"]["_ProductClass"]
            id_temporal = response.json()[0]["_id"]
            #resultado['id'] = id_temporal.replace("%", "%25").replace("%252D", "%2D") 
            resultado['id'] = self.normalizarId(id_temporal)     
            #resultado['id'] = response.json()[0]["_id"]                # Debug
            resultado['equipo']['firmware'] = firmware
            resultado['equipo']['modelo'] = modelo
            #print(resultado)                                           # Debug
            return resultado, response.status_code
        elif response.status_code == 200 and response.text == "[\n\n]":
            #print(response.text)                                       # Debug
            #print("salio por el elif")                                 # Debug
            status_code = 400
            return resultado, status_code
        else:
            return "Fallo la comunicación con el ACS", response.status_code
    
    
    def login(self):
        url = f"http://{str(os.getenv('IP_CMS'))}/cmsexc/ex/netconf"
        headers = {'Content-Type': 'text/plain; charset=utf-8'}
        data = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <auth message-id="1">
                <login>
                    <UserName>{str(os.getenv('CMS_USUARIO'))}</UserName>
                    <Password>{str(os.getenv('CMS_PASSWORD'))}</Password>
                </login>
                </auth>
            </soapenv:Body>
            </soapenv:Envelope>
            """
        respuesta = requests.post(url, data=data, headers=headers)
        #print(f"codigo: {respuesta.status_code}")                              # Debug
        if respuesta.status_code == 200:
            xml = respuesta.text
            root = ET.fromstring(xml)
            elements = root[1][0]
            for row in elements.findall('SessionId') :
                #print(row.text)                                                # Debug
                return (row.text, respuesta.status_code)                        # Devuelve el session id asignado por el CMS
        else:
            return "No se pudo ejecutar la transaccion", respuesta.status_code
           
            
    def logout(self, id_sesion):                          # Recibe como variable el id de sesion obtenido de la funcion Login. Si o Si debe ser asyncrono
        url = f"http://{str(os.getenv('IP_CMS'))}/cmsexc/ex/netconf"
        headers = {'Content-Type': 'text/plain; charset=utf-8'}
        data = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                <soapenv:Body>
                    <auth message-id="2">
                        <logout>
                            <UserName>{str(os.getenv('CMS_USUARIO'))}</UserName>
                            <SessionId>{id_sesion}</SessionId>
                        </logout>
                    </auth>
                </soapenv:Body>
            </soapenv:Envelope>
            """
        respuesta = requests.post(url, data=data, headers=headers)
        if respuesta.status_code == 200:
            return "Logout exitoso", respuesta.status_code
        else:
            return "No se completo el Logout", respuesta.status_code 
    
    def unlink(self, serie: str, olt: str, ont_id: int):                                                                        # Modifica el valor del campo "roaming" a "restricted"                        
        url_a = f"http://{str(os.getenv('IP_FDM'))}/fdm/api/v0.2/devices/ont/"
        url = url_a + serie
        auth = HTTPBasicAuth(str(os.getenv('FDM_USUARIO')), str(os.getenv('FDM_PASSWORD')))
        #print(url)                                                                                                            # Debug
        body = {
            "roaming": "restricted"
        }
        json_body = json.dumps(body)
        response = requests.put(url, auth=auth, data=json_body, headers={'Content-Type': 'application/json'})
        #print(response.status_code)                                                                                           # Debug
        #print(response.json())                                                                                                # Debug
        return "Unlink aplicado con exito", response.status_code
                
       
    def getInfoAcs(self, id_localidad: int, serial:str, parametro:str):                     # QUEDA
        datos_db = self.nombreDb(id_localidad)
        url_a = f"http://{datos_db.IP_HOST}/devices/?query="
        url_b = '"_deviceId._SerialNumber"'
        url_c = '&projection='
        url = url_a + '{' + url_b + ':' + ' ' + '"' + serial + '"' + '}' + url_c + parametro
        #print(f"Url: {url}")
        response = requests.get(url, data=None, headers=None)
        if response.status_code == 200 and response.text != "[\n\n]":
            parametros_aux = parametro.split(".")
            parametros_format = "".join(f"['{param}']" for param in parametros_aux)
            if parametro == "_id" or parametro == "_deviceId":
                parametros_format += ""
            elif parametro in {"_lastBootstrap", "_lastInform", "_registered", "_lastBoot"}:                                    # Para Eventos, queda separado de la linea anterior para evitar confusiones su hubiese que agregar mas condiciones.
                parametros_format += ""
            else:
                parametros_format += "['_value']"
            auxiliar = response.json()[0]
            #print(f"Auxiliar: {auxiliar}")
            respuesta = eval("auxiliar" + parametros_format)
            #print(f"Respuesta: {respuesta}")                                                                                                               # Debug 
            return respuesta, response.status_code
        else:
            return JSONResponse(content={"message": "El dispositivo no se encontró"}, status_code=404)               

    def setInfoAcs(self, id_localidad: int, _id:str, parametro:str, info:str, tipo_dato:str):        # QUEDA
        parametro = parametro.replace(".X_000631_", ".")
        datos_db = self.nombreDb(id_localidad)
        url_a = f"http://{datos_db.IP_HOST}/devices/"
        url_b = '/tasks?timeout=3000&connection_request'
        url = url_a + _id + url_b
        #print(f"Url: {url}")                                                                                                                         # Debug                        
        body = {
            "name": "setParameterValues",
            "parameterValues":
                [
                    [parametro, info, f"xsd:{tipo_dato}"]
                    #["InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.PreSharedKey.1.KeyPassphrase", info, "xsd:string"]             # Debug
                ]             
        }
        response = requests.post(url, json=body)
        if (response.status_code == 200 or response.status_code == 202) and response.text != "[\n\n]":
            #print(f"{parametro}:{response.text}")                                                                                          # Debug 
            #print(response.status_code)                                                                                                    # Debug 
            return response.status_code
        else:
            #print(response.status_code)                                                                                                    # Debug 
            return JSONResponse(content={"message": "El dispositivo no se encontró"}, status_code=404)
    
                                    
    def getInfo(self, id_localidad: int, id_firmware: int, id_modelo:int, nro_serial:str, descripcion: str, buscar: str = 'si'):        # QUEDA
        parametro, tipo_dato = parametroDb(id_firmware, id_modelo, descripcion)
        #print(f"Parametro: {parametro}, Nro de serie: {nro_serial}")                                                                       # Debug
        if buscar == 'no':
            return parametro, 200
        dato , dato_status_code= self.getInfoAcs(id_localidad, nro_serial, parametro)
        #print(dato)                                                                                                                        # Debug
        return str(dato), dato_status_code
    
    
    def setInfo(self, id_localidad: int, id_firmware: int, id_modelo:int, descripcion: str, _id:str, info:str):
        parametro, tipo_dato = parametroDb(id_firmware, id_modelo, descripcion)
        #print(f"Parametro: {parametro}, _id: {_id}")                                                                       # Debug
        dato = self.setInfoAcs(id_localidad, _id, parametro, info, tipo_dato)
        #print(dato)                                                                                                                        # Debug
        return str(dato)
      
    
    def accionesOnuAcs(self, id_localidad: int, _id:str, accion:str ,parametro: Optional[str] = None, ont_id: Optional[int] = None, olt: Optional[str] = None):
        datos_db = self.nombreDb(id_localidad)
        url_a = f"http://{datos_db.IP_HOST}/devices/"
        url_b = '/tasks?timeout=3000&connection_request'
        url = url_a + _id + url_b
        #print(f"Url: {url}")                                                                                                               # Debug                          
        #print(f"Parametro: {parametro}")                                                                                                   # Debug
        body = {
            "name": accion,
            "objectName": parametro      
        }
        response = requests.post(url, json=body)
        #print(response.json())                                                                                                             # Debug
        #print(f"Status_code: {response.status_code}")                                                                                      # Debug
        if response.status_code == 200 and response.text != "[\n\n]":
            return response.status_code
        else:
            return JSONResponse(content={"message": "El dispositivo no se encontró"}, status_code=404)
         
    
    def rebootFactory(self, id_localidad: int, _id:str, accion:str ,parametro: Optional[str] = None, ont_id: Optional[int] = None, olt: Optional[str] = None):
        status_code = self.accionesOnuAcs(id_localidad, _id, accion,parametro, ont_id, olt)
        return status_code == 200
    
    def accionesOnu(self, id_localidad: int, _id:str, id_firmware: int, id_modelo:int, descripcion:str, accion:str):
        parametro, tipo_dato = parametroDb(id_firmware, id_modelo, descripcion)
        #print(parametro)
        resultado = self.accionesOnuAcs(id_localidad, _id, accion, parametro)
        #print(resultado)
        if resultado == 200:
            return JSONResponse(content={"message": "Refresh aplicado correctamente"}, status_code=200)
        else:
            return resultado

         
                 
class CalixDevice(Onu):
    # Atributos
    tipo = "Calix"
    
    # Metodos
    def datos(self, serial: str, id_localidad: int):                    # QUEDA
        vendor = serial[:4]
        modelo = "InternetGatewayDevice.DeviceInfo.ModelName._value"
        firmware = "InternetGatewayDevice.DeviceInfo.SoftwareVersion._value"
        return self.datosACS(id_localidad, serial, modelo, firmware, vendor)
    
    def rebootFactory(self, id_localidad: int, _id: str, accion: str ,parametro: Optional[str] = None, ont_id: Optional[int] = None, olt: Optional[str] = None):                       
        login_salida, login_status_code = self.login()
        #print(f"Id_sesion: {respuesta}")                                                        # Debug
        #print(f"Status code: {login_status_code}")                                              # Debug
        if login_status_code == 200:
            #print(f"Serial recortado {serial}")                                                 # Debug
            if accion == 'reboot':
                tipo_accion = 'force'
            elif accion == 'factoryReset':
                tipo_accion = 'rg-reset'
            salida, status_code = self.factoryReboot(olt, ont_id, login_salida, tipo_accion)
            #print(f"Resultado unlink: {salida}")                                                # Debug
            if status_code == 200:
                logout_salida, logout_status_code = self.logout(login_salida)
                if logout_status_code == 200:
                    return salida, status_code
                else:
                    return logout_salida, logout_status_code
            else:
                return salida, status_code  
        else:
            return login_salida, login_status_code

    def factoryReboot(self, olt: str, ont_id: int, id_sesion: int, accion: str):
        url = f"http://{str(os.getenv('IP_CMS'))}/cmsexc/ex/netconf"
        headers = {'Content-Type': 'text/plain; charset=utf-8'}
        data = f"""
            <soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
            <soapenv:Body><rpc message-id="22" nodename="{olt}" timeout="35000" username="{str(os.getenv('CMS_USUARIO'))}" sessionid="{id_sesion}">
                <action>
                    <action-type>reset-ont</action-type>
                    <action-args>
                        <object>
                            <type>Ont</type>
                            <id>
                                <ont>{ont_id}</ont>
                            </id>
                        </object>
                        <{accion}>true</{accion}>
                    </action-args>
                </action>
            </rpc>
            </soapenv:Body></soapenv:Envelope>"""
        print(data)
        respuesta = requests.post(url, data=data, headers=headers)
        if respuesta.status_code == 200:
            #print(f"Respuesta del reboot: {respuesta.text}")                                   # Debug
            return "Reboot aplicado con exito", respuesta.status_code
        else:
             return "No se pudo aplicar el reboot", respuesta.status_code
        
        
class CiggDevice(Onu):
    # Atributos
    tipo = "Cigg"
    
    # Metodos
    def datos(self, serie: str, id_localidad: int):
        vendor, serial = normalizarSerial(serie)
        modelo = "InternetGatewayDevice.DeviceInfo.ModelName._value"
        firmware = "InternetGatewayDevice.DeviceInfo.SoftwareVersion._value"
        
        return self.datosACS(id_localidad, serial, modelo, firmware, vendor)
    
    def normalizarId(self, id_temporal: str):
        id = id_temporal.replace("%", "%25") 
        return id

          
class KaonDevice(Onu):
    # Atributos
    tipo = "Kaon"
    
    # Metodos
    def datos(self, serial: str, id_localidad: int):
        vendor = serial[:4]
        modelo = "Device.DeviceInfo.ModelName._value"
        firmware = "Device.DeviceInfo.SoftwareVersion._value"
        return self.datosACS(id_localidad, serial, modelo, firmware, vendor)
        
        
class HuaweiDevice(Onu):
    # Atributos
    tipo = "Huawei"
    
    # Metodos
    def datos(self, serial: str, id_localidad: int):
        vendor = serial[:4]
        modelo = "_deviceId._ProductClass"
        firmware = "InternetGatewayDevice.DeviceInfo.SoftwareVersion._value"
        #print(modelo,"    " ,firmware)
        return self.datosACS(id_localidad, serial, modelo, firmware, vendor)
    
    def normalizarId(self, id_temporal: str):
        id = id_temporal.replace("%", "%25") 
        return id
        
    
    def ubicacion(self, ubicacion: str):
        #placaPuerto, onu_id = self.placaPuertoId(ubicacion)                                                                    # 1/8 , 1
        placaPuerto, onu_id = placaPuertoId(ubicacion) 
        placaPuerto = "0/" + placaPuerto
        ubicacion = "/" + placaPuerto.replace("/", "\/") + "/"
        return ubicacion, onu_id
    
    
