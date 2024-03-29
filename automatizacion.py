import requests
import json
import pandas as pd
import sys
import datetime
import json
import pandas as pd
from geopy.geocoders import Nominatim

fuentes = [["https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_South_America_7d.csv",
            "MODIS"]]

def setComuna(x):
    if(x["city"] != ""):
        return x["city"]
    elif(x["town"] != ""):
        return x["town"]
    elif(x["village"] != ""):
        return x["village"]
    else:
        return x["suburb"]

def getComunas(df):
    geolocator = Nominatim(user_agent="geoapiExercises")
    print(df.columns)
    print(1)
    df['Coordenadas'] = df[['latitude', 'longitude']].apply(lambda x: f'{x.latitude},{x.longitude}', axis=1)
    print(2)
    df["Locacion"] = df["Coordenadas"].apply(lambda x: geolocator.reverse(x))
    referencia = ['road', 'city', 'county', 'state', 'country', 'country_code',
       'industrial', 'town', 'isolated_dwelling', 'hamlet', 'postcode',
       'building', 'neighbourhood', 'region', 'suburb', 'amenity',
       'man_made', 'village', 'office', 'historic', 'aeroway', 'tourism',
       'state_district', 'highway']
    print(3)
    for i in referencia:
        def AgregarColumn(x):
            try:
                return x.raw["address"][i]
            except:
                return ""
        df[i] = df["Locacion"].apply(lambda x: AgregarColumn(x))
    print(4)
    dfChile = df[df["country"] == "Chile"]
    print(5)
    dfChile = dfChile.reset_index()
    print(6)
    dfChile["Comuna"] = dfChile[["city","town","village","suburb"]].apply(setComuna, axis=1)
    ref = pd.read_excel(r"LocalizaGoogle.xlsx")
    print(7)
    ref = ref[['REGION', 'PROVINCIA', 'COMUNA','Comuna', 'ComunaUpper', 'raw']]
    dfFinal = dfChile.merge(ref, left_on='Comuna', right_on='Comuna',how="left")
    print(8)
    return dfFinal

def descarga(fuente):
    url = fuente[0]
    print(url)   
    #url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_South_America_7d.csv"
    #df = pd.read_csv("https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_South_America_24h.csv")
    df = pd.read_csv(url) #.iloc[:200,:]
    #dfDate = df[df["acq_date"] == datetime.datetime.now().strftime("%Y-%m-%d")]
    #if(len(dfDate) > 0):
    dfDate = df
    dfLat = dfDate[dfDate["latitude"] < -16.5]
    dfLat2 = dfLat[dfLat["longitude"] < -69.5]
    dfLat2 = dfLat2.reset_index()
    return dfLat2

def getJSON(fuente):
    df = descarga(fuente)
    features = []
    features2 = []
    for i, j in df.iterrows():
        f = {'type': 'Feature', \
            'geometry': {'type': 'Point', 'coordinates': [j["longitude"], j["latitude"]]}, \
            'properties': {'acq_date': j["acq_date"]}}
        features.append(f.copy())
        f = {'acq_date': j["acq_date"],"lat":j["latitude"],"lng":j["longitude"]}
        features2.append(f.copy())
    salida = {"type":"FeatureCollection","features":features}
    with open(f'Data/{fuente[1]}/heatmap_{fuente[1]}.json', 'w') as file:
        json.dump(salida, file, indent=4)
    with open(f'Data/{fuente[1]}/data_{fuente[1]}.json', 'w') as file:
        json.dump(features2, file, indent=4)
    return True

def proceso():
    for i in fuentes:
        #descarga(i)
        getJSON(i)
    #'Data/J1/Puntos_Diarios_J1.csv'
    salida = []
    for ruta in ["MODIS","SUOMI","J1"]:
    #for ruta in ["MODIS"]:
        file = f'Data/{ruta}/Puntos_Diarios_{ruta}.csv'
        dfaux = pd.read_csv(file)
        dfaux["Fuente"] =  ruta
        salida.append(dfaux)
    pd.concat(salida).to_excel("Data/Consolidado/ConsolidadoPuntosCalor.xlsx", index=False)
    return

def saveConsolidado():
    data = pd.read_excel(r"Data/ConsolidadoPuntosFuego.xlsx")
    

    df           = pd.read_csv(fuentes[0][0])
    df["Fuente"] = fuentes[0][1]
    consolidadoUpdate = df[df["acq_date"].apply(lambda x: x not in data["Fecha_Texto"].unique())]
    consolidadoUpdate = consolidadoUpdate[consolidadoUpdate["acq_date"].apply(lambda x: x != consolidadoUpdate["acq_date"].max())]
    #consolidadoUpdate = consolidadoUpdate.reset_index()
    dfDate = consolidadoUpdate
    dfLat = dfDate[dfDate["latitude"] < -16.5]
    dfLat2 = dfLat[dfLat["longitude"] < -69.5]
    dfLat2 = dfLat2.reset_index()
    dfLat2 = getComunas(dfLat2)
    dfSalida = dfLat2[["acq_date","REGION"]]
    dfSalida = dfSalida.groupby(["acq_date","REGION"]).size().reset_index(name='counts')
    
    dfSalida.columns = ["Fecha","Región","Cantidad de Puntos"]
    dfSalida["Fecha_Texto"] = dfSalida["Fecha"]
    dfSalida["Fecha"] = dfSalida["Fecha"].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
    dfSalida = pd.concat([data,dfSalida])
    #try:
    #    dfLat2 = getComunas(dfLat2)
    #except:
    #    error = sys.exc_info()[1]
    #    print(error)
    #    print("Error en getComunas")
    #dfFinal = pd.concat([consolidado,dfLat2])
    #dfFinal = dfFinal.reset_index()
    #dfFinal2 = dfFinal.drop(columns=["level_0","index","Unnamed: 0"])
    dfSalida.to_excel(r"Data/ConsolidadoPuntosFuego.xlsx", index=False)
    print("ya deberia estar")
    #print(dfFinal)
    return 

if __name__ == '__main__':
    print(1)
    print("Se inicia")
    try:
        saveConsolidado()
        #proceso()
        print("Hola todo bien")
    except:
        error = sys.exc_info()[1]
        print(error)
    