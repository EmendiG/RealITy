from bs4 import BeautifulSoup
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
import re
import pandas as pd
import unicodedata

"""
    Gratka
            """
miasta = ['warszawa', 'krakow','lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin', 'bialystok']


def get_urls(Pages, wybrane_miasto):
    start_URL = 'https://gratka.pl/nieruchomosci/mieszkania/'
    mid_URL = '/sprzedaz?page='
    end_URL = '&cena-calkowita:min=120000&cena-za-m2:max=45000&sort=cheap'
    urls = []

    for i in range(1, Pages + 1, 1):
        url =  start_URL + miasta[wybrane_miasto] + mid_URL + str(i) + end_URL
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'
        headers = {'User-Agent': user_agent}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'lxml')
        wyscrapowane = soup.findAll("article", attrs={"class": "teaserEstate"})
        for j in range(0, len(wyscrapowane)):
            scrapowane = wyscrapowane[j]['data-href']
            if scrapowane not in urls:
                urls.append(scrapowane)
        print(i)
        print(url)
    return urls


def write_urls(wybrane_miasto):
    start_URL = 'https://gratka.pl/nieruchomosci/mieszkania/'
    mid_URL = '/sprzedaz?page=2'
    end_URL = '&cena-calkowita:min=120000&cena-za-m2:max=45000&sort=cheap'  #&rynek=pierwotny
    url = start_URL + miasta[wybrane_miasto] + mid_URL + end_URL
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')
    Pages = soup.findAll("div", attrs={"class": "pagination"})[0].find('span', attrs={'class': 'pagination__separator'}).findNext().contents[0]
    Pages = int(Pages)

    with open('urls_gratka_{}.csv'.format(miasta[wybrane_miasto]), 'w+', newline='', encoding="utf-8") as csvfile:
        old_csv = csv.reader(csvfile, delimiter=' ')
        old_list = []
        for row in old_csv:
            old_list.append((row[0]))
        writer = csv.writer(csvfile)
        urls = get_urls(Pages, wybrane_miasto)
        for url in urls:
            if url not in old_list:
                writer.writerow([url])


def soupa(url):
    """Wiekszosc parsera"""
    #page = requests.get(url)
    user_agent = 'Mozilla/5.0'
    headers = {'User-Agent': user_agent}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')
    return soup


def get_lon_lat(soup):
    parses = soup.find("div", attrs={"id": "leftColumn", "class": "small-12 large-8 column"}).find_all("script")
    if isinstance(parses, type(None)):
        pass
    else:
        if len(parses) < 6:
            long = parses[3].contents[0].split("locationParams: ")[1].split("geograficzna-x")[1][2:9]
            lati = parses[3].contents[0].split("locationParams: ")[1].split("geograficzna-y")[1][2:9]
        else:
            long = parses[6].contents[0].split("locationParams: ")[1].split("geograficzna-x")[1][2:9]
            lati = parses[6].contents[0].split("locationParams: ")[1].split("geograficzna-y")[1][2:9]
    long = re.sub("[^0-9]", "", long)
    lati = re.sub("[^0-9]", "", lati)
    long = float(int(long)/(int("1"+((len(long)-2)*"0"))))
    lati = float(int(lati)/(int("1"+((len(lati)-2)*"0"))))
    return long, lati


def get_price(soup):
    price_prep = soup.find("span", attrs={"class": "priceInfo__value"}).contents[0].strip().replace(" ", "").replace(",", ".")
    price = float(price_prep)
    return price


def get_area(soup):
    area_prep = soup.findAll("ul", attrs={"class": "parameters__rolled"})[0].find("span", text="Powierzchnia w m2")\
    .parent.find("b", attrs={"class": "parameters__value"}).contents[0]
    area_len = len(area_prep) - 2
    area = area_prep[:area_len].replace(",", ".")
    area = re.sub("[^0-9.]", "", area)
    area = float(area)
    return area


def get_id(soup):
    #ident = soup.findAll("div", attrs={"class": "contactForm__info row"})[0].find("small", attrs={"class": "contactForm__id"}).b.contents[0]
    parses = soup.find("div", attrs={"id": "leftColumn", "class": "small-12 large-8 column"}).find_all("script")
    if len(parses) < 6:
        ident = parses[3].contents[0].split("offersId: ")[1].split("[")[1].split("]")[0]
    else:
        ident = parses[6].contents[0].split("offersId: ")[1].split("[")[1].split("]")[0]
    return ident


def get_price_per_metr(soup):
    price_per_meter_prep = soup.find("span", attrs={"class": "priceInfo__additional"}).contents[0].strip().replace(" ","").replace(",", ".")
    price_per_metr = round(float(price_per_meter_prep[:-4]), 0)
    return price_per_metr


def get_rynek(soup):
    try:
        match = [scrip for scrip in soup.body.findAll('script') if str(scrip).find('<script>PPDataLayer.push') == 0]
        rynek = json.loads(str(match[0])[25:(len(str(match[0])) - 11)])['rynek']
        return rynek
    except:
        return('NaN')

def get_dzielnia_ulica(soup):
    #parses = soup.find("div", attrs={"id": "leftColumn", "class": "small-12 large-8 column"}).find_all("script")
    #ulica = parses[6].text.split("locationParams: ")[1].split("ulica")[1].split('"')[2].split('"')[0]
    dzielnia = soup.findAll("a", attrs={"class":"parameters__locationLink"})[1].contents[0]
    #dzielnia = parses[6].text.split("locationParams: ")[1].split("dzielnica")[1].split('"')[2].split('"')[0]
    return dzielnia #, ulica


def get_typzabudowy(span):
    try:
        for n, typ in enumerate(span):
            if 'Typ zabudowy' in typ:
                typzabudowy = span[n].findNext('b').contents[0]
        return typzabudowy
    except:
        return('NaN')


def get_rokbudowy(span):
    try:
        for n, typ in enumerate(span):
            if 'Rok budowy' in typ:
                rokbudowy = span[n].findNext('b').contents[0]
        return rokbudowy
    except:
        return('NaN')


def get_liczbapokoi(span):
    try:
        for n, typ in enumerate(span):
            if 'Liczba pokoi' in typ:
                liczbapokoi = span[n].findNext('b').contents[0]
        return liczbapokoi
    except:
        return('NaN')


def get_maxliczbapieter(span):
    try:
        for n, typ in enumerate(span):
            if 'Liczba pięter w budynku' in typ:
                maxliczba = span[n].findNext('b').contents[0]
        return maxliczba
    except:
        return('NaN')


def get_pietro(span):
    try:
        for n, typ in enumerate(span):
            if 'Piętro' in typ:
                pietro = span[n].findNext('b').contents[0]
        return pietro
    except:
        return('NaN')


def get_parking(span):
    try:
        for n, typ in enumerate(span):
            if 'Miejsce parkingowe' in typ:
                parking = span[n].findNext('b').contents[0]
        return parking
    except:
        return('NaN')


def get_kuchnia(span):
    try:
        for n, typ in enumerate(span):
            if 'Forma kuchni' in typ:
                kuchnia = span[n].findNext('b').contents[0]
        return kuchnia
    except:
        return('NaN')


def get_wlasnosc(span):
    try:
        for n, typ in enumerate(span):
            if 'Forma własności' in typ:
                wlasnosc = span[n].findNext('b').contents[0]
        return wlasnosc
    except:
        return('NaN')


def get_stan(span):
    try:
        for n, typ in enumerate(span):
            if 'Stan' in typ:
                stan = span[n].findNext('b').contents[0]
        return stan
    except:
        return('NaN')


def get_material(span):
    try:
        for n, typ in enumerate(span):
            if 'Materiał budynku' in typ:
                material = span[n].findNext('b').contents[0]
        return material
    except:
        return('NaN')


def get_okna(span):
    try:
        for n, typ in enumerate(span):
            if 'Okna' in typ:
                okna = span[n].findNext('b').contents[0]
        return okna
    except:
        return('NaN')


def get_opis(soup):
    opis = soup.find('div', attrs={'class':'description__rolled ql-container', 'description__rolled ql-container': ""}).get_text()
    return opis


def get_url(soup):
    urll = soup.html.head.link.get("href")
    return urll


def wyprintuj_mnie( ident, price, area,  price_per_meter, lengthehe, lat, lon, typzabudowy, rokbudowy, liczbapokoi,
                   maxliczbapieter, pietro, parking, kuchnia, wlasnosc, stan, material, okna, rynek, opis):
    print("ID: ", str(ident).rjust(lengthehe - 5))
    print("Price: ", str(price).rjust(lengthehe - 8))
    print("Area: ", str(area).rjust(lengthehe - 7))
    print("Price per meter: ", str(round(price_per_meter, 0)).rjust(lengthehe - 18))
    print("*" * lengthehe)
    print("Lati: ", str(lat).rjust(lengthehe - 7))
    print("Long: ", str(lon).rjust(lengthehe - 7))
    print("Typ zabudowy: ", str(typzabudowy).rjust(lengthehe - 15))
    print("Rok budowy: ", str(rokbudowy).rjust(lengthehe - 13))
    print("Liczba pokoi: ", str(liczbapokoi).rjust(lengthehe - 15))
    print("Liczba pięter w budynku: ", str(maxliczbapieter).rjust(lengthehe - 26))
    print("Pietro: ", str(pietro).rjust(lengthehe - 9))
    print("Parking: ", str(parking).rjust(lengthehe - 10))
    print("Kuchnia: ", str(kuchnia).rjust(lengthehe - 10))
    print("Forma wlasnosci: ", str(wlasnosc).rjust(lengthehe - 18))
    print("Stan: ", str(stan).rjust(lengthehe - 7))
    print("Materiał: ", str(material).rjust(lengthehe - 11))
    print("Okna: ", str(okna).rjust(lengthehe - 7))
    print("Rynek: ", str(rynek).rjust(lengthehe - 8))
    print(opis)


def getthat(url):
    soup = soupa(url)
    span = soup.find('ul', attrs={'class': 'parameters__rolled'}).findAll('span')
    lon = get_lon_lat(soup)[0]
    lat = get_lon_lat(soup)[1]
    price = get_price(soup)
    area = get_area(soup)
    rynek = get_rynek(soup)
    typzabudowy = get_typzabudowy(span)
    rokbudowy = get_rokbudowy(span)
    liczbapokoi = get_liczbapokoi(span)
    maxliczbapieter = get_maxliczbapieter(span)
    pietro = get_pietro(span)
    parking = get_parking(span)
    kuchnia = get_kuchnia(span)
    wlasnosc = get_wlasnosc(span)
    stan = get_stan(span)
    material = get_material(span)
    okna = get_okna(span)
    ident = get_id(soup)
    price_per_meter = round(price / area, 0)
    #price_per_metr = get_price_per_metr(soup)
    opis = get_opis(soup)
    lengthehe = len(url)
    #wyprintuj_mnie(dzielnia, ident, price, area, price_per_meter, lengthehe, lat, lon, typzabudowy, rokbudowy, liczbapokoi, maxliczbapieter, pietro, parking, kuchnia, wlasnosc, stan, material, okna, rynek, opis, urll)
    return price, area, price_per_meter, lat, lon, ident, typzabudowy, rokbudowy, liczbapokoi, maxliczbapieter, pietro, parking, kuchnia, wlasnosc, stan, material, okna, rynek, opis


