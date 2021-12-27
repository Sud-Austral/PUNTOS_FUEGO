import ee
import geemap
import pandas as pd
import datetime
from datetime import timedelta
import sys
import git

Map = geemap.Map()    
studyArea = ee.FeatureCollection("users/APP_DATA_I/limites/CHL_regiones_sim");

FIRMS_colection2 =  ee.ImageCollection('FIRMS')
FIRMS_colection =  ee.ImageCollection('FIRMS')

def getPointByRegion(region,Fecha_inicial,Fecha_final):
    studyArea_region = studyArea.filterMetadata("Codreg","equals", region);     

    FIRMS4 =FIRMS_colection2 \
      .select(['T21']) \
      .filterDate(Fecha_inicial,Fecha_final) \
      .filterBounds(studyArea_region)

    FIRMS =FIRMS_colection \
      .select(['T21']) \
      .filterDate(Fecha_inicial,Fecha_final) \
      .filterBounds(studyArea_region)
    
    FIRMScount4  = ee.Image(FIRMS4.max()).clip(studyArea);
    FIRMSbinary4 = FIRMScount4.eq(FIRMScount4).rename('FIRMS_binary_alert_3');

    project_crs   = ee.Image(FIRMS.first()).projection().crs();
    scale = ee.Image(FIRMS.first()).projection().nominalScale(); 

    FIRMSpoint4 = FIRMSbinary4.reduceToVectors( \
      None, studyArea, scale,'centroid',True, 'modis_fire',project_crs,None, True)
    numero_PI = ee.FeatureCollection(FIRMSpoint4).filterBounds(studyArea_region)
    d = numero_PI.getInfo()
    #return d
    #print("Hola")
    #print(d["features"])
    return d["features"]

def Update(ref = pd.read_excel("https://github.com/Sud-Austral/PUNTOS_FUEGO/raw/main/Data/ConsolidadoPuntosFuego.xlsx")):
    #ref = pd.read_excel("D:\github\PUNTOS_FUEGO\Data\ConsolidadoPuntosFuego.xlsx")
    
    regiones = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16"]
    FI = datetime.datetime.strptime(ref["Fecha_Texto"].max(), '%Y-%m-%d') #+  timedelta(days=1)
    salida = []
    flag = True
    #while FI < datetime.datetime.now() +  timedelta(days=1) and flag:
    while FI < datetime.datetime.now() and flag:
        print(datetime.datetime.now().strftime('%H:%M:%S'))
        FF = FI +  timedelta(days=1)
        FI_text = FI.strftime('%Y-%m-%d')
        FF_text = FF.strftime('%Y-%m-%d')
        print("Comenzamos con las fechas:")
        print(f"Inicial: {FI_text} y Final: {FF_text}")        
        try:
            for region in regiones:
                result = getPointByRegion(region,FI_text,FF_text)
                print(len(result))
                diccionario = {"Región":region,"Fecha":FI,"Fecha_Texto":FI_text, \
                            "Cantidad de Puntos":len(result)}
                salida.append(diccionario.copy())
                #pd.DataFrame(salida).to_csv(f"Avance_{FI_text}.csv", index=False)
            FI = FF    
            print("Terminamos con las fechas")
            print(datetime.datetime.now().strftime('%H:%M:%S'))
        except:
            error = sys.exc_info()[1]
            print(error)
            flag = False
    return pd.DataFrame(salida)

def SaveConsolidado():
    ref = pd.read_excel("https://github.com/Sud-Austral/PUNTOS_FUEGO/raw/main/Data/ConsolidadoPuntosFuego.xlsx")
    dfUpdate = Update(ref)
    df = pd.concat([ref,dfUpdate])
    df.to_excel("Data/ConsolidadoPuntosFuego.xlsx", index=False)
    return False

def guardarRepositorio():
  #Esta linea crea un objeto para manejar el repositorio alojado en la ruta
  #Correspondinete al argumento entregado en String
  repoLocal = git.Repo(r'C:\Users\datos\Documents\GitHub\PUNTOS_FUEGO')  
  try:
      #Agrego todos los archivos nuevos
      repoLocal.git.add(".")
      #Hace el commit con un comentario sobre el origen del mismo y la hora
      repoLocal.git.commit(m='Update automatico via Actualizar ' + datetime.datetime.now().strftime("%m-%d-%Y %H-%M-%S"))
      #Apuntamos al gitHub (online)
      origin = repoLocal.remote(name='origin')
      #Se hace el push (enviar los archivos al repositorio online)
      origin.push()
      #Mensaje simpatico que todo salio bien
      print("Repositorio actualizado =)")
  except:
      #Da un mensaje de error al fallar
      print("Error de GITHUB")    
  return
