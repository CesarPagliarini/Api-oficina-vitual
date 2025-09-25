from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, Response
from sqlalchemy import join
from esquemas.dispositivos.onu import Onu                                                 # Esquema de datos de onu
from esquemas.suscriptores.suscriptor import Suscriptor
from funciones.funciones import *
from modelos.dispositivo.marcas import modelos, marcas, modos_operacion                                # Modelo de datos de las onus
from modelos.parametro.parametros import firmware
from modelos.dispositivo.dispositivos import tipo_dispositivos
from middlewares.acceso_token_rutas import VerifyTokenRoute
from middlewares.clases_onus import obtenerTipoOnu
from middlewares.acceso_usuario import verificacionRol
from retry import retry


rutasOnu = APIRouter(route_class=VerifyTokenRoute, prefix="/onus", dependencies=[Depends(verificacionRol())])
rutasOnu = APIRouter(prefix="/onus")

     
@retry(tries=3, delay=1)
@rutasOnu.get("/{serial}/{id_localidad}")
async def datosOnu(serial: str, id_localidad: int, request: Request, onu: Onu = Depends(obtenerTipoOnu)):
    suscriptor = Suscriptor()
    respuesta, datos_status_code = onu.datos(serial, id_localidad)                             
    #print(f"respuesta: {respuesta}")                                                            # Debug
    #print(f"datos_status_code: {datos_status_code}")                                            # Debug
    resultado_fdm, fdm_status_code = suscriptor.getInfoFdm(serial)
    #print(f"resultado_fdm: {resultado_fdm}")                                                    # Debug
    #print(f"status_code_fdm: {fdm_status_code}")                                                # Debug
    status_code = 404
    if fdm_status_code == 200:
        if datos_status_code == 404:
            return JSONResponse(content={"message": "Fallo la comunicacion con el ACS"}, status_code=404)                                                                                        
        elif datos_status_code == 200 and respuesta['equipo']['modelo'] != None:
            modelo = respuesta['equipo']['modelo']
            #print(modelo)                                                                       # Debug
        else:
            modelo = resultado_fdm['model']['value']
            respuesta['equipo']['firmware'] = resultado_fdm['swVer']['value'] 
        respuesta['equipo']['modelo'] = modelo
        estado_onu = estado(resultado_fdm['status']['value'])
        consulta = join(join(modelos, marcas), tipo_dispositivos).select().where(modelos.c.modelo == modelo)
        resultado = consultaMysql(consulta, 'first')      
        if resultado or estado_onu == 'offline': # Evaluar aca para separar cuando esta offline de cuando no se encuentra
            if estado_onu != 'offline':
                respuesta['equipo']['id_modelo'] = resultado[0]
            else:
                respuesta['equipo']['id_modelo'] = "-"
            consulta = firmware.select().where(firmware.c.firmware == respuesta['equipo']['firmware'])
            resultado = consultaMysql(consulta, 'first')
            #if resultado or respuesta['equipo']['firmware'] == None:
            if resultado or estado_onu == 'offline':
                #if respuesta['equipo']['firmware'] == None:
                if estado_onu == 'offline':
                    respuesta['equipo']['firmware'] = "-"
                    respuesta['equipo']['id_firmware'] = "-"
                else:
                    respuesta['equipo']['id_firmware'] = resultado[0]
                consulta = join(modelos, modos_operacion).select().where(modelos.c.id_modelo == respuesta['equipo']['id_modelo'])
                resultado = consultaMysql(consulta, 'first')
                if resultado or estado_onu == 'offline':
                    respuesta['valores']['nombre_olt'] = resultado_fdm['oltName']['value']
                    respuesta['valores']['interfaz'] = resultado_fdm['interface']['value']
                    respuesta['valores']['estado'] = estado_onu
                    #if respuesta['valores']['estado'] != 'offline':                                                                         # Si la Onu esta offline, no sigue consultando valores, los setea a 0
                    #    respuesta['valores']['uptime'] = uptime(resultado_fdm['upTime']['value'])
                    del respuesta['equipo']['modelo']
                    return JSONResponse(content=respuesta, status_code=200)
                else:
                    return JSONResponse(content={"message": "El modelo no existe en la base de datos"}, status_code=404)
            else:
                return JSONResponse(content={"message": "No se encontró la version de firmware en la base de datos"}, status_code=404)
        else:
            return JSONResponse(content={"message": "No se encontró la marca ,o el modelo no esta ingresado en la base de datos"}, status_code=404)      
    else:
        return JSONResponse(content={"message": "El dispositivo no se encontró en el ACS ni Stech"}, status_code=status_code)       
    

@rutasOnu.post("/wifi")
async def getWifi(request: Request, onu: Onu = Depends(obtenerTipoOnu)):
    body = await request.json()
    id_localidad = body.get('id_localidad')
    serial = (body.get('serial')).upper()
    id_modelo = body.get('id_modelo')
    id_firmware = body.get('id_firmware')
    red = body.get('red')                                                                                               # Red: 2.4 / 5.8 / 6
    accion = body.get('accion')                                                                                         # Acciones: get  / set 
    contador_canal_uso = 0
    descripcion = [f"Rama Wifi {red}", f"SSID {red}", f"Password {red}", f"Canal {red}", f"Rama Canal {red}", f"Canal en uso {red}", f"Posibles canales {red}"]
    descripcion = [f"SSID {red}", f"Password {red}", f"Canal {red}", f"Canal en uso {red}", f"Posibles canales {red}"]
    id_temporal, _id_status_code = onu.getInfo(id_localidad, id_firmware, id_modelo, serial, "Id de equipo")                          # Obtiene el valor del _id (id interno del ACS para cada onu)
    _id = id_temporal.replace("%", "%25") 
    #print(f"_id: {_id}")                                                                                               # Debug
    if accion == "get":
        #for i in range(0,7):
        for i in range(0,4):                                                                                            # Prueba - La onu refresca esta rama cada hora - Controlar si funciona!!!
            #print(descripcion[i])                                                                                      # Debug
            onu.accionesOnu(id_localidad, _id, id_firmware, id_modelo, descripcion[i], "refreshObject")                               # Refresca los valores de las distintas ramas
        ssid, ssid_status_code= onu.getInfo(id_localidad, id_firmware, id_modelo, serial, descripcion[0])                             # Obtiene el valor de ssid seteado en la onu
        #print(f"SSID: {ssid}")                                                                                          # Debug
        #password, password_status_code = onu.getInfo(id_localidad, id_firmware, id_modelo, serial, descripcion[1])                    # Obtiene el valor de password seteado en la onu
        password = "-"
        #print(f"Contraseña: {password}")                                                                                # Debug
        try:
            canal_en_uso, canal_status_code = onu.getInfo(id_localidad, id_firmware, id_modelo, serial, descripcion[3])                   # Verifica si el canal automatico esta encendido
            #print(f"Canal en uso: {canal_en_uso}")                                                                          # Debug
        except:
            if contador_canal_uso >= 1:
                canal_en_uso == ""
            else:
                contador_canal_uso += 1
                onu.accionesOnu(id_localidad, _id, id_firmware, id_modelo, descripcion[3], "refreshObject")
                canal_en_uso, canal_status_code = onu.getInfo(id_localidad, id_firmware, id_modelo, serial, descripcion[3])
        if canal_en_uso == "":
            canal_en_uso = 0
        canal, canal_status_code = onu.getInfo(id_localidad, id_firmware, id_modelo, serial, descripcion[2])                      # Obtiene el valor del canal seteado en la onu
        #print(f"Canal: {canal}")                                                                                        # Debug
        if canal == "":
            canal = 0
        posibles_canales, posibles_canal_status_code = onu.getInfo(id_localidad, id_firmware, id_modelo, serial, descripcion[4])      # Obtiene la lista de posibles canales a setear en la onu
        #print(f"Posibles canales: {posibles_canales}")                                                                  # Debug
        if posibles_canales == '':    
            posibles_canales = canalesPosibles(red)  
        if len(posibles_canales) <= 7:
                posibles_canales = normalizarCanalesPosibles(posibles_canales, red)
                
        return JSONResponse(content={
            "message": "Operacion exitosa",
            "ssid": ssid,
            "password": password,
            "canal en uso": canal_en_uso,
            "canal": canal,
            "posibles canales": posibles_canales
            }, status_code=200)
    elif accion == "set":
        ssid_request = body.get('ssid')
        password_request = body.get('password')
        canal_request = body.get('canal')
        elementos = [ssid_request, password_request, canal_request]
        for i in range(0, len(elementos)):
            if elementos[i] != "":
                  onu.setInfo(id_localidad, id_firmware, id_modelo, descripcion[i], _id, elementos[i])     # Solo modifica los parametros que cambian, sino llegan vacios.
                  #print(elementos[i])                                                           # Debug
        return JSONResponse(content={"message": "Cambio aplicado con exito"}, status_code=200)


@rutasOnu.post("/acciones")                                                                     # Reset, Factory Reset
async def acciones(request: Request, onu: Onu = Depends(obtenerTipoOnu)):
    body = await request.json()
    id = body.get('id')
    accion = body.get('accion')                                                                 # El contenido de "accion" debe ser: factoryReset o reboot
    ont_id = body.get('ont_id')
    olt = body.get('olt')
    id_localidad = body.get('id_localidad')
    respuesta = onu.rebootFactory(id_localidad, id, accion, None, ont_id, olt)
    if respuesta:
        return JSONResponse(content={"message": f"El {accion} se aplico correctamente"}, status_code=200)
        #return f"El {accion} se aplico correctamente"
    else:
        return JSONResponse(content={"message": f"No se pudo aplicar el {accion}, intente mas tarde"}, status_code=404)
        #return f"No se pudo aplicar el {accion}, intente mas tarde"
        
         
@rutasOnu.post("/ip/")
async def direccionIp(request: Request, onu: Onu = Depends(obtenerTipoOnu)):
    body = await request.json()
    id_localidad = body.get('id_localidad')
    id_acs = body.get('id') or ""               # Si 'id' es None o vacío, asignar un string vacío
    serial = body.get('serial')
    id_modelo = body.get('id_modelo')
    id_firmware = body.get('id_firmware')
    nombre_olt = body.get('nombre_olt')
    interfaz = body.get('interfaz')
    servicio = body.get('servicio')
    placaPuerto, id = placaPuertoId(interfaz)
    #print(id_localidad, serial, nombre_olt, interfaz, servicio, placaPuerto, id)
    datos, status_code = await onu.obtenerIp(id_localidad, nombre_olt, placaPuerto, id, servicio, serial, id_firmware, id_modelo, id_acs)
    if status_code == 204:
        return Response(status_code=204)                                                # Si devuelve 204, no hay registros de la onu en la Db.
    return JSONResponse(content=datos, status_code=status_code)



