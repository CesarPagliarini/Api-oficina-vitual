from utiles.config import DatosConexion as datos
from utiles.config import DatosConexionInfluxRosario as datosRosarioInflux
from utiles.config import DatosConexionInfluxSalta as datosSaltaInflux
from utiles.config import DatosConexionInfluxSantiago as datosSantiagoInflux
from sqlalchemy import create_engine, MetaData
from influxdb_client import InfluxDBClient

#engine = create_engine(datos.DB_URL)
engine = create_engine(datos.DB_URL, pool_recycle=60 * 60 * 4, pool_pre_ping=True)            # Verificar si no da el error de conexion a la DB al iniciar por primera vez.

try:
    conexion = engine.connect()
    meta_data = MetaData()
    #print("Conexion a la DB exitosa")       # Debug
    
except Exception as e:
    print("Existe un error: ", e)

try:
    #cliente_rosario = InfluxDBClient(url='http://200.3.220.59:8086', token='IzQou24SqRc75Pm5H6HLh3UNrjF8Qm5wCWrx3klO4nQp7RFD2K5EYWlMPibizVcmF8Q5u3wFH3QkDislBG156Q==', org='express')
    cliente_rosario = InfluxDBClient(url=datosRosarioInflux.DB_URL, token=datosRosarioInflux.DB_TOKEN, org=datosRosarioInflux.DB_ORGANIZACION)
    cliente_rosario.ping()
    conexion_rosario = cliente_rosario.query_api()
    #print(conexion_rosario)                                                                                        # Debug
except Exception as e:
    print("Error en la conexión a InfluxDB Rosario: ", e)
    raise SystemExit("No se pudo establecer la conexión a InfluxDB Rosario. La aplicación se detiene.")


#try:
#    conexion_salta = InfluxDBClient(url=datosSalta.DB_URL, token=datosSalta.DB_TOKEN, org=datosSalta.DB_ORGANIZACION)
#    conexion_salta.ping()
#    #print(conexion_salta)                   # Debug
#except Exception as e:
#    print("Error en la conexión a InfluxDB Salta: ", e)
#    raise SystemExit("No se pudo establecer la conexión a InfluxDB Salta. La aplicación se detiene.")
#
#
#try:
#    conexion_santiago = InfluxDBClient(url=datosSantiago.DB_URL, token=datosSantiago.DB_TOKEN, org=datosSantiago.DB_ORGANIZACION)
#    conexion_santiago.ping()
#    #print(conexion_santiago)                # Debug
#except Exception as e:
#    print("Error en la conexión a InfluxDB Santiago: ", e)
#    raise SystemExit("No se pudo establecer la conexión a InfluxDB Santiago. La aplicación se detiene.")
