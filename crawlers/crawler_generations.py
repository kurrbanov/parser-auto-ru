import logging
import os
import django

from bs4 import BeautifulSoup
from datetime import date

from crawlers.data_structures import ModelData, GenerationData
from crawlers.base_crawler import Crawler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from parser.models import CarGeneration


class GenCrawler(Crawler):
    def __init__(self, car_models: list[ModelData]):
        super().__init__(car_models)
        self._car_gens: list[GenerationData] = []

    def clean_and_create(self, html: str):
        bs = BeautifulSoup(html, "lxml")
        brand = bs.find('a', {'class': 'search-form-v2-mmm__breadcrumbs-item_type_mark'}).text.strip()
        model = bs.find('a', {'class': 'search-form-v2-mmm__breadcrumbs-item_type_model'}).text.strip()
        all_data = bs.find('dl', {'class': 'catalog-all-text-list_view_generations'})
        all_titles = all_data.find_all('dt', {'class': 'catalog-all-text-list__title'})
        all_gens_body_images = all_data.findAll('dd', {'class': 'catalog-all-text-list__desc'})

        for gen_idx, title in enumerate(all_titles):
            try:
                start_year, end_year, generation = self.clear_year(title)
                body_type, photo_url, link = self.clear_gen(all_gens_body_images[gen_idx])
                self._car_gens.append(GenerationData(brand=brand,
                                                     model=model,
                                                     generation=generation,
                                                     start_year=start_year,
                                                     end_year=end_year,
                                                     body_type=body_type,
                                                     link=link,
                                                     id=int(link.split('/')[-3]),
                                                     photo_url=photo_url,
                                                     average_price=None,
                                                     total=None))
            except (AttributeError, Exception) as exc:
                logging.error(f"Generated exception: {exc}")

    @staticmethod
    def clear_year(title_year) -> tuple[int, int, str]:
        start_year, _, end_year = title_year.text[:11].split()
        generation = title_year.text[11:]
        if end_year == 'н.в.':
            end_year = date.today().year
        start_year, end_year = int(start_year), int(end_year)
        return start_year, end_year, generation

    @staticmethod
    def clear_gen(gen_cards: BeautifulSoup) -> tuple[str, str, str]:
        a = gen_cards.find('a', {'class': 'mosaic__title'})
        photo_url = f"https://{gen_cards.find('div', {'class': 'mosaic__image-inner'}).attrs['style'][24:-2]}"
        link = a.attrs['href']
        body_types = CarGeneration().BodyType.labels
        for body_type in body_types:
            if a.text.startswith(str(body_type)):
                body_type_name = body_type
                break
        else:
            if a.text.startswith('Родстер') or a.text.startswith('Спидстер'):
                body_type_name = CarGeneration().BodyType.CABRIO.label
            elif a.text.startswith('Внедорожник'):
                body_type_name = CarGeneration().BodyType.ALLROAD.label
            elif a.text.startswith('Хэтчбек'):
                body_type_name = CarGeneration().BodyType.HATCHBACK.label
            else:
                raise ValueError(f"Тип кузова не существует: {a.text}")
        return body_type_name, photo_url, link

    def get_models(self):
        super().get_models()
        return self._car_gens
