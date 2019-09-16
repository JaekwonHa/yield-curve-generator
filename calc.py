import urllib.request
from bs4 import BeautifulSoup

united_state = "미국"
column = ['3개월', '6개월', '1년', '2년', '3년', '5년', '10년']

def getData():

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    url_path = "https://kr.investing.com/rates-bonds/world-government-bonds"
    req = urllib.request.Request(url=url_path, headers=headers)
    data = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(data, 'html.parser')

    # print(soup.prettify())

    result = []

    for period in column:
        title = united_state + " " + period
        print(title)
        # price = soup.find(title=title).find_parent("td").find_next_sibling("td")
        price = soup.find(title=title).parent.next_sibling
        print(price.contents[0])
        result.append([title, price.contents[0]])

    return result







