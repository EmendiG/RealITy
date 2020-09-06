import requests
from bs4 import BeautifulSoup
import re
import csv

"""
    Morizon
            """


miasta = ['warszawa', 'krakow','lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin', 'bialystok']


def get_urls(Pages, wybrane_miasto):
    start_URL = 'https://www.morizon.pl/mieszkania/najwieksza-powierzchnia/'
    mid_URL = '/?ps[price_from]=120000&ps[price_m2_to]=45000&page='
    urls = []

    for i in range(1, Pages + 1, 1):
        url =  start_URL + miasta[wybrane_miasto] + mid_URL + str(i)
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'
        headers = {'User-Agent': user_agent}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'lxml')
        try:
            wyscrapowane = soup.find("div", attrs={'class':'listingBox mainBox propertyListingBox content-box-main col-xs-9'}).section
            wyscrapowane2 = wyscrapowane.findAll("div", attrs={'class':'row row--property-list'})
            for j in range(0, len(wyscrapowane2)):
                    if wyscrapowane2[j].find("a", attrs={'class':'property_link property-url'}) is not type(None):
                        scrapowane = wyscrapowane2[j].find("a", attrs={'class':'property_link property-url'})['href']
                        if scrapowane not in urls:
                            urls.append(scrapowane)
        except:
            pass
        print(i)
        # print(url)
        print('Links amont to = ', len(urls))
    return urls


def write_urls(wybrane_miasto):
    start_URL = 'https://www.morizon.pl/mieszkania/najnowsze/'
    mid_URL = '/?ps[price_from]=120000&ps[price_m2_to]=45000&page=2'
    url = start_URL + miasta[wybrane_miasto] + mid_URL
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')
    Pages = soup.find("ul", attrs={"class": "nav nav-pills mz-pagination-number"}).findAll("li")[-2].a.text
    Pages = int(Pages)

    with open('morizon/urls_morizon_{}.csv'.format(miasta[wybrane_miasto]), 'a+', newline='', encoding="utf-8") as csvfile:
        file = open('morizon/urls_morizon_{}.csv'.format(miasta[wybrane_miasto]), "r")
        old_csv = csv.reader(file, delimiter=' ')
        old_list = []
        for row in old_csv:
            old_list.append((row[0]))
        file.close()

        writer = csv.writer(csvfile)
        urls = get_urls(Pages, wybrane_miasto)
        for url in urls:
            if url not in old_list:
                writer.writerow([url])


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
    if parses:
        long = parses[0].get('data-lng')
        long = round(float(long), 4)
        lati = parses[0].get('data-lat')
        lati = round(float(lati), 4)

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

def get_rynek(table):
    if table:
        for tr in table.table.find_all('tr'):
            if 'Rynek: ' in str(tr.th):
                return str(tr.td.text).strip()
        return 'NaN'

def get_typzabudowy(table):
    if table:
        table_2 = table.find_all('table')[1]
        for tr in table_2.find_all('tr'):
            if 'Typ budynku: ' in str(tr.th):
                return str(tr.td.text).strip().lower()
        return 'NaN'


def get_rokbudowy(table):
    if table:
        table_2 = table.find_all('table')[1]
        for tr in table_2.find_all('tr'):
            if 'Rok budowy: ' in str(tr.th):
                return str(tr.td.text).strip()
        return 'NaN'

def get_liczbapokoi(soup):
    if soup:
        roomnumber = soup.find('li', attrs={'class': 'paramIconNumberOfRooms'})
        return  roomnumber.em.get_text()
    else:
        return 'NaN'

def get_pietro(table):
    if table:
        for tr in table.table.find_all('tr'):
            if 'Piętro: ' in str(tr.th):
                pietro = str(tr.td.text).strip()
                if '/' in pietro:
                    return pietro.split('/')[0].strip()
                else:
                    return pietro
        return 'NaN'

def get_maxliczbapieter(table):
    if table:
        for tr in table.table.find_all('tr'):
            if 'Liczba pięter: ' in str(tr.th):
                return str(tr.td.text).strip()
            elif 'Piętro: ' in str(tr.th):
                maxpietro = str(tr.td.text).strip()
                if '/' in maxpietro:
                    return maxpietro.split('/')[1].strip()
        return 'NaN'

def get_parking(table):
    if table:
        for h3 in table.find_all('h3'):
            if 'Udogodnienia' in h3.text:
                if re.findall('parking', h3.findNext('p').text):
                    return 'garaz'
        return 'NaN'

def get_kuchnia(table):
    if table:
        table_2 = table.find_all('table')[0]
        for tr in table_2.find_all('tr'):
            if 'Typ kuchni: ' in str(tr.th):
                return str(tr.td.text).strip().lower()
        return 'NaN'

def get_wlasnosc(table):
    if table:
        table_2 = table.find_all('table')[0]
        for tr in table_2.find_all('tr'):
            if 'Forma własności: ' in str(tr.th):
                return str(tr.td.text).strip().lower()
        return 'NaN'

def get_stan(table):
    if table:
        table_2 = table.find_all('table')[0]
        for tr in table_2.find_all('tr'):
            if 'Stan nieruchomości: ' in str(tr.th):
                return str(tr.td.text).strip().lower()
        return 'NaN'

def get_material(table):
    if table:
        table_2 = table.find_all('table')[1]
        for tr in table_2.find_all('tr'):
            if 'Materiał budowlany: ' in str(tr.th):
                return str(tr.td.text).strip().lower()
        return 'NaN'

def get_okna(table):
    if table:
        table_2 = table.find_all('table')[0]
        for tr in table_2.find_all('tr'):
            if 'Stolarka okienna: ' in str(tr.th):
                return str(tr.td.text).strip().lower()
        return 'NaN'

def get_opis(soup):
    opis = soup.find('section', attrs={'class':'descriptionContent'}).get_text()
    return opis

def wyprintuj_mnie( ident, price, area, price_per_meter, lengthehe, lat, lon, typzabudowy, rokbudowy, liczbapokoi,
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
    # print(opis)

def getthat(url):
    soup = soupa(url)
    table = soup.find('section', attrs={'class': 'params clearfix'})
    if type(get_lon_lat(soup)) is not type(None):
        lon = get_lon_lat(soup)[0]
        lat = get_lon_lat(soup)[1]
        price = get_price(soup)
        area = get_area(soup)
        price_per_meter = round(price / area, 0)
        # price_per_metr = get_price_per_metr(soup)
        rynek = get_rynek(table)
        typzabudowy = get_typzabudowy(table)
        rokbudowy = get_rokbudowy(table)
        liczbapokoi = get_liczbapokoi(soup)
        maxliczbapieter = get_maxliczbapieter(table)
        pietro = get_pietro(table)
        parking = get_parking(table)
        kuchnia = get_kuchnia(table)
        wlasnosc = get_wlasnosc(table)
        stan = get_stan(table)
        material = get_material(table)
        okna = get_okna(table)
        ident = get_id(soup)
        lengthehe = len(url)
        opis = get_opis(soup)
        # wyprintuj_mnie(ident, price, area, price_per_meter, lengthehe, lat, lon, typzabudowy, rokbudowy, liczbapokoi, maxliczbapieter, pietro, parking, kuchnia, wlasnosc, stan, material, okna, rynek, opis)
        return price, area, price_per_meter, lat, lon, ident, typzabudowy, rokbudowy, liczbapokoi, maxliczbapieter, pietro, parking, kuchnia, wlasnosc, stan, material, okna, rynek, opis
    else:
        pass

