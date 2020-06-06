import mysql.connector
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import pymysql

db_dane = {'name':'RealITy', 'password':'RealITy1!', 'hostname':'127.0.0.1', 'db_name':'realestate_zero'}

def sqlite():
    conn = sqlite3.connect('nieruchomosci.db')
    sql_query = pd.read_sql_query('''SELECT * FROM oferty ''', conn)
    sql_query2 = pd.read_sql_query('''SELECT * FROM oferty2 ''', conn)
    df = pd.DataFrame(sql_query)
    df2 = pd.DataFrame(sql_query2)

def db_connection():
    db_connection_str = 'mysql+pymysql://{name}:{password}@{hostname}/{db_name}'.format(**db_dane)
    db_connection = create_engine(db_connection_str)

df2.to_sql(name='oferty2', con=db_connection)

