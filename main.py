import gratkapy
import otodompy
import csv
import slownik
import sqlite3
from bs4 import BeautifulSoup
import time

miasta = ['warszawa', 'krakow','lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin', 'bialystok']

def get_data(miasto):
    urls_file = csv.reader(open("urls_otodom_{}.csv".format(miasto), "r", encoding="utf-8"))
    urls = []
    for row in urls_file:
        urls.append(row[0])

    #fieldnames = ['Price', 'Area', 'Price_per_metr', 'Latitude', 'Longitude', 'ID', 'Typ_zabudowy', 'Rok_zabudowy', 'Liczba_pokoi',
    #              'Max_liczba_pieter', 'Pietro', 'Parking', 'Kuchnia', 'Wlasnosc', 'Stan', 'Material', 'Okna', 'Opis', 'Link']
    conn = sqlite3.connect('nieruchomosci2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS oferty2 (Price BLOB,
                                      Area BLOB,
                                      Price_per_metr BLOB,
                                      Latitude BLOB,
                                      Longitude BLOB,
                                      ID BLOB,
                                      Typ_zabudowy BLOB,
                                      Rok_zabudowy BLOB,
                                      Liczba_pokoi BLOB,
                                      Max_liczba_pieter BLOB,
                                      Pietro BLOB,
                                      Parking BLOB,
                                      Kuchnia BLOB,
                                      Wlasnosc BLOB,
                                      Stan BLOB,
                                      Material BLOB,
                                      Okna BLOB,
                                      Rynek BLOB,
                                      Opis BLOB,
                                      Link BLOB,
                                      Miasto BLOB)''')

    #with open('gratka_oferty_{}.csv'.format(miasto), 'a', newline='', encoding="utf-8") as csvfile:
    #    writer = csv.writer(csvfile)
        #writer.writerow(fieldnames)
    for n, url in enumerate(urls):
        if n > 0: # and miasto == 'warszawa':
            try:
                url = urls[n]
                print(n)
                print(url)
                data = otodompy.getthat(url)
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
                        #if field == opis:
                            #lista_opis = field.split()
                            #opis_new = []
                            #opis_old = []
                            #for word in lista_opis:
                            #    opis_old.append(word)
                            #    if word.isalpha():
                            #        word = slownik.Slownik().kodowanie(word)
                            #        opis_new.append(word)
                            #nowy_opis = ' '.join(word for word in opis_new)
                            #stary_opis = ' '.join(word2 for word2 in opis_old)
                            #nowy_fields.append(nowy_opis)
                            #nowy_fields.append(stary_opis)
                        if field != opis:
                            sting = str(field)
                            sting = slownik.Slownik().kodowanie(sting)
                            nowy_fields.append(sting)
                    c.execute('''INSERT INTO oferty2 VALUES (:Price, :Area, :Price_per_metr, :Latitude, :Longitude, :ID,
                                :Typ_zabudowy, :Rok_zabudowy, :Liczba_pokoi, :Max_liczba_pieter, :Pietro, :Parking, 
                                 :Kuchnia, :Wlasnosc, :Stan, :Material, :Okna, :Rynek, :Opis, :Link, :Miasto)''',
                              {'Price':nowy_fields[0],
                              'Area':nowy_fields[1],
                              'Price_per_metr':nowy_fields[2],
                              'Latitude':nowy_fields[3],
                              'Longitude':nowy_fields[4],
                              'ID':nowy_fields[5],
                              'Typ_zabudowy':nowy_fields[6],
                              'Rok_zabudowy':nowy_fields[7],
                              'Liczba_pokoi':nowy_fields[8],
                              'Max_liczba_pieter':nowy_fields[9],
                              'Pietro':nowy_fields[10],
                              'Parking':nowy_fields[11],
                              'Kuchnia':nowy_fields[12],
                              'Wlasnosc':nowy_fields[13],
                              'Stan':nowy_fields[14],
                              'Material':nowy_fields[15],
                              'Okna':nowy_fields[16],
                              'Rynek':nowy_fields[17],
                              'Opis': str(data[18]),
                              'Link':url,
                              'Miasto':miasto})
                    conn.commit()
                    #writer.writerow(nowy_fields)
            except:
                pass
    conn.close()
    #csvfile.close()

for miasto in miasta:
    get_data(miasto)


#import pandas as pd
#conn = sqlite3.connect('nieruchomosci.db')
#sql_query = pd.read_sql_query('''SELECT * FROM oferty''', conn)
#df = pd.DataFrame(sql_query)
#print(df.head())

