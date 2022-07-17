import logging

from django.db import models, connection
from django.utils.translation import gettext_lazy as _

from crawlers.data_structures import BrandData, ModelData, GenerationData


class CarBrand(models.Model):
    brand = models.CharField(max_length=255, verbose_name="Марка")
    link_auto_ru = models.URLField(verbose_name="Ссылка на auto.ru")

    @staticmethod
    def add_brands(brands: list[BrandData]):
        if not brands:
            return None
        values = ', '.join(f"{brand.brand, brand.link}" for brand in brands)
        sql = f"INSERT INTO car_brand(brand, link_auto_ru) VALUES {values};"
        with connection.cursor() as cursor:
            cursor.execute(sql)
        return True

    @staticmethod
    def delete_all():
        sql = "DELETE FROM car_brand WHERE 1 == 1;"
        with connection.cursor() as cursor:
            cursor.execute(sql)
        return True

    def __str__(self):
        return f"{self.brand}"

    class Meta:
        db_table = 'car_brand'


class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, verbose_name="Марка")
    car_model = models.CharField(max_length=255, verbose_name="Модель")
    link_auto_ru = models.URLField(verbose_name="Ссылка на auto.ru")

    @staticmethod
    def add_models(car_models: list[ModelData]):
        if not car_models:
            return None
        CarModel.__clear_data(car_models)
        values = ', '.join(f"{car.model, car.link, car.brand}" for car in car_models)
        sql = f"INSERT INTO car_model (car_model, link_auto_ru, brand_id) VALUES {values};"
        with connection.cursor() as cursor:
            cursor.execute(sql)
        return True

    @staticmethod
    def __clear_data(car_models: list[ModelData]):
        for car in car_models:
            brand_id = CarBrand.objects.get(brand=car.brand)
            car.brand = brand_id.id

    @staticmethod
    def delete_all():
        sql = "DELETE FROM car_model WHERE 1 == 1;"
        with connection.cursor() as cursor:
            cursor.execute(sql)
        return True

    def __str__(self):
        return f"{self.car_model}"

    class Meta:
        db_table = 'car_model'


class CarGeneration(models.Model):
    class BodyType(models.TextChoices):
        SEDAN = 'SEDAN', _('Седан')
        HATCHBACK = 'HATCHBACK', _('Хэтчбек')
        HATCHBACK_3_DOOR = 'HATCHBACK_3_DOORS', _('Хэтчбек 3 дв.')
        HATCHBACK_5_DOOR = 'HATCHBACK_5_DOORS', _('Хэтчбек 5 дв.')
        LIFTBACK = 'LIFTBACK', _('Лифтбек')
        ALLROAD_3_DOOR = 'ALLROAD_3_DOORS', _('Внедорожник 3 дв.')
        ALLROAD_5_DOOR = 'ALLROAD_5_DOORS', _('Внедорожник 5 дв.')
        ALLROAD = 'ALLROAD', _('Внедорожник')
        WAGON = 'WAGON', _('Универсал')
        COUPE = 'COUPE', _('Купе')
        MINIVAN = 'MINIVAN', _('Минивэн')
        PICKUP = 'PICKUP', _('Пикап')
        CABRIO = 'CABRIO', _('Кабриолет')
        VAN = 'VAN', _('Фургон')
        LIMOUSINE = 'LIMOUSINE', _('Лимузин')

    title = models.CharField(max_length=255, verbose_name="Поколение")
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, verbose_name="Модель")
    body_type = models.CharField(choices=BodyType.choices, max_length=25, verbose_name="Тип кузова")
    photo_link = models.URLField(verbose_name="Ссылка на фото")
    auto_ru_link = models.URLField(verbose_name="Ссылка на auto.ru")
    auto_ru_id = models.IntegerField(unique=True, verbose_name="ID поколения на auto.ru")
    start_year = models.IntegerField(verbose_name="Год начала производства")
    end_year = models.IntegerField(verbose_name="Год конеца производства")
    average_price = models.IntegerField(default=0, blank=True, verbose_name="Средняя цена, руб.", null=True)
    total = models.IntegerField(default=0, blank=True, verbose_name='Всего на рынке', null=True)

    @staticmethod
    def add_generations(car_generations: list[GenerationData]):
        if not car_generations:
            return None
        CarGeneration.__clear_data(car_generations)
        values = ', '.join(f"('{car_gen.generation}', '{car_gen.body_type}', '{car_gen.photo_url}', "
                           f"'{car_gen.link}', {car_gen.id}, {car_gen.start_year}, "
                           f"{car_gen.end_year}, {car_gen.average_price}, {car_gen.total}, "
                           f"{car_gen.model})" for car_gen in car_generations)
        sql = f"INSERT INTO car_generation (title, body_type, photo_link, auto_ru_link, auto_ru_id, start_year, " \
              f"end_year, average_price, total, car_model_id) VALUES {values}"
        with connection.cursor() as cursor:
            cursor.execute(sql)
        return True

    @staticmethod
    def __clear_data(car_generations: list[GenerationData]):
        for car in car_generations:
            model_id = CarModel.objects.get(car_model=car.model)
            car.model = model_id.id
            if car.total == 0 or car.average_price == 0 or car.total is None or car.average_price is None:
                car.average_price = 0
                car.total = 0

    @staticmethod
    def delete_all():
        sql = "DELETE FROM car_generation WHERE 1 == 1;"
        with connection.cursor() as cursor:
            cursor.execute(sql)
        return True

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'car_generation'


class CarEngine(models.Model):
    class OilType(models.TextChoices):
        PETROL = 'PETROL', _('Бензин')
        DIESEL = 'DIESEL', _('Дизель')
        HYBRID = 'HYBRID', _('Гибрид')
        GAZ = 'GAZ', _('Газ')
        ELECTRICITY = 'ELECTRICITY', _('Электрический')

    modification = models.CharField(max_length=255, verbose_name="Модификация")
    volume = models.DecimalField(decimal_places=1, max_digits=2, verbose_name="Объём")
    power = models.IntegerField(verbose_name="Мощность л.с.")
    oil_type = models.CharField(choices=OilType.choices, max_length=15, verbose_name="Тип топлива")
    acceleration = models.IntegerField(verbose_name="Разгон до 100 км/ч, сек.")

    def __str__(self):
        return f"{self.volume}"

    class Meta:
        db_table = 'car_engine'


class GenerationEngine(models.Model):
    class GearType(models.TextChoices):
        FORWARD_CONTROL = 'FORWARD_CONTROL', _('Передний')
        REAR_DRIVE = 'REAR_DRIVE', _('Задний')
        ALL_WHEEL_DRIVE = 'ALL_WHEEL_DRIVE', _('Полный')

    class TransmissionType(models.TextChoices):
        AMT = 'AMT', _('Роботизированная')
        AV = 'AV', _('Автоматическая')
        CVT = 'CVT', _('Вариатор')
        MT = 'MT', _('Механическая')

    gen = models.ForeignKey(CarGeneration, on_delete=models.CASCADE, verbose_name="Поколение")
    engine = models.ForeignKey(CarEngine, on_delete=models.CASCADE, verbose_name="Двигатель")
    gear_type = models.CharField(choices=GearType.choices, max_length=20, verbose_name="Привод")
    transmission_type = models.CharField(choices=TransmissionType.choices, max_length=20,
                                         verbose_name="Коробка передач")

    class Meta:
        db_table = 'generation__engine'


class GenerationRegion(models.Model):
    gen = models.ForeignKey(CarModel, on_delete=models.CASCADE, verbose_name="Поколение")
    region = models.ForeignKey('Region', on_delete=models.CASCADE, verbose_name="Регион")
    total = models.IntegerField(verbose_name="Количество")
    average_price = models.IntegerField(verbose_name="Средняя цена в регионе")

    class Meta:
        db_table = 'generation__region'


class Region(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название региона")

    class Meta:
        db_table = 'region'
