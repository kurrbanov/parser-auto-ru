import requests
import os
import django
import logging

from concurrent.futures import ThreadPoolExecutor, as_completed

from bs4 import BeautifulSoup

from crawlers.data_structures import GenerationData

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from parser.models import CarGeneration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")


class AnnouncementCrawler:
    base_link = 'https://auto.ru/rossiya/cars/'
    timeout = 5
    workers = 12

    def __init__(self, car_generations: list[GenerationData]):
        self._car_generations = car_generations
        self._links_car: list[tuple[str, GenerationData]] = []
        self._executor: ThreadPoolExecutor = ThreadPoolExecutor(self.workers)

    def __generate_links(self):
        body_types = CarGeneration().BodyType
        for car_gen in self._car_generations:
            url = f"{self.base_link}{car_gen.link.split('/')[-5]}/{car_gen.link.split('/')[-4]}/{car_gen.id}" \
                  f"/all/?body_type_group="
            if car_gen.body_type == str(body_types.HATCHBACK.label):
                url = url + f"{str(body_types.HATCHBACK.value)}" \
                            f"&body_type_group={str(body_types.HATCHBACK_3_DOOR.value)}" \
                            f"&body_type_group={str(body_types.HATCHBACK_5_DOOR.value)}" \
                            f"&body_type_group={str(body_types.LIFTBACK.value)}"
            elif car_gen.body_type == str(body_types.ALLROAD.LIFTBACK.label):
                url = url + f"{str(body_types.ALLROAD.value)}" \
                            f"&body_type_group={str(body_types.ALLROAD_3_DOOR.value)}" \
                            f"&body_type_group={str(body_types.ALLROAD_5_DOOR.value)}"
            else:
                for eng, rus in body_types.choices:
                    if car_gen.body_type == str(rus):
                        url += str(eng)

            logger.info(f"GENERATED LINK: {url}")
            self._links_car.append((url, car_gen))

    def retrieve_sell_page(self, url):
        cookies = {"_ym_d": str(os.getenv("_YM_D")), "_ym_uid": str(os.getenv("_YM_UID"))}
        response = requests.get(url, timeout=self.timeout, cookies=cookies)
        logging.info(f"Send request to {url}")
        if response.status_code == 404:
            logging.info(f"{url} doesn't exist")
            return None
        return response.content.decode('utf-8')

    def run(self):
        self.__generate_links()
        with self._executor as executor:
            futures = []
            future_url_mapping = dict()
            for url, car in self._links_car:
                future = executor.submit(self.retrieve_sell_page, url)
                futures.append(future)
                future_url_mapping[future] = (url, car)

            for future in as_completed(futures):
                try:
                    html = future.result()
                except Exception as exc:
                    logging.error(f"Generated an exception: {exc} on url: {future_url_mapping[future][0]}")
                else:
                    if html is None:
                        continue
                    self.clean_and_create(html, future_url_mapping[future][1])

    @staticmethod
    def clean_and_create(html, car: GenerationData):
        bs = BeautifulSoup(html, "lxml")
        try:
            car_cards = bs.find_all('div', {'class': 'ListingItem'})
            prices = bs.find_all('div', {'class': 'ListingItemPrice__content'})
            total_quantity = 0
            total_price = 0
            for price_idx, card in enumerate(car_cards):
                total_price += int(
                    prices[price_idx].text.replace('\xa0', '').replace('₽', '').replace('от', '').replace('до',
                                                                                                          '').strip())
                total_quantity += 1
            if total_quantity > 0:
                car.average_price = int(total_price / total_quantity)
            car.total = total_quantity
        except AttributeError:
            pass

    def get_models(self):
        self._executor.shutdown(wait=True)
        return self._car_generations
