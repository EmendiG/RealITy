import pandas as pd
import geopandas as gpd
import time
import concurrent.futures
import psycopg2
from sqlalchemy import create_engine
from shapely import wkb
import PostgreSQLModifier

miasta = ['warszawa', 'krakow', 'lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin', 'bialystok']


def PostgreSQL_getrelations_checking(arr_feature_warszawa, arr_oferty_warszawa, start, end, miasto, num_of_process):
    df_merged = pd.DataFrame(columns=['Ident_feature', 'Ident_oferty', 'Miasto'])
    i = 0
    howmanymore = round((end - start)/10)
    approximation = (end - start)
    for n, poly in enumerate(arr_feature_warszawa):
        if start <= n <= end:
            if n%howmanymore == 0:
                print(f'Process {num_of_process} is {round((n-start)/approximation*100)} % done')
            for point in arr_oferty_warszawa:
                if poly[2].exterior.distance(point[23]) < 0.004:
                    df_merged.loc[i] = [point[6], poly[0], miasto]
                    i += 1
    return df_merged


def PostgreSQL_getrelations(miasto, tabletolookin):
    conn = PostgreSQLModifier.PostgreSQL_connectSQLalchemy()
    df_oferty_merged = pd.read_sql(sql="oferty_merged", con=conn)
    df_feature = pd.read_sql(sql=tabletolookin, con=conn)
    df_feature['Geometry'] = df_feature['Geometry'].apply(lambda x: wkb.loads(x, hex=True))
    gdf_oferty_merged = gpd.GeoDataFrame(df_oferty_merged, geometry=gpd.points_from_xy(df_oferty_merged.Longitude,
                                                                                       df_oferty_merged.Latitude))
    gdf_oferty_warszawa = gdf_oferty_merged.loc[gdf_oferty_merged['Miasto'] == miasto]
    arr_oferty_warszawa = gdf_oferty_warszawa.to_numpy()
    df_feature_warszawa = df_feature.loc[df_feature['Miasto'] == miasto]
    arr_feature_warszawa = df_feature_warszawa.to_numpy()

    timestart = time.time()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        f1 = executor.submit(PostgreSQL_getrelations_checking, arr_feature_warszawa, arr_oferty_warszawa, 0,
                             len(arr_feature_warszawa) / 4, miasto, 1)
        f2 = executor.submit(PostgreSQL_getrelations_checking, arr_feature_warszawa, arr_oferty_warszawa,
                             len(arr_feature_warszawa) / 4, len(arr_feature_warszawa) / 2, miasto, 2)
        f3 = executor.submit(PostgreSQL_getrelations_checking, arr_feature_warszawa, arr_oferty_warszawa,
                             len(arr_feature_warszawa) / 2, 3 * len(arr_feature_warszawa) / 4, miasto, 3)
        f4 = executor.submit(PostgreSQL_getrelations_checking, arr_feature_warszawa, arr_oferty_warszawa,
                             3 * len(arr_feature_warszawa) / 4, len(arr_feature_warszawa), miasto, 4)
    timeend = time.time()
    print(timeend - timestart)
    return f1.result().append(f2.result()).append(f3.result()).append(f4.result()).reset_index(drop=True)

# for tables in PostgreSQLModifier.PosgreSQL_gettables():
#    print(tables)


if __name__ == '__main__':
    for table in PostgreSQLModifier.PosgreSQL_gettables():
        if '_Way' in table: # or 'Rel' in table:
            for miasto in miasta:
                returneddataframe = PostgreSQL_getrelations(miasto, table)
                conn = PostgreSQLModifier.PostgreSQL_connectSQLalchemy()
                returneddataframe.to_sql(f'{table}_relation', con=conn, if_exists='append', index=False)
