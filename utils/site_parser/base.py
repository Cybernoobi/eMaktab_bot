from bs4 import BeautifulSoup
import requests


# https://

class BaseParser:
    BASE_URL = "https://kinogo.biz"

    def get_soup(self, url=BASE_URL):
        html = requests.get(url).text
        return BeautifulSoup(html, "html.parser")

