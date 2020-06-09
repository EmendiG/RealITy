import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
from mysql.connector import (connection)
import numpy as np

db_dane = {'name': 'RealITy', 'password': 'Reality1!', 'hostname': '127.0.0.1', 'db_name': 'realestate_zero'}

def connect_to_MYSQL():
    db_connection_str = 'mysql+pymysql://{name}:{password}@{hostname}/{db_name}'.format(**db_dane)
    db_connection = create_engine(db_connection_str).execution_options(autocommit=True)
    return db_connection

def oferty_db_MERGER(bd_base:str, bd_comp:str, db_nowa:str):
    '''
    CHECK 2 DBs (bd_base + bd_comp) IF RECORDS DON'T OVERLAP THEN MERGE INTO (db_nowa)
    IF (db_nowa) EXISTS THEN merging result of DBs (bd_base + bd_comp) IS APPENDED TO (db_nowa)
    '''
    mydb = connection.MySQLConnection(user=db_dane['name'], password=db_dane['password'], host=db_dane['hostname'],
                                      database=db_dane['db_name'], auth_plugin='mysql_native_password')
    df_base = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_base), con=mydb)
    df_comp = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_comp), con=mydb)
    db_connection_str = 'mysql+pymysql://{name}:{password}@{hostname}/{db_name}'.format(**db_dane)
    db_connection = create_engine(db_connection_str).execution_options(autocommit=True)
    conn = db_connection.connect()

    gratka_arr = np.empty((0, 6), int)
    otodom_arr = np.empty((0, 6), int)
    for index, row in df_comp.iterrows():
        if int(index) % 1000 == 0:
            print(f'Wprowadzam dane z db oferty_{bd_base}', index, '/', df_comp.shape[0])
        gratka_arr = np.concatenate((gratka_arr, [
            [index, row['Miasto'], row['Price_per_metr'], row['Area'], row['Latitude'], row['Longitude']]]), axis=0)
    for xedni, wor in df_base.iterrows():
        if int(xedni) % 1000 == 0:
            print(f'Wprowadzam dane z db oferty_{bd_comp}', xedni, '/', df_base.shape[0])
        otodom_arr = np.concatenate((otodom_arr, [
            [xedni, wor['Miasto'], wor['Price_per_metr'], wor['Area'], wor['Latitude'], wor['Longitude']]]), axis=0)

    wyniki = []
    for row in gratka_arr:
        index = int(row[0])
        if index % 1000 == 0:
            print('Sprawdzam dane z dbs gratka i otodom', index, '/', gratka_arr.shape[0])
        for wor in otodom_arr:
            if row[1] == wor[1]:
                if row[2] == wor[2] and row[3] == wor[3]:
                    if abs(float(wor[4]) - float(row[4])) < 0.001 and abs(float(wor[5]) - float(row[5])) < 0.001:
                        wyniki.append(str(index))

    dobre = [row[0] for row in gratka_arr if row[0] not in wyniki]
    print(f'Wprowadzam dane do db {db_nowa}')
    df_comp = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_comp), con=mydb).iloc[dobre].drop(['index'],
                            axis=1).reset_index(drop=True)
    df_base_max = df_base.shape[0]
    df_comp_len = df_comp.shape[0]
    df_comp["index"] = range(df_base_max, df_base_max + df_comp_len)
    df_comp = df_comp.set_index("index")
    cursor = mydb.cursor()
    cursor.execute("USE realestate_zero")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    tabela = [tab[0] for tab in tables]
    if f'oferty_{db_nowa}' not in tabela:
        df_base = df_base.reset_index(drop=True).drop('index', axis=1)
        df_base.to_sql(f'oferty_{db_nowa}',index_label='index', index=True, con=conn)
    df_comp.to_sql(f'oferty_{db_nowa}', con=conn, if_exists='append')

