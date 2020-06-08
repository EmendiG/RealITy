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

def oferty_INITIATION(bd_1:str, bd_2:str):
    '''         DLA DUZYCH POROWNAN !!!  -- TWORZY NOWĄ BAZOWĄ (POROWNAWCZA) BD      '''
    mydb = connection.MySQLConnection(user=db_dane['name'], password=db_dane['password'], host=db_dane['hostname'],
                                      database=db_dane['db_name'])
    df_1 = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_1), con=mydb)
    df_2 = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_2), con=mydb)
    # df = pd.DataFrame(columns=('Price', 'Area', 'Price_per_metr', 'Latitude', 'Longitude', 'Ident', 'Typ_zabudowy',
    #                           'Rok_zabudowy', 'Liczba_pokoi', 'Max_liczba_pieter', 'Pietro', 'Parking', 'Kuchnia',
    #                           'Wlasnosc', 'Stan', 'Material', 'Okna', 'Rynek', 'Opis', 'Link', 'Miasto'))
    db_connection_str = 'mysql+pymysql://{name}:{password}@{hostname}/{db_name}'.format(**db_dane)
    db_connection = create_engine(db_connection_str).execution_options(autocommit=True)
    conn = db_connection.connect()

    gratka_arr = np.empty((0, 6), int)
    otodom_arr = np.empty((0, 6), int)
    for index, row in df_2.iterrows():
        if int(index) % 1000 == 0:
            print(f'Wprowadzam dane z db oferty_{bd_1}', index, '/', df_2.shape[0])
        gratka_arr = np.concatenate((gratka_arr, [
            [index, row['Miasto'], row['Price_per_metr'], row['Area'], row['Latitude'], row['Longitude']]]), axis=0)
    for xedni, wor in df_1.iterrows():
        if int(xedni) % 1000 == 0:
            print(f'Wprowadzam dane z db oferty_{bd_2}', xedni, '/', df_1.shape[0])
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
    df_2 = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_2), con=mydb).iloc[dobre]
    df = pd.concat([df_2, df_1]).reset_index().drop(['id', 'index', 'level_0'], axis=1)
    df.to_sql('oferty_init', con=conn)


def oferty_MERGER(bd_b, bd_p):
    '''      DLA NOWYCH MALYCH POROWNAN   (bazowa = bd_b), (porownywana = bd_p)  nadpisuje w bazowej       '''

    mydb = connection.MySQLConnection(user=db_dane['name'], password=db_dane['password'], host=db_dane['hostname'],
                                      database=db_dane['db_name'])
    df_b = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_b), con=mydb)
    df_p = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_p), con=mydb)
    db_connection = connect_to_MYSQL()
    conn = db_connection.connect()

    gratka_arr = np.empty((0, 6), int)
    otodom_arr = np.empty((0, 6), int)
    for index, row in df_p.iterrows():
        if int(index) % 1000 == 0:
            print(f'Wprowadzam dane z db oferty_{bd_p}', index, '/', df_p.shape[0])
        gratka_arr = np.concatenate((gratka_arr, [
            [index, row['Miasto'], row['Price_per_metr'], row['Area'], row['Latitude'], row['Longitude']]]), axis=0)
    for xedni, wor in df_b.iterrows():
        if int(xedni) % 1000 == 0:
            print(f'Wprowadzam dane z db oferty_{bd_b}', xedni, '/', df_b.shape[0])
        otodom_arr = np.concatenate((otodom_arr, [
            [xedni, wor['Miasto'], wor['Price_per_metr'], wor['Area'], wor['Latitude'], wor['Longitude']]]), axis=0)

    for row in gratka_arr:
        spr = 0
        index = int(row[0])
        if index%1000 ==0:
            print(f'Sprawdzam dane z dbs {bd_b} i {bd_p}', index, '/', gratka_arr.shape[0])
        for wor in otodom_arr:
            if row[1] == wor[1]:
                if row[2] == wor[2] and row[3] == wor[3]:
                    if abs(float(wor[4]) - float(row[4])) < 0.001 and abs(float(wor[5]) - float(row[5])) < 0.001:
                        spr = 1
                        print(row[0])
        if spr == 0:
            df_p.iloc[index].drop('index')
            df_p.iloc[index].to_sql('oferty_init', if_exists='append', con=conn)

    #dobre = [row[0] for row in gratka_arr if row[0] not in wyniki]
    #df_p = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_p), con=mydb).iloc[dobre]
    #df = pd.concat([df_p, df_b]).reset_index().drop(['id', 'index'], axis=1)
    #df.to_sql('oferty_merged', con=conn)