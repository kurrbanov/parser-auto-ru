import os
import requests
import logging

from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from bs4 import BeautifulSoup

from crawlers.data_structures import BrandData, ModelData

WORKERS = 12
TIMEOUT = 10

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")


class ModelCrawler:
    def __init__(self, car_lst: List[BrandData]):
        self._car_lst = car_lst
        self._models_lst: List[ModelData] = []
        self.executor = ThreadPoolExecutor(max_workers=WORKERS)
        self.problem_urls: List[str] = []

    @staticmethod
    def retrieve_brands(url) -> str:
        cookies = {"_ym_d": str(os.getenv("_YM_D")), "_ym_uid": str(os.getenv("_YM_UID"))}
        logging.info(f"Send request to: {url}")
        response = requests.get(url, timeout=TIMEOUT, cookies=cookies)
        return response.content.decode('utf-8')

    def run(self):
        with self.executor as executor:
            urls = [car.link for car in self._car_lst]
            futures = []
            future_url_mapping = dict()
            for url in urls:
                future = executor.submit(self.retrieve_brands, url)
                futures.append(future)
                future_url_mapping[future] = url

            for future in as_completed(futures):
                try:
                    html = future.result()
                except Exception as exc:
                    logging.error(f"Generated an exception: {exc} on url: {future_url_mapping[future]}")
                    self.problem_urls.append(future_url_mapping[future])
                else:
                    self.clean_and_create(html)

    def run_sync(self, urls_list):
        for url in urls_list:
            try:
                html = self.retrieve_brands(url)
                self.clean_and_create(html)
            except Exception as exc:
                logging.error(f"Generated an exception: {exc} on url: {url}")

    def clean_and_create(self, html):
        bs = BeautifulSoup(html, "lxml")
        div_header = bs.find("div", {"class": "search-accordion__header"})
        span_brand = div_header.find("a", {"class": "search-form-v2-mmm__breadcrumbs-item_type_mark"})
        div_models = bs.find("div", {"class": "search-form-v2-list_type_popular"})
        a_models = div_models.find_all("a", recursive=True)
        for model in a_models:
            self._models_lst.append(
                ModelData(brand=span_brand.text.strip(), model=model.text, link=model.attrs["href"]))

    def get_models(self):
        self.executor.shutdown(wait=True)
        if self.problem_urls:
            self.run_sync(self.problem_urls)
        return self._models_lst

    def get_models_sync(self):
        return self._models_lst
