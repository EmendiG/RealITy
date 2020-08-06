import pandas as pd
import geopandas as gpd
import time
import concurrent.futures
from shapely import wkb
import PostgreSQLModifier
from collections import defaultdict
from itertools import chain

miasta = ['warszawa', 'krakow', 'lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin', 'bialystok']


def PostgreSQL_getrelations_WayRelmultprocess_checking(arr_feature_miasto, arr_oferty_miasto, start, end, miasto, num_of_process):
    df_merged = pd.DataFrame(columns=['Ident_oferty', 'Ident_feature', 'Miasto'])
    i = 0
    if end - start > 10:
        howmanymore = round((end - start)/10)
    else:
        howmanymore = 1
    approximation = (end - start)
    for n, point in enumerate(arr_oferty_miasto):
        temp_relation_dict = defaultdict(list)
        if start <= n <= end:
            if n%howmanymore == 0:
                print(f'Process {num_of_process} is {round((n-start)/approximation*100)} % done')
            for poly in arr_feature_miasto:
                if poly[2].geom_type == 'Polygon':
                    if poly[2].exterior.distance(point[22]) < 0.004:
                        df_merged.loc[i] = [point[5], poly[0], miasto]
                        i += 1
                elif poly[2].geom_type == 'MultiPolygon':
                    for r in poly[2]:
                        if r.exterior.distance(point[22]) < 0.004:
                            if point[6] not in temp_relation_dict.keys():
                                temp_relation_dict[point[5]].append(poly[0])
                                df_merged.loc[i] = [point[5], poly[0], miasto]
                                i += 1
                            elif poly[0] not in temp_relation_dict[point[5]]:
                                temp_relation_dict[point[5]].append(poly[0])
                                df_merged.loc[i] = [point[5], poly[0], miasto]
                                i += 1
    return df_merged

def PostgreSQL_getrelations_Nodemultprocess_checking(arr_feature_miasto, arr_oferty_miasto, start, end, miasto, num_of_process):
    df_merged = pd.DataFrame(columns=['Ident_oferty', 'Ident_feature', 'Miasto'])
    i = 0
    if end - start > 10:
        howmanymore = round((end - start)/10)
    else:
        howmanymore = 1
    approximation = (end - start)
    print(f'Process {num_of_process} is ready')
    for n, point in enumerate(arr_oferty_miasto):
        if start <= n <= end:
            if n % howmanymore == 0:
                print(f'Process {num_of_process} is {round((n - start) / approximation * 100)} % done')
            for node in arr_feature_miasto:
                if point[22].distance(node[7]) < 0.004:
                    df_merged.loc[i] = [point[5], node[0], miasto]
                    i += 1
    return df_merged


def PostgreSQL_getrelations_WayRelmultprocess(miasto:str, tabletolookin:str, tablecompared:str):
    conn = PostgreSQLModifier.PostgreSQL_connectSQLalchemy()
    df_oferty_merged = pd.read_sql(sql=tablecompared, con=conn)
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
        f1 = executor.submit(PostgreSQL_getrelations_WayRelmultprocess_checking, arr_feature_warszawa, arr_oferty_warszawa,
                             0, len(arr_feature_warszawa) / 4, miasto, 1)
        f2 = executor.submit(PostgreSQL_getrelations_WayRelmultprocess_checking, arr_feature_warszawa, arr_oferty_warszawa,
                             len(arr_feature_warszawa) / 4, len(arr_feature_warszawa) / 2, miasto, 2)
        f3 = executor.submit(PostgreSQL_getrelations_WayRelmultprocess_checking, arr_feature_warszawa, arr_oferty_warszawa,
                             len(arr_feature_warszawa) / 2, 3 * len(arr_feature_warszawa) / 4, miasto, 3)
        f4 = executor.submit(PostgreSQL_getrelations_WayRelmultprocess_checking, arr_feature_warszawa, arr_oferty_warszawa,
                             3 * len(arr_feature_warszawa) / 4, len(arr_feature_warszawa), miasto, 4)
    timeend = time.time()
    print(timeend - timestart)
    return f1.result().append(f2.result()).append(f3.result()).append(f4.result()).reset_index(drop=True)

def PostgreSQL_getrelations_Nodemultprocess(miasto:str, tabletolookin:str, tablecompared:str):
    conn = PostgreSQLModifier.PostgreSQL_connectSQLalchemy()
    df_oferty_merged = pd.read_sql(sql=tablecompared, con=conn)
    df_feature = pd.read_sql(sql=tabletolookin, con=conn)

    gdf_oferty_merged = gpd.GeoDataFrame(df_oferty_merged, geometry=gpd.points_from_xy(df_oferty_merged.Longitude,
                                                                                       df_oferty_merged.Latitude))
    gdf_feature = gpd.GeoDataFrame(df_feature, geometry=gpd.points_from_xy(df_feature.Longitude,
                                                                            df_feature.Latitude))

    gdf_oferty_miasto = gdf_oferty_merged.loc[gdf_oferty_merged['Miasto'] == miasto]
    arr_oferty_miasto = gdf_oferty_miasto.to_numpy()
    gdf_feature_miasto = gdf_feature.loc[gdf_feature['Miasto'] == miasto]
    arr_feature_miasto = gdf_feature_miasto.to_numpy()

    timestart = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        f1 = executor.submit(PostgreSQL_getrelations_Nodemultprocess_checking, arr_feature_miasto, arr_oferty_miasto,
                             0, len(arr_oferty_miasto) / 4, miasto, 1)
        f2 = executor.submit(PostgreSQL_getrelations_Nodemultprocess_checking, arr_feature_miasto, arr_oferty_miasto,
                             len(arr_oferty_miasto) / 4, len(arr_oferty_miasto) / 2, miasto, 2)
        f3 = executor.submit(PostgreSQL_getrelations_Nodemultprocess_checking, arr_feature_miasto, arr_oferty_miasto,
                             len(arr_oferty_miasto) / 2, 3 * len(arr_oferty_miasto) / 4, miasto, 3)
        f4 = executor.submit(PostgreSQL_getrelations_Nodemultprocess_checking, arr_feature_miasto, arr_oferty_miasto,
                             3 * len(arr_oferty_miasto) / 4, len(arr_oferty_miasto), miasto, 4)
    timeend = time.time()
    print(timeend - timestart)
    return f1.result().append(f2.result()).append(f3.result()).append(f4.result()).reset_index(drop=True)


def PostgreSQL_getrelations(tablecompared:str="oferty_merged"):
    """ All tables sourced from openstreetmap are compared with a table that contains offers (default = oferty_merged) """
    # It takes 5 hours to finish ALL calculations :/
    all_tables = PostgreSQLModifier.PosgreSQL_gettables()
    for table in all_tables:
        if '_Node' in table and '_Node_' not in table:
            for miasto in miasta:
                print(table, miasto)
                returneddataframe = PostgreSQL_getrelations_Nodemultprocess(miasto, table, tablecompared)
                conn = PostgreSQLModifier.PostgreSQL_connectSQLalchemy()
                returneddataframe.to_sql(f'{table}_relation', con=conn, if_exists='append', index=False)
        elif 'Rel' in table or '_Way' in table and '_Way_' not in table and '_Rel_' not in table:
            for miasto in miasta:
                print(table, miasto)
                returneddataframe = PostgreSQL_getrelations_WayRelmultprocess(miasto, table, tablecompared)
                conn = PostgreSQLModifier.PostgreSQL_connectSQLalchemy()
                returneddataframe.to_sql(f'{table}_relation', con=conn, if_exists='append', index=False)



def PostgreSQL_getfeatures_multprocess_checking(arr_Shop_Node_miasto, arr_Shop_Node_relation_miasto, start, end, num_of_process):

    temp_dict = defaultdict(list)
    howmanymore = round((end - start) / 10)
    approximation = end - start

    for n, relation in enumerate(arr_Shop_Node_relation_miasto):
        if start <= n <= end:
            if n % howmanymore == 0:
                print(f'Process {num_of_process} is {round((n - start) / approximation * 100)} % done')
            for node in arr_Shop_Node_miasto:
                if relation[1] == node[0]:
                    temp_dict[relation[0]].append(node[1])
    return temp_dict


def PostgreSQL_getfeatures_multprocess(miasto:str, tabletolookin:str, df_oferty_merged, df_feature, df_feature_relation):

    df_oferty_miasto = df_oferty_merged.loc[df_oferty_merged['Miasto'] == miasto]
    df_Shop_Node_miasto = df_feature.loc[df_feature['Miasto'] == miasto]
    arr_Shop_Node_miasto = df_Shop_Node_miasto.to_numpy()
    df_Shop_Node_relation_miasto = df_feature_relation.loc[df_feature_relation['Miasto'] == miasto]
    arr_Shop_Node_relation_miasto = df_Shop_Node_relation_miasto.to_numpy()

    timestart = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        f1 = executor.submit(PostgreSQL_getfeatures_multprocess_checking, arr_Shop_Node_miasto, arr_Shop_Node_relation_miasto,
                             0, len(arr_Shop_Node_relation_miasto) / 4, 1)
        f2 = executor.submit(PostgreSQL_getfeatures_multprocess_checking, arr_Shop_Node_miasto, arr_Shop_Node_relation_miasto,
                             len(arr_Shop_Node_relation_miasto) / 4, len(arr_Shop_Node_relation_miasto) / 2, 2)
        f3 = executor.submit(PostgreSQL_getfeatures_multprocess_checking, arr_Shop_Node_miasto, arr_Shop_Node_relation_miasto,
                             len(arr_Shop_Node_relation_miasto) / 2, 3 * len(arr_Shop_Node_relation_miasto) / 4, 3)
        f4 = executor.submit(PostgreSQL_getfeatures_multprocess_checking, arr_Shop_Node_miasto, arr_Shop_Node_relation_miasto,
                             3 * len(arr_Shop_Node_relation_miasto) / 4, len(arr_Shop_Node_relation_miasto), 4)
    print(time.time() - timestart)

    temp_dict = defaultdict(list)
    for k, v in chain(f1.result().items(), f2.result().items(), f3.result().items(), f4.result().items()):
        for item in v:
            temp_dict[k].append(item)

    keys = list(temp_dict.keys())
    values = list(temp_dict.values())
    for indeks, row in df_oferty_miasto.iterrows():
        if row['Ident'] in temp_dict.keys():
            df_oferty_merged[tabletolookin].iloc[indeks] = values[keys.index(row['Ident'])]
            # df_oferty_merged.loc.__setitem__((indeks, tabletolookin), values[keys.index(row['Ident'])])
    return df_oferty_merged

def PostgreSQL_getfeatures(tabletolookin:str, tablecompared:str="oferty_merged"):

    conn = PostgreSQLModifier.PostgreSQL_connectSQLalchemy()
    all_tables = PostgreSQLModifier.PosgreSQL_gettables()


    if f'{tablecompared}_features' in all_tables:
        df_oferty_merged = pd.read_sql(sql=f'{tablecompared}_features', con=conn)
        columnsnames = PostgreSQLModifier.PosgreSQL_getcolumns(f'{tablecompared}_features')
        if tabletolookin not in columnsnames:
            df_oferty_merged[tabletolookin] = ''
    else:
        df_oferty_merged = pd.read_sql(sql=tablecompared, con=conn)
        df_oferty_merged[tabletolookin] = ''
    df_feature_relation = pd.read_sql(sql=f"{tabletolookin}_relation", con=conn)
    df_feature = pd.read_sql(sql=tabletolookin, con=conn)
    for miasto in miasta:
        print(tabletolookin, miasto)
        df_oferty_merged = PostgreSQL_getfeatures_multprocess(miasto, tabletolookin, df_oferty_merged, df_feature,
                                                              df_feature_relation)

    df_oferty_merged.to_sql(f'{tablecompared}_features', con=conn, if_exists='replace', index=False)


if __name__ == '__main__':

    all_tables = PostgreSQLModifier.PosgreSQL_gettables()
    for table in all_tables:
        if '_Node' in table  and '_Node_' not in table and 'relation' not in table or'_Rel' in table and '_Rel_' not in table or '_Way' in table and '_Way_' not in table:
            PostgreSQL_getfeatures(table)