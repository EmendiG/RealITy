import requests
from bs4 import BeautifulSoup
import re

"""
    Morizon
            """



def soupa(url):
    """Wiekszosc parsera"""
    #page = requests.get(url)
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')
    return soup


def get_lon_lat(soup):
    parses = soup.find_all("div", attrs={"class": "mz-card__item"})[1].find_all('div', attrs={'class': 'GoogleMap'})
    long = parses[0].get('data-lng')
    lati = parses[0].get('data-lat')
    return long, lati


def get_price(soup):
    parses = soup.find_all('li', attrs={'class':'paramIconPrice'})[0].contents[1].contents[0]
    parses = re.sub("[^0-9]", "", parses)
    price = float(parses)
    return price


def get_area(soup):
    parses = soup.find_all('li', attrs={'class': 'paramIconLivingArea'})[0].contents[1].contents[0].replace(",", ".")
    parses = re.sub("[^0-9.]", "", parses)
    area = float(parses)
    return area


def get_id(soup):
    parses = soup.find_all("div", attrs={"class": "mz-card__item"})[1].find_all('div', attrs={'class': 'GoogleMap'})
    ident = parses[0].get('data-id')
    return ident


def get_price_per_metr(soup):
    parses = soup.find_all('li', attrs={'class': 'paramIconPriceM2'})[0].contents[1].contents[0].replace(",", ".")
    parses = re.sub("[^\d\.]", '', parses)  # parses = parses.replace(u'\xa0', u' ').strip().replace(' ', '')
    price_per_metr = float(parses)
    return price_per_metr

def get_rynek(soup):
    try:
        parses = soup.find_all('section', attrs={'class': 'params clearfix'})
        for tr in parses[0].table.find_all('tr'):
            if 'Rynek: ' in str(tr.th):
                return str(tr.td.text.strip())
    except:
        return('NaN')

def wyprintuj_mnie( ident, price, area, price_per_meter, price_per_metr, lengthehe, lat, lon, url):
    #print("Ulica: ", ulica.rjust(lengthehe - 8))
    print("ID: ", str(ident).rjust(lengthehe - 5))
    print("Price: ", str(price).rjust(lengthehe - 8))
    print("Area: ", str(area).rjust(lengthehe - 7))
    print("Price per meter: ", str(round(price_per_meter, 0)).rjust(lengthehe - 18))
    print("2nd Price per meter: ", str(round(price_per_metr, 0)).rjust(lengthehe - 22))
    print("*" * lengthehe)
    print("Lati: ", str(lat).rjust(lengthehe - 7))
    print("Long: ", str(lon).rjust(lengthehe - 7))

def getthat(url):
    soup = soupa(url)
    lon = get_lon_lat(soup)[0]
    lat = get_lon_lat(soup)[1]
    price = get_price(soup)
    area = get_area(soup)
    ident = get_id(soup)
    price_per_meter = round(price / area, 0)
    price_per_metr = get_price_per_metr(soup)
    url = url
    lengthehe = len(url)
    print(get_rynek(soup))
    # wyprintuj_mnie( ident, price, area, price_per_meter, price_per_metr, lengthehe, lat, lon, url)
    return price, area, price_per_metr, price_per_meter, lat, lon, ident, url

url1 = 'https://www.morizon.pl/oferta/sprzedaz-mieszkanie-warszawa-ursus-tomcia-palucha-47m2-mzn2036649127'
url2 = 'https://www.morizon.pl/oferta/sprzedaz-mieszkanie-warszawa-mokotow-ludwiga-van-beethovena-45m2-mzn2036387936'
url3 = 'https://www.morizon.pl/oferta/sprzedaz-mieszkanie-warszawa-wilanow-292m2-mzn2034562958'
url4 = 'https://www.morizon.pl/oferta/sprzedaz-mieszkanie-warszawa-mokotow-157m2-mzn2035978428'

getthat(url1)
