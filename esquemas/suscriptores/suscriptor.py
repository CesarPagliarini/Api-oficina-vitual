from pydantic import BaseModel
import os
import requests
from requests.auth import HTTPBasicAuth

class Suscriptor(BaseModel):
    
    # Metodos
    
    def getInfoFdm(self, serial:str):                                                                                   # Trae informacion del FDM                        
        status_code = 404
        url_a = f"http://{str(os.getenv('IP_FDM'))}/fdm/api/v0.2/devices/ont/"
        url_b = '/info'
        url = url_a + serial + url_b
        #url = "http://200.81.125.175:8087/fdm/api/v0.2/devices/ont/CXNK0068322A/info"                                                    # Debug
        auth = HTTPBasicAuth(str(os.getenv('FDM_USUARIO')), str(os.getenv('FDM_PASSWORD')))
        #print(url)                                                                                                                       # Debug
        response = requests.get(url, auth=auth, data=None, headers=None)
        #print(response.status_code)                                                                                                      # Debug
        if response.status_code == 200 and response.json()['Error_code'] != '404':
            auxiliar = response.json()['Items']
            #print(response.json())                                                                                                       # Debug 
            return auxiliar, response.status_code
        elif response.status_code != 500:
            #print(status_code)
            return "El dispositivo no se encontró", status_code
        else:
            return "Fallo la comunicacion con Stech", status_code
        
    #def getSuscripcionDsa(self, suscriptor: str):
    #    status_code = 404
    #    url_a = f"http://{str(os.getenv('IP_DSA'))}/dsa/api/v1.0/subscriber/"
    #    url_b = '/subscription'
    #    url = url_a + suscriptor
    #    url_2 = url + url_b
    #    auth = HTTPBasicAuth(str(os.getenv('DSA_USUARIO')), str(os.getenv('DSA_PASSWORD')))
    #    response = requests.get(url, auth=auth, data=None, headers=None)
    #    #print(response.text)
    #    if response.status_code == 200 and response.json()['Error_code'] != 404:
    #        campos_extraidos = {}
    #        campos_extraidos['Abonado'] = response.json()['Items']['name']                  # Obtiene el nombre del abonado
#
    #        response = requests.get(url_2, auth=auth, data=None, headers=None)
#
    #        if response.status_code == 200 and response.text != "[\n\n]":
    #            auxiliares = response.json()['Items']
    #            suscripciones = []
#
    #            for auxiliar in auxiliares:
    #                serial = auxiliar['deviceId']
    #                if serial == None:
    #                    serial = "No posee dispositivos instalados"
    #                suscripcion = {
    #                    'suscripcion': auxiliar['id'],
    #                    'serial': serial.upper(),                           # Si lo dejo en minusvula, el ACS no lo reconoce y da error.
    #                    'direccion': auxiliar['address'],
    #                }
    #                suscripciones.append(suscripcion)
#
    #            campos_extraidos['Suscripciones'] = suscripciones
    #            return campos_extraidos, response.status_code
    #        else:
    #            return "El suscriptor no posee suscripciones creadas", status_code
    #    elif response.status_code != 500:
    #        return f"El suscriptor {suscriptor} no existe", status_code
    #    else:
    #        return "Fallo la comunicacion con Stech", status_code
    
