import csv
import slownik
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Text, MetaData, Float
import mysql_modifier

miasta = ['warszawa', 'krakow', 'lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin', 'bialystok']


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
        db_connection = mysql_modifier.connect_to_MYSQL()
        metadata = MetaData()
        users = Table('oferty_{}'.format(self.serwis), metadata,
                      Column('index', Integer, primary_key=True, autoincrement=True),
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
        return users


def get_data(miasto, serwis):
    urls_file = csv.reader(open("{0}/urls_{0}_{1}.csv".format(serwis, miasto), "r", encoding="utf-8"))
    urls = []
    for row in urls_file:
        urls.append(row[0])

    serwer = Strona(serwis).wybor()
    db_connection = mysql_modifier.connect_to_MYSQL()
    users = Strona(serwis).mysql_dbMaker()
    conn = db_connection.connect()

    for n, url in enumerate(urls):
        if n:
            try:
                url = urls[n]
                print(n)
                print(url)
                data = serwer.getthat(url)
                if type(data) != type(None):
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
                    kuchnia = data[12]
                    wlasnosc = data[13]
                    stan = data[14]
                    material = data[15]
                    okna = data[16]
                    rynek = data[17]
                    opis = data[18]
                    fields = [price, area, price_per_meter, lat, lon, ident, typzabudowy, rokbudowy, liczbapokoi,
                              maxliczbapieter, pietro, parking, kuchnia, wlasnosc, stan, material, okna, rynek, opis,
                              url]
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


#get_data('warszawa', 'gratka')
#mysql_modifier.oferty_INITIATION('otodom', 'gratka')
#mysql_modifier.oferty_db_MERGER('merged', 'gratka', 'merged')

help(mysql_modifier.oferty_db_MERGER)

# TODO: ?? znalexc granice administracyjne lokalizacji za pomoca API Openmaps ??
# TODO: Ogarnac koordynaty amenities z Openmaps i Geoportal
# TODO: Znaleźć najblizsze amenities dla kazdego z rekordu (wystepowanie, nie cecha??) => Wykonac nowy db
# TODO: Znaleźc sąsiadow lokalizacyjnych (po co??)
