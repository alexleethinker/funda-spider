from requests_html import HTMLSession
import pandas as pd
from tqdm import tqdm


def fetch_search_page(page):
    url = base_url + 'p' + str(page)
    r = session.get(url)

    address = []
    for i in r.html.find('h2.search-result__header-title'):
        address.append(i.text)

    href = []
    for i in r.html.find('div.search-result__header-title-col>a:first-child[data-object-url-tracking="resultlist"]'):
        href.append(i.attrs['href'])

    zip_code = []
    city = []
    for i in r.html.find('h4.search-result__header-subtitle'):
        if len(i.text.split(' ', 2)) == 3:
            zip_code.append(i.text.split(' ', 2)[0] + ' ' + i.text.split(' ', 2)[1])
            city.append(i.text.split(' ', 2)[2])
        elif len(i.text.split(' ', 2)) == 2:
            zip_code.append(i.text.split(' ', 2)[0])
            city.append(i.text.split(' ', 2)[1])
        else:
            zip_code.append(i.text)
            city.append('unknown')

    price = []
    for i in r.html.find('div.search-result-content-inner div.search-result-info:nth-of-type(2)>span.search-result-price'):
        try:
            price.append(i.text.split(' ')[1].replace(',',''))
        except:
            price.append(i.text)

    living_area = []
    for i in r.html.find('ul.search-result-kenmerken'):
        living_area.append(i.text.replace('\n',';'))

    agency = []
    for i in r.html.find('span.search-result-makelaar-name'):
        agency.append(i.text)

    agency_href = []
    for i in r.html.find('a.search-result-makelaar'):
        agency_href.append(i.attrs['href'])

    funda_df = pd.DataFrame()
    funda_df['address'] = address
    funda_df['type'] = woon_type
    funda_df['zip_code'] = zip_code
    funda_df['city'] = city
    funda_df['price'] = price
    funda_df['price'] = pd.to_numeric(funda_df['price'], errors='coerce').fillna('0').astype(int)
    funda_df['living_area'] = living_area
    funda_df['href'] = href
#     funda_df['agency'] = agency
#     funda_df['agency_href'] = agency_href

    import os
    if not os.path.isfile(woon_type + '_' + status +'.csv'):
       funda_df.to_csv(woon_type + '_' + status +'.csv', mode='a', index = False, encoding = 'utf-8')
    else: 
       funda_df.to_csv(woon_type + '_' + status +'.csv', mode='a', index = False, encoding = 'utf-8', header = False)


if __name__ == '__main__':
    session = HTMLSession()
    
    # type = ['appartement','woonhuis']
    woon_type = 'woonhuis'
    # status = ['beschikbaar','in-onderhandeling','verkocht']
    status = 'verkocht'

    base_url = 'https://www.funda.nl/en/koop/heel-nederland/' + status + '/' + woon_type + '/sorteer-datum-op/'
    r = session.get(base_url)
    max_page = int(r.html.find('a', containing='page')[0].attrs['data-pagination-page'])

    for page in tqdm(range(1 , max_page + 1), desc = status + '-' + woon_type):
        fetch_search_page(page)
    