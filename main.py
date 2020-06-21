import csv
import slownik
import postgresql_modifier
import osmOverpassApi

miasta = ['warszawa', 'krakow', 'lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin','bialystok'] #

miastaDict = {'warszawa': 'Warszawa', 'krakow': 'Kraków', 'lodz': 'Łódź', 'wroclaw': 'Wrocław', 'poznan': 'Poznań',
              'gdansk': 'Gdańsk', 'szczecin': 'Szczecin', 'bydgoszcz': 'Bydgoszcz', 'lublin': 'Lublin',
              'bialystok': 'Białystok'}


def get_data(miasto, serwis):
    urls_file = csv.reader(open("{0}/urls_{0}_{1}.csv".format(serwis, miasto), "r", encoding="utf-8"))
    urls = []
    for row in urls_file:
        urls.append(row[0])

    serwer = postgresql_modifier.Strona(serwis).wybor()
    users = postgresql_modifier.Strona(serwis).sqldbMaker()
    conn = postgresql_modifier.PostgreSQL_connectSQLalchemy()

    for n, url in enumerate(urls):
        if n < 30:
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



# get_data('warszawa', 'otodom')
# help(postgresql_modifier.oferty_Merger)
# postgresql_modifier.oferty_Merger('otodom', 'gratka', 'merged')

# for n, miasto in enumerate(miastaDict):
#    District(miastaDict[miasto]).osmApi_getDistricts_mapPolygons()
# for miasto in miasta:
#    postgresql_modifier.osmApi_DataFrame_ToSQL(miasto, 'Leisure')

#postgresql_modifier.osmApi_DataFrame_ToSQL('warszawa', 'Tourism')

# TODO: Znaleźć najblizsze amenities dla kazdego z rekordu (wystepowanie, nie cecha??) => Wykonac nowy db (relacyjny)
# TODO: Znaleźc sąsiadow lokalizacyjnych (inne nieuchomosci, po co?? <- trzeba sprawdzic czy trzeba)
