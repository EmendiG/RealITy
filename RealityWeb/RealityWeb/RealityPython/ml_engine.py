import pandas as pd
import geopandas as gpd

from sqlalchemy import create_engine
import psycopg2

from shapely.geometry import Point
from shapely import wkb

from math import log2
import gzip
import re
import time
import os 

POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

db_dane = {
            'name': POSTGRES_USER, 
            'password': POSTGRES_PASSWORD, 
            'hostname': POSTGRES_HOST, 
            'db_name': 'realestate_zero'
}

def PostgreSQL_connectSQLalchemy():
    db_connection_str = 'postgresql://{name}:{password}@{hostname}/{db_name}'.format(**db_dane)
    db_connection = create_engine(db_connection_str)
    return db_connection.connect()

def PostgreSQL_connectPsycopg2():
    con = psycopg2.connect(user=db_dane['name'], password=db_dane['password'], host=db_dane['hostname'],
                           database=db_dane['db_name'])
    return con

def PosgreSQL_gettables():
    cursor = PostgreSQL_connectPsycopg2().cursor()
    cursor.execute("""select "relname" from "pg_class" where relkind='r' and "relname" !~ '^(pg_|sql_)';""")
    tables = cursor.fetchall()
    return [tab[0] for tab in tables]

def PosgreSQL_oferty_Merger_assignDistricts(miasto, lat, lon):
    # Adjust existing table that contains offers and assign proper district name according to geographical coordinates
    city_districts = gpd.read_file(f'RealityWeb/RealityPython/districts/{miasto}.json')
    point = Point(lon, lat)
    for dzielnica in city_districts.iterrows():
        if dzielnica[1]['geometry'].contains(point):
            return dzielnica[1]['name']

def PostgreSQL_getfeatures(tabletolookin:str, miasto, lat:float, lon:float, tempDict):
    conn = PostgreSQL_connectSQLalchemy()
    point = Point(lon, lat)
    if 'Node' in tabletolookin:
        df_lat_lon = pd.read_sql(f"""SELECT * FROM "{tabletolookin}" WHERE "{tabletolookin}"."Miasto"='{miasto}' """, con=conn)
        gdf_lat_lon = gpd.GeoDataFrame(df_lat_lon, geometry=gpd.points_from_xy(df_lat_lon.Longitude,
                                                                               df_lat_lon.Latitude))
        arr_lat_lon = gdf_lat_lon.to_numpy()

        for node in arr_lat_lon:
            if point.distance(node[7]) < 0.004:
                if node[1] not in tempDict.keys():
                    tempDict[node[1]] = 1
                else:
                    tempDict[node[1]] += 1
    else:
        df_geometry = pd.read_sql(f"""SELECT * FROM "{tabletolookin}" WHERE "{tabletolookin}"."Miasto"='{miasto}' """, con=conn)
        df_geometry['Geometry'] = df_geometry['Geometry'].apply(lambda x: wkb.loads(x, hex=True))
        arr_geometry = df_geometry.to_numpy()
        temp_relation_dict = {}

        for poly in arr_geometry:
            if poly[2].geom_type == 'Polygon':
                if poly[2].exterior.distance(point) < 0.004:
                    if poly[1] not in tempDict.keys():
                        tempDict[poly[1]] = 1
                    else:
                        tempDict[poly[1]] += 1
            elif poly[2].geom_type == 'MultiPolygon':
                for r in poly[2]:
                    if r.exterior.distance(point) < 0.004:
                        if poly[0] not in temp_relation_dict.keys():
                            temp_relation_dict[poly[0]] = ''
                            if poly[1] not in tempDict.keys():
                                tempDict[poly[1]] = 1
                            else:
                                tempDict[poly[1]] += 1


def RealityPython_MLREP_getPrice(request):
    """ Get real estate price (per square meter) given the RealityWeb forms output """
    miasto = 'warszawa'
    myData = request.POST
    myDataDict = dict(myData)
    all_tables = PosgreSQL_gettables()

    start = time.time()
    tempDict = {}
    for table in all_tables:
        if '_Node' in table and '_Node_' not in table and 'relation' not in table or '_Rel' in table and '_Rel_' not in table or '_Way' in table and '_Way_' not in table:
            PostgreSQL_getfeatures(table, miasto, float(myData['lat']), float(myData['lon']), tempDict)

    tempDict2 = {}
    doNotCheckList = ['lat', 'lon', 'area', 'rok_zabudowy', 'liczba_pokoi', 'pietro', 'max_liczba_pieter', 'csrfmiddlewaretoken', 'tagi' ]
    for data in myDataDict.keys():
        if data not in doNotCheckList:
            tempDict2[f'{data.capitalize()}_{myDataDict[data][0]}'] = 1
        else:
            tempDict2[f'{data.capitalize()}'] = myDataDict[data][0]
    tempDict2['Opis'] = tempDict2.pop('Tagi')
    tempDict2['Latitude'] = tempDict2.pop('Lat')
    tempDict2['Longitude'] = tempDict2.pop('Lon')
    tempDict2['Area_log'] = log2(float(tempDict2['Area']))
    if tempDict2['Pietro'] != 0:
        tempDict2['Pietro_do_dachu'] = float(tempDict2['Pietro'])/float(tempDict2['Max_liczba_pieter'])
    else:
        tempDict2['Pietro_do_dachu'] = 0
    tempDict2.pop('Csrfmiddlewaretoken')

    district = PosgreSQL_oferty_Merger_assignDistricts(miasto, float(myData['lat']), float(myData['lon']))
    tempDict3 = {}
    tempDict3[f'Dzielnica_{district}'] = 1

    z = {**tempDict, **tempDict2, **tempDict3}
    # file = open('RealityWeb/RealityPython/models/col_zero_model_warszawa.sav', 'rb')
    empty_df = pd.read_pickle('RealityWeb/RealityPython/models/col_zero_model_warszawa.sav')
    for n, col in enumerate(empty_df.columns):
        if col in z.keys():
            empty_df.loc[0, col] = z[col]

    n = 0
    for i in empty_df.iterrows():
        n += 1
        l = list(splitter.split(i[1][1]))
        raw_corpus.append(l)

    empty_df["opisTT"] = empty_df['Opis'].apply(
        lambda x: ' '.join(preprocessing(x, filter_raw=True, filter_dict=True)))
    empty_df["opisTF"] = empty_df['Opis'].apply(
        lambda x: ' '.join(preprocessing(x, filter_raw=True, filter_dict=False)))
    empty_df["opisFT"] = empty_df['Opis'].apply(
        lambda x: ' '.join(preprocessing(x, filter_raw=False, filter_dict=True)))
    empty_df["opisFF"] = empty_df['Opis'].apply(
        lambda x: ' '.join(preprocessing(x, filter_raw=False, filter_dict=False)))

    wynik = 2**pd.read_pickle('RealityWeb/RealityPython/models/model_warszawa.sav').predict(pd.DataFrame(empty_df))[0]
    print('znalezienie wszystkich featurow trwa: ', time.time() - start)
    # print(empty_df) # to get ML input
    # print(wynik)    # to get ML output
    return wynik


# Change_COLUMN(Opis) to opisTT / opisFT / opisTF /opisFF <--> This should be in memory ALL the time to
# shorten the time needed to process the description from around 9/11 seconds to 1,5 seconds
splitter = re.compile(r'[^ąąćęńłóóśśżżź\w]+')
isnumber = re.compile(r'[0-9]')
f = gzip.open('RealityWeb/RealityPython/models/odm.txt.gz', 'rt', encoding='utf-8')
dictionary = {}
set_dict = set()
for x in f:
    t = x.strip().split(',')
    tt = [x.strip().lower() for x in t]
    for w in tt:
        set_dict.add(w)
        dictionary[w] = tt[0]
def lematize(w):
    w = w.replace('ą', 'ą')
    w = w.replace('ó', 'ó')
    w = w.replace('ę', 'ę')
    w = w.replace('ż', 'ż')
    return dictionary.get(w, w)
raw_corpus = []
all_words = []
for t in raw_corpus:
    all_words[0:0] = t
words = {}
for w in all_words:
    rec = words.get(w.lower(), {'upper': 0, 'lower': 0})
    if w.lower() == w or w.upper() == w:
        rec['lower'] = rec['lower'] + 1
    else:
        rec['upper'] = rec['upper'] + 1
    words[w.lower()] = rec
raw_stop_words = [x for x in words.keys() if words[x]['upper'] >= words[x]['lower'] * 4]
set_raw_stop_words = set(raw_stop_words)
def preprocessing(opis, filter_raw=True, filter_dict=True):
    opis = str(opis)
    tokenized = splitter.split(opis)
    l = list(tokenized)
    l = [x.lower() for x in l]
    l = [x for x in l if len(x) > 2]
    l = [x for x in l if x.find('_') < 0]
    l = [x for x in l if isnumber.search(x) is None]
    if filter_raw: l = [x for x in l if x not in set_raw_stop_words]
    if filter_dict: l = [x for x in l if x in set_dict]
    l = [lematize(x) for x in l]
    l = [x for x in l if len(x) > 2]
    return l