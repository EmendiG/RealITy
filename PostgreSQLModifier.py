import pandas as pd
import geopandas as gpd
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Text, MetaData, Float
import numpy as np
import time
import OpenStreetMapOverpass


db_dane = {'name': 'RealITy', 'password': 'Reality1!', 'hostname': '127.0.0.1', 'db_name': 'realestate_zero'}


class Strona:
    def __init__(self, serwis):
        self.serwis = serwis

    def wybor(self):
        if self.serwis == 'otodom':
            import otodompy as serwer
            return serwer
        elif self.serwis == 'gratka':
            import gratkapy as serwer
            return serwer
        elif self.serwis == 'morizon':
            import morizonpy as serwer
            return serwer

    def sqldbMaker(self):
        conn = PostgreSQL_connectSQLalchemy()
        metadata = MetaData()
        users = Table('oferty_{}'.format(self.serwis), metadata,
                      # Column('index', Integer, autoincrement=True, primary_key=True),
                      Column('Price', Float),
                      Column('Area', Float),
                      Column('Price_per_metr', Float),
                      Column('Latitude', Float),
                      Column('Longitude', Float),
                      Column('Ident', Text),
                      Column('Typ_zabudowy', Text),
                      Column('Rok_zabudowy', Text),
                      Column('Liczba_pokoi', Text),
                      Column('Max_liczba_pieter', Text),
                      Column('Pietro', Text),
                      Column('Parking', Text),
                      Column('Kuchnia', Text),
                      Column('Wlasnosc', Text),
                      Column('Stan', Text),
                      Column('Material', Text),
                      Column('Okna', Text),
                      Column('Rynek', Text),
                      Column('Opis', Text),
                      Column('Link', Text),
                      Column('Miasto', Text),
                      Column('ExtractionTime', Text),
                      )
        metadata.create_all(conn)
        return users


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

def PosgreSQL_getcolumns(tablename):
    cursor = PostgreSQL_connectPsycopg2().cursor()
    cursor.execute(f"""Select * FROM "{tablename}" LIMIT 0""")
    colnames = [desc[0] for desc in cursor.description]
    return colnames

def oferty_Merger(db_base: str, db_comp: str, db_nowa: str):
    '''
       CHECK 2 DBs (bd_base + bd_comp) IF RECORDS DON'T OVERLAP THEN MERGE THEM INTO (db_nowa)
       IF (db_nowa) EXISTS THEN merging result of DBs (db_base + db_comp + db_nowa) IS APPENDED TO (db_nowa)
    '''

    start = time.time()
    con = PostgreSQL_connectPsycopg2()
    conn = PostgreSQL_connectSQLalchemy()
    df_get = pd.read_sql_query('SELECT * FROM oferty_{}'.format(db_comp), con=conn)

    for miasto in df_get['Miasto'].unique().tolist():
        arr_comp = np.empty((0, 5), float)
        arr_base = np.empty((0, 5), float)
        if miasto:
            df_base = pd.read_sql_query("""SELECT * FROM oferty_{} WHERE "Miasto"='{}'""".format(db_base, miasto),
                                        con=conn)
            df_comp = pd.read_sql_query("""SELECT * FROM oferty_{} WHERE "Miasto"='{}'""".format(db_comp, miasto),
                                        con=conn)

            for index, row in df_comp.iterrows():
                if int(index) % 1000 == 0:
                    print(f'Wprowadzam dane z db oferty_{db_comp}', index, '/', df_comp.shape[0],
                          'do tymczasowego array dla', miasto)
                arr_comp = np.concatenate(
                    (arr_comp, [[index, row['Price_per_metr'], row['Area'], row['Latitude'], row['Longitude']]]),
                    axis=0)
            for xedni, wor in df_base.iterrows():
                if int(xedni) % 1000 == 0:
                    print(f'Wprowadzam dane z db oferty_{db_base}', xedni, '/', df_base.shape[0],
                          'do tymczasowego array dla', miasto)
                arr_base = np.concatenate(
                    (arr_base, [[xedni, wor['Price_per_metr'], wor['Area'], wor['Latitude'], wor['Longitude']]]),
                    axis=0)

            wyniki = []
            for row in arr_comp:
                index = int(row[0])
                if index % 1000 == 0:
                    print(f'Sprawdzam dane z dbs {db_base} i {db_comp}', index, '/', arr_comp.shape[0])
                for wor in arr_base:
                    if row[1] == wor[1] and row[2] == wor[2] and abs(float(wor[3]) - float(row[3])) < 0.001 \
                            and abs(float(wor[4]) - float(row[4])) < 0.001:
                        wyniki.append(row[0])

            dobre = [row[0] for row in arr_comp if row[0] not in wyniki]
            print(f'Wprowadzam dane do db {db_nowa} = {len(dobre)} nowych rekordow')
            df_comp = \
            pd.read_sql("""SELECT * FROM oferty_{} WHERE "Miasto"='{}'""".format(db_comp, miasto), con=conn).iloc[dobre]
            df_base = pd.read_sql("""SELECT * FROM oferty_{}""".format(db_base), con=conn)
            df_comp_len = df_comp.shape[0]

            tabela = PosgreSQL_gettables()
            if f'oferty_{db_nowa}' not in tabela:
                df_base = df_base.reset_index(drop=True)
                Strona(db_nowa).sqldbMaker()
                df_base.to_sql(f'oferty_{db_nowa}', if_exists='replace', con=conn)
                df_base_max = df_base.shape[0]
            else:
                df_base = pd.read_sql('SELECT * FROM oferty_{}'.format(db_nowa), con=conn)
                df_base_max = df_base.shape[0]

            df_comp["index"] = range(df_base_max, df_base_max + df_comp_len)
            df_comp = df_comp.set_index("index")


            tabela = PosgreSQL_gettables()
            if f'oferty_{db_nowa}' not in tabela:
                df_base = df_base.reset_index(drop=True)  # .drop('level_0', axis=1)
                Strona(db_nowa).sqldbMaker()
                df_base.to_sql(f'oferty_{db_nowa}', if_exists='replace', con=conn)

            df_comp.to_sql(f'oferty_{db_nowa}', con=conn, if_exists='append')

            cursor = PostgreSQL_connectPsycopg2().cursor()
            cursor.execute(f"""Select * FROM "oferty_{db_nowa}" LIMIT 0""")
            colnames = [desc[0] for desc in cursor.description]
            if 'level_0' in colnames:
                cursor.execute(f"""ALTER TABLE "oferty_{db_nowa}" DROP COLUMN level_0""")
                con.commit()
    print(time.time() - start)

def PosgreSQL_oferty_Merger_assignDistricts(miasto, db_nowa:str="oferty_merged"):
    # Adjust existing table that contains offers and assign proper district name according to geographical coordinates
    city_districts = gpd.read_file(f'districts/{miasto}.json')

    conn = PostgreSQL_connectSQLalchemy()
    df_oferty_merged = pd.read_sql(f'{db_nowa}', con=conn)
    gdf_oferty_merged = gpd.GeoDataFrame(df_oferty_merged, geometry=gpd.points_from_xy(df_oferty_merged.Longitude,
                                                                                       df_oferty_merged.Latitude))
    gdf_oferty_miasto = gdf_oferty_merged.loc[gdf_oferty_merged['Miasto'] == miasto]

    howmany = round(len(gdf_oferty_miasto) / 10)
    print(miasto)
    for n, oferta in enumerate(gdf_oferty_miasto.iterrows()):
        if n % (howmany) == 0:
            print(n / howmany * 10, '%')
        for dzielnica in city_districts.iterrows():
            if dzielnica[1]['geometry'].contains(oferta[1]['geometry']):
                df_oferty_merged.loc[oferta[0], 'Dzielnica'] = dzielnica[1]['name']
    df_oferty_merged.drop('geometry', axis=1).to_sql(f'{db_nowa}', if_exists='replace', con=conn, index=False)


def osmApi_DataFrame_ToSQL(miasto: str, feature: str, type: str, autoselection: bool = True):
    """
    Send DataFrame to PostgreSQL server

    :param miasto: str
    :param feature: str
            Mandatory str:
                - Amenity           (N)
                - Tourism           (N)
                - Leisure           (N, W, R, NoW)
                - Shop              (N, NoW)
                - Public_transport  (N)
    :param type: str
            Mandatory str:
                - Node          (N)
                - Way           (W)
                - Rel           (R)
                - NodeOfWay     (NoW)
    :param autoselection: bool
            True    -   get features that are prepared
            False   -   get features that you wish
    :param onepoint: bool , onepoint: bool = False
            True    -   (works only with ways) get only one point of all ways (lon, lat)
            False   -   get all points of ways (geom: Polygon)

    :return: -> send DataFrame to SQL server
    """
    global feature_df
    print(miasto)
    conn = PostgreSQL_connectSQLalchemy()

    if feature == 'Amenity' and type == 'Node':
        feature_df = OpenStreetMapOverpass.MapFeatures(miasto, feature, type, autoselection
                                                       ).osmApi_getAmenities_parseToDataFrame_nodes()
    elif feature == 'Tourism' and type == 'Node':
        feature_df = OpenStreetMapOverpass.MapFeatures(miasto, feature, type, autoselection
                                                       ).osmApi_getFeature_parseToDataFrame_nodes()
    elif feature == 'Leisure' and type == 'Node':
        feature_df = OpenStreetMapOverpass.MapFeatures(miasto, feature, type, autoselection
                                                       ).osmApi_getFeature_parseToDataFrame_nodes()
    elif feature == 'Leisure' and type == 'NodeOfWay':
        feature_df = OpenStreetMapOverpass.MapFeatures(miasto, feature, type, autoselection
                                                       ).osmApi_getFeature_parseToDataFrame_nodeOfway()
    elif feature == 'Leisure' and type == 'Rel':
        feature_df = OpenStreetMapOverpass.MapFeatures(miasto, feature, type, autoselection
                                                       ).osmApi_getFeature_parseToDataFrame_rels()
    elif feature == 'Leisure' and type == 'Way':
        feature_df = OpenStreetMapOverpass.MapFeatures(miasto, feature, type, autoselection
                                                       ).osmApi_getFeature_parseToDataFrame_ways()
    elif feature == 'Shop' and type == 'Node':
        feature_df = OpenStreetMapOverpass.MapFeatures(miasto, feature, type, autoselection
                                                       ).osmApi_getFeature_parseToDataFrame_nodes()
    elif feature == 'Shop' and type == 'NodeOfWay':
        feature_df = OpenStreetMapOverpass.MapFeatures(miasto, feature, type, autoselection
                                                       ).osmApi_getFeature_parseToDataFrame_nodeOfway()
    elif feature == 'Public_transport' and type == 'Node':
        feature_df = OpenStreetMapOverpass.MapFeatures(miasto, feature, type, autoselection
                                                       ).osmApi_getFeature_parseToDataFrame_nodes()

    if 'Geometry' in feature_df:  # isinstance doesn't work cuz gdf==df
        feature_df.set_index('Ident', inplace=True)  # Delete this funky 'index' column
        feature_df.postgis.to_postgis(table_name=f'{feature}_{type}', con=conn, if_exists='append', geometry='Geometry')
    else:
        feature_df.set_index('Ident', inplace=True)  # Delete this funky 'index' column
        feature_df.to_sql(f'{feature}_{type}', con=conn, if_exists='append')

    # TODO: Wyjebać te if pify (wszystko kurwa na zszywkach sie trzyma - REFACTOR CODE !!)


def osmApi_DataFrame_FromSQL(feature, type):
    conn = PostgreSQL_connectSQLalchemy()
    tabela = PosgreSQL_gettables()
    if f'{feature}_{type}' in tabela:
        df_base = pd.read_sql(f"""SELECT "Ident" FROM "{feature}_{type}" """, con=conn)['Ident'].values.tolist()
    else:
        df_base = []
    return df_base


