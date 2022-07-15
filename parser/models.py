from django.db import models
from django.utils.translation import gettext_lazy as _


class CarBrand(models.Model):
    brand = models.CharField(max_length=255, verbose_name="Марка")
    link_auto_ru = models.URLField(verbose_name="Ссылка на auto.ru")

    def __str__(self):
        return f"{self.brand}"

    class Meta:
        db_table = 'car_brand'


class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, verbose_name="Марка")
    car_model = models.CharField(max_length=255, verbose_name="Модель")
    link_auto_ru = models.URLField(verbose_name="Ссылка на auto.ru")

    def __str__(self):
        return f"{self.car_model}"

    class Meta:
        db_table = 'car_model'


class CarGeneration(models.Model):
    class BodyType(models.TextChoices):
        SEDAN = 'SEDAN', _('Седан')
        HATCHBACK = 'HATCHBACK', _('Хэтчбек')
        HATCHBACK_3_DOOR = 'HATCHBACK_3_DOOR', _('Хэтчбек 3 дв.')
        HATCHBACK_5_DOOR = 'HATCHBACK_5_DOOR', _('Хэтчбек 5 дв.')
        LIFTBACK = 'LIFTBACK', _('Лифтбек')
        ALLROAD_3_DOOR = 'ALLROAD_3_DOOR', _('Внедорожник 3 дв.')
        ALLROAD_5_DOOR = 'ALLROAD_5_DOOR', _('Внедорожник 5 дв.')
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
    average_price = models.IntegerField(default=0, blank=True, verbose_name="Средняя цена, руб.")
    total = models.IntegerField(default=0, blank=True, verbose_name='Всего на рынке')

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
