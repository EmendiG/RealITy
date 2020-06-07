import csv
import slownik
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Text, MetaData, Float

serwis = 'otodom'  # 'gratka', 'otodom'

if serwis == 'otodom':
    import otodompy as serwer
elif serwis == 'gratka':
    import gratkapy as serwer

miasta = ['warszawa', 'krakow','lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin', 'bialystok']


db_dane = {'name':'RealITy', 'password':'Reality1!', 'hostname':'127.0.0.1', 'db_name':'realestate_zero'}
db_connection_str = 'mysql+pymysql://{name}:{password}@{hostname}/{db_name}'.format(**db_dane)
db_connection = create_engine(db_connection_str).execution_options(autocommit=True)
metadata = MetaData()
users = Table('oferty_{}'.format(serwis), metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
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
              )
metadata.create_all(db_connection)


def get_data(miasto):
    urls_file = csv.reader(open("{}/urls_{}_{}.csv".format(serwis, serwis, miasto), "r", encoding="utf-8"))
    urls = []
    for row in urls_file:
        urls.append(row[0])

    conn = db_connection.connect()
    for n, url in enumerate(urls):
        if n: # and miasto == 'warszawa':
            try:
                url = urls[n]
                print(n)
                print(url)
                data = serwer.getthat(url)
                if type(data)  != type(None):
                    price = data[0]
                    area = data[1]
                    price_per_meter = data[2]
                    lat = data[3]
                    lon = data[4]
                    ident = data[5]
                    typzabudowy = data[6]
                    rokbudowy = data[7]
                    liczbapokoi = data[8]
                    maxliczbapieter = data[9]
                    pietro = data[10]
                    parking = data[11]
                    kuchnia = data [12]
                    wlasnosc = data[13]
                    stan = data[14]
                    material = data[15]
                    okna = data[16]
                    rynek = data[17]
                    opis = data[18]
                    fields = [price, area, price_per_meter, lat, lon, ident, typzabudowy, rokbudowy, liczbapokoi,
                              maxliczbapieter, pietro, parking, kuchnia, wlasnosc, stan, material, okna, rynek, opis, url]
                    nowy_fields = []
                    for field in fields:
                        if field != opis:
                            sting = str(field)
                            sting = slownik.Slownik().kodowanie(sting)
                            nowy_fields.append(sting)

                    conn.execute(users.insert(),
                                 Price=nowy_fields[0],
                                 Area=nowy_fields[1],
                                 Price_per_metr=nowy_fields[2],
                                 Latitude=nowy_fields[3],
                                 Longitude=nowy_fields[4],
                                 Ident=nowy_fields[5],
                                 Typ_zabudowy=nowy_fields[6],
                                 Rok_zabudowy=nowy_fields[7],
                                 Liczba_pokoi=nowy_fields[8],
                                 Max_liczba_pieter=nowy_fields[9],
                                 Pietro=nowy_fields[10],
                                 Parking=nowy_fields[11],
                                 Kuchnia=nowy_fields[12],
                                 Wlasnosc=nowy_fields[13],
                                 Stan=nowy_fields[14],
                                 Material=nowy_fields[15],
                                 Okna=nowy_fields[16],
                                 Rynek=nowy_fields[17],
                                 Opis=str(data[18]),
                                 Link=url,
                                 Miasto=miasto
                                 )
            except Exception as e:
                print(e)
    conn.close()

