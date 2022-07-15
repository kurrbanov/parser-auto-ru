import os
import requests
import logging

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union

from crawlers.data_structures import ModelData, BrandData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")


class Crawler:
    workers = os.cpu_count() * 3
    timeout = 5

    def __init__(self, cars: list[Union[BrandData, ModelData]]):
        self._cars: list[Union[BrandData, ModelData]] = cars
        self._executor = ThreadPoolExecutor(max_workers=self.workers)
        self._problem_urls: list[str] = []

    def retrieve_data(self, url: str):
        cookies = {"_ym_d": str(os.getenv("_YM_D")), "_ym_uid": str(os.getenv("_YM_UID"))}
        logging.info(f"Send request to: {url}")
        response = requests.get(url, timeout=self.timeout, cookies=cookies)
        return response.content.decode('utf-8')

    def run(self):
        with self._executor as executor:
            urls = [car.link for car in self._cars]
            futures = []
            future_url_mapping = dict()
            for url in urls:
                future = executor.submit(self.retrieve_data, url)
                futures.append(future)
                future_url_mapping[future] = url

            for future in as_completed(futures):
                try:
                    html = future.result()
                except Exception as exc:
                    logging.error(f"Generated an exception: {exc} on url: {future_url_mapping[future]}")
                    self._problem_urls.append(future_url_mapping[future])
                else:
                    self.clean_and_create(html)

    def run_sync(self, urls_list):
        for url in urls_list:
            try:
                html = self.retrieve_data(url)
                self.clean_and_create(html)
            except Exception as exc:
                logging.error(f"Generated an exception: {exc} on url: {url}")

    def clean_and_create(self, html):
        raise NotImplemented

    def get_models(self):
        self._executor.shutdown(wait=True)
        if self._problem_urls:
            self.run_sync(self._problem_urls)
