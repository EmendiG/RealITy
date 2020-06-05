from bs4 import BeautifulSoup
import requests
import time
import csv
import json
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

"""
    Otodom
            """

miasta = ['warszawa', 'krakow', 'lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin', 'bialystok']

#'181.118.167.104:80'
#'139.162.38.191:80'

proxies = {
    'http': 'http://139.162.38.191:80',
    'https': 'https://139.162.38.191:80'
}


def get_urls(Pages, wybrane_miasto):
    start_URL = 'https://www.otodom.pl/sprzedaz/mieszkanie/'
    mid_URL = '/?search%5Bfilter_float_price%3Afrom%5D=120000&search%5Bfilter_float_price_per_m%3Ato%5D=45000&page='
    # end_URL = ''
    urls = []

    for i in range(1, Pages + 1, 1):
        url = start_URL + miasta[wybrane_miasto] + mid_URL + str(i)  # + end_URL
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'
        headers = {'User-Agent': user_agent, 'Referer': 'https://google.com'}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'lxml')
        wyscrapowane = soup.find("div", attrs={"class": "col-md-content section-listing__row-content"}).findAll(
            "article", attrs={"class": "offer-item"})
        for j in range(0, len(wyscrapowane)):
            scrapowane = wyscrapowane[j]['data-url']
            if scrapowane not in urls:
                urls.append(scrapowane)
        time.sleep(random.uniform(1, 4))
        print(i)
        print(url)
    return urls


def write_urls(wybrane_miasto):
    start_URL = 'https://www.otodom.pl/sprzedaz/mieszkanie/'
    mid_URL = '/?search%5Bfilter_float_price%3Afrom%5D=120000&search%5Bfilter_float_price_per_m%3Ato%5D=45000&page=2'
    # end_URL = ''
    url = start_URL + miasta[wybrane_miasto] + mid_URL  # + end_URL
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'
    headers = {'User-Agent': user_agent, 'Referer': 'https://google.com'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')
    Pages = \
    soup.findAll("div", attrs={"class": "after-offers clearfix"})[0].find('ul', attrs={'class': 'pager'}).findAll('li')[
        4].contents[0].contents[0]
    Pages = int(Pages)

    with open('urls_otodom_{}.csv'.format(miasta[wybrane_miasto]), 'w+', newline='', encoding="utf-8") as csvfile:
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
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'
    headers = {'User-Agent': user_agent, 'Referer': 'https://google.com'}
    page = requests.get(url, headers=headers, proxies=proxies) #
    soup = BeautifulSoup(page.content, 'lxml')
    if type(soup.find("div", attrs={"class": "css-eij48e"})) == type(None):
        soup = 'niekonektet'
    else:
        soup = soup
    return soup


def get_lon_lat(soup):
    parses = soup.find("div", attrs={"class": "css-eij48e"}).find_next_sibling()
    for pars in parses:  # czemu get_text() nie dziala??
        data = json.loads(pars)
    lati = data['@graph'][0]['geo']['latitude']
    longi = data['@graph'][0]['geo']['longitude']
    return lati, longi


def get_price(soup):
    parses = soup.find("div", attrs={"class": "css-eij48e"}).find_next_sibling()
    for pars in parses:  # czemu get_text() nie dziala??
        data = json.loads(pars)
    price = data['@graph'][1]['price']
    price = float(price)
    return price


def get_area(soup):
    area_prep = soup.find("div", attrs={'class': "css-1ci0qpi"})
    area_text = area_prep.ul.li.strong.contents[0].string
    area_len = len(area_text) - 3
    area = area_text[:area_len].replace(",", ".")
    area = float(area)
    return area


def get_id(soup):
    id_prep = soup.find("div", attrs={'class': "css-kos6vh"})
    id = id_prep.contents[0][-8:]
    id = int(id)
    return id


def get_price_per_metr(soup):
    price_per_meter_prep = soup.find("div", attrs={"class": "css-zdpt2t"})
    price_per_meter_raw = price_per_meter_prep.contents[0].replace(" ", "")
    price_per_meter_len = len(price_per_meter_raw) - 5
    price_per_metr = price_per_meter_raw[:price_per_meter_len]
    price_per_metr = float(price_per_metr)
    return price_per_metr


def get_rynek(li):
    try:
        for typ in li:
            if 'Rynek:' in typ.text:
                rynek = typ.strong.text  # .contents[0]
        return rynek
    except:
        return ('NaN')


def get_typzabudowy(li):
    try:
        for typ in li:
            if 'Rodzaj zabudowy: ' in typ:
                typzabudowy = typ.strong.text
        return typzabudowy
    except:
        return ('NaN')


def get_rokbudowy(li):
    try:
        for typ in li:
            if 'Rok budowy: ' in typ:
                rokbudowy = typ.strong.text
        return rokbudowy
    except:
        return ('NaN')


def get_liczbapokoi(li):
    try:
        for typ in li:
            if 'Liczba pokoi: ' in typ:
                liczbapokoi = typ.strong.text
        return liczbapokoi
    except:
        return ('NaN')


def get_maxliczbapieter(li):
    try:
        for typ in li:
            if 'Liczba pięter: ' in typ:
                maxliczba = typ.strong.text
        return maxliczba
    except:
        return ('NaN')


def get_pietro(li):
    try:
        for typ in li:
            if 'Piętro: ' in typ:
                pietro = typ.strong.text
        return pietro
    except:
        return ('NaN')


def get_parking(soup):
    try:
        parking_prep = soup.find("div", attrs={'class': "css-1bpegon"})
        for park in parking_prep.ul:
            if 'garaż/miejsce parkingowe' in park:
                parking = park.text
        return parking
    except:
        return ('NaN')


def get_kuchnia(soup):
    try:
        kuchnia_prep = soup.find("div", attrs={'class': "css-1bpegon"})
        for kuch in kuchnia_prep.ul:
            if 'oddzielna kuchnia' in kuch:
                kuchnia = kuch.text
        return kuchnia
    except:
        return ('NaN')


def get_wlasnosc(li):
    try:
        for typ in li:
            if 'Forma własności: ' in typ:
                wlasnosc = typ.strong.text
        return wlasnosc
    except:
        return ('NaN')


def get_stan(li):
    try:
        for typ in li:
            if 'Stan wykończenia: ' in typ:
                stan = typ.strong.text
        return stan
    except:
        return ('NaN')


def get_material(li):
    try:
        for typ in li:
            if 'Materiał budynku: ' in typ:
                material = typ.strong.text
        return material
    except:
        return ('NaN')


def get_okna(li):
    try:
        for typ in li:
            if 'Okna: ' in typ:
                okna = typ.strong.text
        return okna
    except:
        return ('NaN')


def get_opis(zoup):
    """To co JavaScriptowe"""
    """try:
        chromeOptions = Options()
        chromeOptions.add_argument('-headless')
        #chromeOptions.add_argument('--ignore-certificate-errors')
        chromeOptions.add_argument('--incognito')
        browser = webdriver.Chrome(executable_path=r"F:\OneDrive - Politechnika Warszawska\PyCharmProjects\analityka\chromedriver.exe", options= chromeOptions)
        browser.get(url)
        element = browser.find_element_by_xpath('/html/body/div/article/div[3]/div[1]/section[2]/div[2]/a')
        browser.execute_script("arguments[0].click();", element)
        opis = browser.find_element_by_xpath('/html/body/div/article/div[3]/div[1]/section[2]/div[1]').text
        return opis
    except:
        opis = soup.find('div', attrs={'class':"css-1bi3ib9"}).text
        return opis"""
    opis = zoup.find('section', attrs={'class': "section-description"}).text
    return opis


def wyprintuj_mnie( ident, price, area,  price_per_meter, lengthehe, lat, lon, typzabudowy, rokbudowy, liczbapokoi, maxliczbapieter, pietro, parking, kuchnia, wlasnosc, stan, material, okna, rynek, opis):
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
    if soup != "niekonektet":
        li = soup.findAll('li')
        lon = get_lon_lat(soup)[1]
        lat = get_lon_lat(soup)[0]
        price = get_price(soup)
        area = get_area(soup)
        ident = get_id(soup)
        price_per_meter = round(price / area, 0)
        price_per_metr = get_price_per_metr(soup)
        rynek = get_rynek(li)
        typzabudowy = get_typzabudowy(li)
        rokbudowy = get_rokbudowy(li)
        liczbapokoi = get_liczbapokoi(li)
        maxliczbapieter = get_maxliczbapieter(li)
        pietro = get_pietro(li)
        parking = get_parking(soup)
        kuchnia = get_kuchnia(soup)
        wlasnosc = get_wlasnosc(li)
        stan = get_stan(li)
        material = get_material(li)
        okna = get_okna(li)
        start = time.time()
        opis = get_opis(soup)
        end = time.time()
        print(end - start)
        lengthehe = len(url)
        #wyprintuj_mnie(ident, price, area, price_per_meter, lengthehe, lat, lon, typzabudowy, rokbudowy, liczbapokoi, maxliczbapieter, pietro, parking, kuchnia, wlasnosc, stan, material, okna, rynek, opis)
        return price, area, price_per_meter, lat, lon, ident, typzabudowy, rokbudowy, liczbapokoi, maxliczbapieter, pietro, parking, kuchnia, wlasnosc, stan, material, okna, rynek, opis
    else:
        pass



