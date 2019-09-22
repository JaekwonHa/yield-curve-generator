import urllib.request
from bs4 import BeautifulSoup
import common


def get_yield_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    url_path = "https://kr.investing.com/rates-bonds/world-government-bonds"
    req = urllib.request.Request(url=url_path, headers=headers)
    data = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(data, 'html.parser')

    yield_data = {}

    for country in common.COUNTRIES:
        country_data = {}
        for year_step in common.YIELD_STEPS:
            title = country + " " + year_step

            result = soup.find(title=title)
            if result is not None:
                result = result.parent
                if result is not None:
                    result = result.next_sibling
                    country_data[year_step] = result.contents[0]
        yield_data[country] = country_data
    #print(yield_data)
    return yield_data
