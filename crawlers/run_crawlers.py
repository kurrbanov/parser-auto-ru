import os
import logging
import django

from django.db import transaction, DatabaseError, IntegrityError

from crawlers.data_structures import BrandData
from crawlers.crawler_models import ModelCrawler
from crawlers.crawler_generations import GenCrawler
from crawlers.crawler_announcement import AnnouncementCrawler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from parser.models import CarBrand, CarModel, CarGeneration

if __name__ == '__main__':
    brands = [BrandData(brand='BMW', link='https://auto.ru/catalog/cars/bmw/'),
              BrandData(brand='Audi', link='https://auto.ru/catalog/cars/audi/'),
              BrandData(brand='Porsche', link='https://auto.ru/catalog/cars/porsche/'),
              BrandData(brand='Mercedes', link='https://auto.ru/catalog/cars/mercedes/'),
              BrandData(brand='LADA (ВАЗ)', link='https://auto.ru/catalog/cars/vaz/'),
              BrandData(brand='Toyota', link='https://auto.ru/catalog/cars/toyota/')]

    model_crawler = ModelCrawler(brands)
    model_crawler.run()
    models = model_crawler.get_models()

    gen_crawler = GenCrawler(models)
    gen_crawler.run()
    gens = gen_crawler.get_models()

    an_crawler = AnnouncementCrawler(gens)
    an_crawler.run()

    generations = an_crawler.get_models()

    try:
        with transaction.atomic():
            CarGeneration.delete_all()
            CarModel.delete_all()
            CarBrand.delete_all()

            CarBrand.add_brands(brands)
            logging.info("inserting into brands")
            CarModel.add_models(models)
            logging.info("inserting into models")
            CarGeneration.add_generations(generations)
            logging.info("inserting into generations")
    except (DatabaseError, IntegrityError, Exception) as exc:
        logging.error(f"Raised an exception at insert into db: {exc}")
