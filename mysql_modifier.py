import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
from mysql.connector import (connection)
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Text, MetaData, Float
import numpy as np
import time

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

    def mysql_dbMaker(self):
        #db_connection = mysql_modifier.connect_to_MYSQL()
        conn = connect_to_MYSQL()
        metadata = MetaData()
        users = Table('oferty_{}'.format(self.serwis), metadata,
                      Column('index', Integer, autoincrement=True),
                      Column('Price', Integer),
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
                      )
        metadata.create_all(conn)
        return users


def connect_to_MYSQL():
    db_connection_str = 'mysql+pymysql://{name}:{password}@{hostname}/{db_name}'.format(**db_dane)
    db_connection = create_engine(db_connection_str).execution_options(autocommit=True)
    return db_connection.connect()

def oferty_Merger(bd_base:str, bd_comp:str, db_nowa:str):
    '''
       CHECK 2 DBs (bd_base + bd_comp) IF RECORDS DON'T OVERLAP THEN MERGE THEM INTO (db_nowa)
       IF (db_nowa) EXISTS THEN merging result of DBs (bd_base + bd_comp) IS APPENDED TO (db_nowa)
    '''
    start = time.time()

    mydb = connection.MySQLConnection(user=db_dane['name'], password=db_dane['password'], host=db_dane['hostname'],
                                      database=db_dane['db_name'], auth_plugin='mysql_native_password')

    conn = connect_to_MYSQL()
    df_get = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_comp), con=mydb)
    for miasto in df_get['Miasto'].unique().tolist():
        arr_comp = np.empty((0, 5), float)
        arr_base = np.empty((0, 5), float)
        if miasto:
            df_base = pd.read_sql('SELECT * FROM oferty_{} WHERE Miasto="'"{}"'"'.format(bd_base, miasto), con=mydb)
            df_comp = pd.read_sql('SELECT * FROM oferty_{} WHERE Miasto="'"{}"'"'.format(bd_comp, miasto), con=mydb)

            for index, row in df_comp.iterrows():
                if int(index) % 1000 == 0:
                    print(f'Wprowadzam dane z db oferty_{bd_comp}', index, '/', df_comp.shape[0],
                          'do tymczasowego array dla', miasto)
                arr_comp = np.concatenate(
                    (arr_comp, [[index, row['Price_per_metr'], row['Area'], row['Latitude'], row['Longitude']]]),
                    axis=0)
            for xedni, wor in df_base.iterrows():
                if int(xedni) % 1000 == 0:
                    print(f'Wprowadzam dane z db oferty_{bd_base}', xedni, '/', df_base.shape[0],
                          'do tymczasowego array dla', miasto)
                arr_base = np.concatenate(
                    (arr_base, [[xedni, wor['Price_per_metr'], wor['Area'], wor['Latitude'], wor['Longitude']]]),
                    axis=0)

            wyniki = []
            for row in arr_comp:
                index = int(row[0])
                if index % 1000 == 0:
                    print(f'Sprawdzam dane z dbs {bd_base} i {bd_comp}', index, '/', arr_comp.shape[0])
                for wor in arr_base:
                    if row[1] == wor[1] and row[2] == wor[2] and abs(float(wor[3]) - float(row[3])) < 0.001 \
                            and abs(float(wor[4]) - float(row[4])) < 0.001:
                        wyniki.append(row[0])

            dobre = [row[0] for row in arr_comp if row[0] not in wyniki]
            print(f'Wprowadzam dane do db {db_nowa} = {len(dobre)} nowych rekordow')
            df_comp = pd.read_sql('SELECT * FROM oferty_{} WHERE Miasto="'"{}"'"'.format(bd_comp, miasto), con=mydb).iloc[dobre]
            df_base = pd.read_sql('SELECT * FROM oferty_{}'.format(bd_base), con=mydb)
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
                df_base = df_base.reset_index(drop=True)  # .drop('level_0', axis=1)
                Strona(db_nowa).mysql_dbMaker()
                df_base.to_sql(f'oferty_{db_nowa}', if_exists='replace', con=conn)
            df_comp.to_sql(f'oferty_{db_nowa}', con=conn, if_exists='append')

            mydb.reconnect()
            cursor = mydb.cursor()
            cursor.execute("USE realestate_zero")
            cursor.execute(f'DESCRIBE oferty_{db_nowa}')
            columns = cursor.fetchall()
            columna = [col[0] for col in columns]
            if 'level_0' in columna:
                cursor.execute(f'ALTER TABLE oferty_{db_nowa} DROP COLUMN level_0')
    end = time.time()
    print(end - start)
