import os
import requests

from typing import List, NamedTuple

from bs4 import BeautifulSoup

BASE_LINK = 'https://auto.ru/catalog/cars/'


class BrandData(NamedTuple):
    brand: str
    link: str


def get_car_list() -> List[NamedTuple]:
    """
    Get the html from catalog and parse it.
    return: the List of BrandData(brand: str, link: str)
    """
    response = requests.get(BASE_LINK, cookies={"_ym_d": str(os.getenv("_YM_D")), "_ym_uid": str(os.getenv("_YM_UID"))})
    html = response.content.decode('utf-8')
    bs = BeautifulSoup(html, "html.parser")
    div_car_lst = bs.find("div", {"class": "search-form-v2-list_type_all"})
    a_cars = div_car_lst.find_all("a", recursive=True)
    return [BrandData(car.text, car.attrs['href']) for car in a_cars]
