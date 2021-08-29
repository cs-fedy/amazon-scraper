from typing import Any, Dict, List, Tuple
import requests
from bs4 import BeautifulSoup
import re
import json
from os import path


def get_page_content(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    print(f'+++ requesting {url}')
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    raise Exception("error while extracting data", response.status_code)

def save_data(data: Dict) -> None:
    if not path.isfile(r'data.json'):
        with open(r'data.json', 'w') as file:
            json.dump({ 'data': [data] }, file)
        return
    with open(r'data.json', 'r') as file:
        file_data = json.load(file)
        file_data['data'].append(data)

    with open(r'data.json', mode='w') as file:
        json.dump(file_data, file)


class ScrapeProductData:
    def __init__(self, url) -> None:
        self.url = url
        html_page = get_page_content(url)
        self.soup = BeautifulSoup(html_page, 'html.parser')

    def __get_product_title(self) -> str:
        title_element = self.soup.select_one('#title_feature_div h1')
        return title_element.get_text().strip()

    def __get_product_price(self) -> str:
        price_element = self.soup.select_one('#priceblock_ourprice')
        return price_element.get_text().strip()

    def __get_product_rate(self) -> str:
        rate_element = self.soup.select_one('#acrPopover')
        return rate_element['title']

    def __get_product_rate_count(self) -> str:
        rate_count_element = self.soup.select_one('#acrCustomerReviewText')
        return rate_count_element.get_text().strip()

    def __get_product_description(self) -> List[str]:
        description_element = self.soup.select('#feature-bullets ul .a-list-item')
        return [child.get_text().strip() for child in description_element]


    def __get_product_overview(self) -> Dict[str, str]:
        overview_element = self.soup.select('#productOverview_feature_div tr')
        overview = {}
        for child in overview_element:
            row_data = child.findChildren('span')
            key = row_data[0].get_text().strip()
            value = row_data[1].get_text().strip()
            overview[key] = value
        return overview

    def __get_product_pictures(self) -> str:
        pictures_script = self.soup.select_one('#imageBlock').findNextSibling('script')
        return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', pictures_script.string)[0]

    def __get_product_category(self) -> List[str]:
        categories_element = self.soup.select('#wayfinding-breadcrumbs_feature_div ul li')
        return [
            child.get_text().strip() 
            for child in categories_element 
            if 'class' not in child.attrs or 'a-breadcrumb-divider' not in child.attrs['class'] 
        ]

    def get_data(self) -> Dict[str, Any]:
        try:
            availability_element = self.soup.find(id='availability')
            if 'Currently unavailable' in availability_element.get_text():
                return {}
        except:
            pass

        return {
            'url': self.url,
            'title': self.__get_product_title(),
            'price': self.__get_product_price(),
            'rate': self.__get_product_rate(),
            'rate_count': self.__get_product_rate_count(),
            'description': self.__get_product_description(),
            'overview': self.__get_product_overview(),
            'picture': self.__get_product_pictures(),
            'categories': self.__get_product_category()
        }


class ScrapeAmazonProducts:
    def __init__(self, urls: List[str]) -> None:
        self.urls = urls
    def get_data(self) -> None:
        for url in self.urls:
            scraper = ScrapeProductData(url)
            save_data(scraper.get_data())


if __name__ == '__main__':
    urls = [
        #! products urls here
    ]
    scraper = ScrapeAmazonProducts(urls)
    scraper.get_data()


# TODO: fix get overview