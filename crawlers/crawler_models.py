import logging

from typing import List
from bs4 import BeautifulSoup

from crawlers.data_structures import BrandData, ModelData
from crawlers.base_crawler import Crawler


class ModelCrawler(Crawler):
    def __init__(self, car_lst: List[BrandData]):
        super().__init__(car_lst)
        self._models_lst: List[ModelData] = []

    def clean_and_create(self, html: str):
        bs = BeautifulSoup(html, "lxml")
        try:
            div_header = bs.find("div", {"class": "search-accordion__header"})
            span_brand = div_header.find("a", {"class": "search-form-v2-mmm__breadcrumbs-item_type_mark"})
            div_models = bs.find("div", {"class": "search-form-v2-list_type_popular"})
            a_models = div_models.find_all("a", recursive=True)
            for model in a_models:
                self._models_lst.append(
                    ModelData(brand=span_brand.text.strip(), model=model.text, link=model.attrs["href"]))
        except AttributeError as exc:
            logging.error(f"Generated an exception: {exc}")

    def get_models(self):
        self._executor.shutdown(wait=True)
        if self._problem_urls:
            self.run_sync(self._problem_urls)
        return self._models_lst

    def get_models_sync(self):
        return self._models_lst
