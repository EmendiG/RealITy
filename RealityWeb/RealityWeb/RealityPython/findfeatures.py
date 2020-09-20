import pandas as pd
import geopandas as gpd

from sqlalchemy import create_engine
import psycopg2
import os

from shapely.geometry import Point
from shapely import wkb
import re
import math

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', default="postgres")
POSTGRES_USER = os.environ.get('POSTGRES_USER', default="realityadmin")
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', default="Reality1!")

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

def PostgreSQL_getfeatures(tabletolookin:str, miasto, radius, lat:float, lon:float, tempDict):
    conn = PostgreSQL_connectSQLalchemy()
    point = Point(lon, lat)
    radius = int(radius)/100000
    if 'Node' in tabletolookin:
        df_lat_lon = pd.read_sql(f"""SELECT * FROM "{tabletolookin}" WHERE "{tabletolookin}"."Miasto"='{miasto}' """, con=conn )
        gdf_lat_lon = gpd.GeoDataFrame(df_lat_lon, geometry=gpd.points_from_xy(df_lat_lon.Longitude,
                                                                               df_lat_lon.Latitude))
        arr_lat_lon = gdf_lat_lon.to_numpy()
        for node in arr_lat_lon:
            if ((lon - node[2])/1.4)**2 + ((lat - node[3])*1.2)**2 < radius**2:
                if node[1] not in tempDict.keys():
                    tempDict[node[1]] = []
                    tempDict[node[1]].append(list(node[1:5]))
                else:
                    tempDict[node[1]].append(list(node[1:5]))

    else:
        df_geometry = pd.read_sql(f"""SELECT * FROM "{tabletolookin}" WHERE "{tabletolookin}"."Miasto"='{miasto}' """, con=conn)
        df_geometry['Geometry'] = df_geometry['Geometry'].apply(lambda x: wkb.loads(x, hex=True))
        arr_geometry = df_geometry.to_numpy()
        temp_relation_dict = {}

        for poly in arr_geometry:
            if poly[2].geom_type == 'Polygon':
                if poly[2].exterior.distance(point) < radius:
                    if poly[1] not in tempDict.keys():
                        tempDict[poly[1]] = []
                        tempDict[poly[1]].append([poly[1], poly[2].centroid.x, poly[2].centroid.y, poly[3]])
                    else:
                        tempDict[poly[1]].append([poly[1], poly[2].centroid.x, poly[2].centroid.y, poly[3]])
            elif poly[2].geom_type == 'MultiPolygon':
                for r in poly[2]:
                    if r.exterior.distance(point) < radius:
                        if poly[0] not in temp_relation_dict.keys():
                            temp_relation_dict[poly[0]] = ''
                            if poly[1] not in tempDict.keys():
                                tempDict[poly[1]] = []
                                tempDict[poly[1]].append([poly[1], poly[2].centroid.x, poly[2].centroid.y, poly[3]])
                            else:
                                tempDict[poly[1]].append([poly[1], poly[2].centroid.x, poly[2].centroid.y, poly[3]])


def FindNearFeatures(request):
    dataReq = request.POST
    dataReqDict = dict(dataReq)

    city = dataReqDict['city'][0] 
    radius = dataReqDict['mapka_radius'][0] 
    lat = dataReqDict['lat'][0]
    lon = dataReqDict['lon'][0]

    shops = dataReqDict['feature_shop']                                 # all_shop          none_shop
    amenities_fun = dataReqDict['feature_amenity_fun']                  # all_fun           none_fun
    amenities_healthcare = dataReqDict['feature_amenity_healthcare']    # all_helthcare     none_helthcare
    amenities_schooling = dataReqDict['feature_amenity_schooling']      # all_schooling     none_schooling
    leisures = dataReqDict['feature_leisure']                           # all_leisure       none_leisure
    transports = dataReqDict['feature_transport']                       # all_transport     none_transport
    tourisms = dataReqDict['feature_tourism']                           # all_tourism       none_tourism
    
    all_tables = PosgreSQL_gettables()
    tempDict = {}
    for table in all_tables:
        if '_Node' in table and '_Node_' not in table and 'relation' not in table or '_Rel' in table and '_Rel_' not in table or '_Way' in table and '_Way_' not in table:
            PostgreSQL_getfeatures(table, city, radius, float(lat), float(lon), tempDict)

    tempList = []
    for key, value in dataReqDict.items():
        if key not in ['csrfmiddlewaretoken', 'city', 'mapka_radius', 'lat', 'lon']:
            for v in value:
                tempList.append(v)

    shops_all = ['mall', 'pastry', 'department_store', 'chemist', 'hairdresser', 'deli', 'kiosk',
                'florist', 'ice_cream', 'bakery', 'butcher', 'beauty', 'jewelry', 'alcohol',
                'convenience', 'coffee', 'beverages', 'seafood', 'wine', 'confectionery', 'art',
                'supermarket', 'greengrocer']
    fun_all = ['vending_machine', 'bank', 'atm', 'bar', 'fast_food', 'arts_centre',
                'cafe', 'cinema', 'nightclub', 'post_office', 'police', 'pub', 
                'restaurant', 'theatre', 'bicycle_rental']
    healthcare_all = ['pharmacy', 'dentist', 'doctors', 'clinic', 'hospital']
    schooling_all = ['library', 'kindergarten', 'school', 'college', 'university']
    leisures_all = ['fitness_centre', 'sports_centre', 'park', 'playground', 'nature_reserve']
    transports_all = ['bus', 'subway', 'train', 'stop_position', 'tram']
    tourisms_all = ['attraction', 'artwork', 'hotel', 'museum', 'viewpoint']
    
    if 'all_shop' in shops:
        i = tempList.index('all_shop')
        tempList[i:i+1] = shops_all
    if 'all_fun' in amenities_fun:
        i = tempList.index('all_fun')
        tempList[i:i+1] = fun_all
    if 'all_helthcare' in amenities_healthcare:
        i = tempList.index('all_helthcare')
        tempList[i:i+1] = healthcare_all
    if 'all_schooling' in amenities_schooling:
        i = tempList.index('all_schooling')
        tempList[i:i+1] = schooling_all
    if 'all_leisure' in leisures:
        i = tempList.index('all_leisure')
        tempList[i:i+1] = leisures_all
    if 'all_transport' in transports:
        i = tempList.index('all_transport')
        tempList[i:i+1] = transports_all
    if 'all_tourism' in tourisms:
        i = tempList.index('all_tourism')
        tempList[i:i+1] = tourisms_all

    for element in tempList:
        if re.search('none_', element):
            tempList.pop(tempList.index(element))

    for key in list(tempDict):
        if key not in tempList:
            tempDict.pop(key, None)

    translation = {'mall':'centrum handlowe', 'pastry':'cukiernia', 'department_store': 'dom towarowy', 'chemist': 'drogeria', 'hairdresser': 'fryzjer',
    'deli': 'garmażeria', 'kiosk': 'kiosk', 'florist': 'kwiaciarnia', 'ice_cream': 'lodziarnia', 'bakery': 'piekarnia', 'butcher': 'rzeźnik',
    'beauty': 'salon piękności', 'jewelry': 'sklep jubilerski', 'alcohol': 'sklep monopolowy', 'convenience': 'sklep wielobranzowy', 'coffee': 'sklep z kawa',
    'beverages': 'sklep z napojami', 'seafood': 'sklep z owocami morza', 'wine': 'sklep z winami', 'confectionery':'sklep cukierniczy',
    'art': 'sklep ze sztuka', 'supermarket': 'supermarket', 'greengrocer': 'warzywniak', 'vending_machine': 'automat vendingowy', 'bank': 'bank',
    'atm': 'bankomat', 'bar': 'bar', 'fast_food': 'fast food', 'arts_centre': 'galeria sztuki', 'cafe': 'kawiarnia', 'cinema': 'kino',
    'nightclub': 'klub nocny', 'post_office': 'poczta', 'police': 'policja', 'pub': 'pub', 'restaurant': 'restauracja', 'theatre': 'teatr',
    'bicycle_rental': 'wypozyczalnia rowerow', 'pharmacy': 'apteka', 'dentist': 'dentysta', 'doctors': 'gabinet lekarski', 'clinic': 'klinika',
    'hospital': 'szpital', 'library': 'biblioteka', 'kindergarten': 'przedszkole', 'school': 'szkola', 'college': 'uczelnia', 'university': 'uniwersytet',
    'fitness_centre': 'centrum fitness', 'sports_centre': 'ośrodek sportowy', 'park': 'park', 'playground': 'plac zabaw', 'nature_reserve': 'rezerwat przyrody',
    'bus': 'przystanek autobusowy', 'subway': 'metro', 'train': 'przystanek kolejowy', 'stop_position': 'przystanek', 'tram': 'przystanek tramwajowy',
    'attraction': 'atrakcje', 'artwork': 'dzieła sztuki', 'hotel': 'hotel', 'museum': 'muzeum', 'viewpoint': 'punkt widokowy'
    }
    for value in tempDict.values():
        for v in value:
            v[0] = translation[v[0]]

    tempDict['lat'] = lat
    tempDict['lon'] = lon
    tempDict['mapka_radius'] = radius
    return tempDict


