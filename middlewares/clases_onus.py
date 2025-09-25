from esquemas.dispositivos.onu import CalixDevice, CiggDevice, KaonDevice, HuaweiDevice
from fastapi import Request
    
def determinarTipoOnu(serial:str):                          # Determina cual es el objeto que se debe instanciar en base al serial
    if len(serial) == 16:
        return HuaweiDevice()
    elif serial[:4] == 'KAON':
        return KaonDevice()
    elif serial[:4] == 'CXNK': 
        return CalixDevice()
    elif serial[:4] == 'CIGG': 
        return CiggDevice()
    else:
        raise ValueError('Serial no reconocido') 

def obtenerSerial(id:str):                                  # Procesa el id para extraer el serial
    partes = id.split('-')
    if len(partes) > 2:
        serial = partes[2]
        #print(serial)                                      # Debug
        return serial
        
    
async def obtenerTipoOnu(request: Request):
    serial = None
    if request.method == 'GET':
        serial = request.path_params.get('serial')
    elif request.method == 'POST':
        nro_serial = (await request.json()).get('serial')
        #print(nro_serial)
        if nro_serial is None:
            id = (await request.json()).get('id')
            serial = obtenerSerial(id)
        else:
            serial = nro_serial           
    else:
        return "Metodo no permitido"
    
    onu = determinarTipoOnu(serial)     # Devuelve un objeto instanciado
    #print(onu)                         # Debug
    #request.state.onu = onu            # Crea una instancia del objeto ONU y la guárda en el estado de la solicitud
    return onu

   
    
    