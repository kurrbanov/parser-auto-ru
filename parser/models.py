from django.db import models


class CarBrand(models.Model):
    brand = models.CharField(max_length=255, verbose_name="Марка")
    link_auto_ru = models.URLField(verbose_name="Ссылка на auto.ru")

    def __str__(self):
        return f"{self.brand}"


class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, verbose_name="Марка")
    car_model = models.CharField(max_length=255, verbose_name="Модель")
    link_auto_ru = models.URLField(verbose_name="Ссылка на auto.ru")

    def __str__(self):
        return f"{self.car_model}"


class CarGeneration(models.Model):
    class BodyType(models.TextChoices):
        SEDAN = 'SEDAN', 'Седан'
        HATCHBACK_3_DOOR = 'HATCHBACK_3_DOOR', 'Хэтчбэк 3 дв.'
        HATCHBACK_5_DOOR = 'HATCHBACK_5_DOOR', 'Хэтчбэк 5 дв.'
        LIFTBACK = 'LIFTBACK', 'Лифтбэк'
        ALLROAD_3_DOOR = 'ALLROAD_3_DOOR', 'Внедорожник 3 дв.'
        ALLROAD_5_DOOR = 'ALLROAD_5_DOOR', 'Внедорожник 5 дв.'
        WAGON = 'WAGON', 'Универсал'
        COUPE = 'COUPE', 'Купе'
        MINIVAN = 'MINIVAN', 'Минивэн'
        PICKUP = 'PICKUP', 'Пикап'
        CABRIO = 'CABRIO', 'Кабриолет'
        VAN = 'VAN', 'Фургон'
        LIMOUSINE = 'LIMOUSINE', 'Лимузин'

    title = models.CharField(max_length=255, verbose_name="Поколение")
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, verbose_name="Модель")
    body_type = models.CharField(choices=BodyType.choices, max_length=25, verbose_name="Тип кузова")
    photo_link = models.URLField(verbose_name="Ссылка на фото")
    start_year = models.IntegerField(verbose_name="Год начала производства")
    end_year = models.IntegerField(verbose_name="Год конеца производства")
    places = models.IntegerField(verbose_name="Количество мест")
    average_price = models.IntegerField(default=0, blank=True, verbose_name="Средняя цена, руб.")
    total = models.IntegerField(default=0, blank=True, verbose_name='Всего на рынке')

    def __str__(self):
        return f"{self.title}"


class CarEngine(models.Model):
    class OilType(models.TextChoices):
        PETROL = 'PETROL', 'Бензин'
        DIESEL = 'DIESEL', 'Дизель'
        HYBRID = 'HYBRID', 'Гибрид'
        GAZ = 'GAZ', 'Газ'
        ELECTRICITY = 'ELECTRICITY', 'Электрический'

    volume = models.DecimalField(decimal_places=1, max_digits=2, verbose_name="Объём")
    power = models.IntegerField(verbose_name="Мощность л.с.")
    oil_type = models.CharField(choices=OilType.choices, max_length=15, verbose_name="Тип топлива")
    acceleration = models.IntegerField(verbose_name="Разгон до 100 км/ч, сек.")

    def __str__(self):
        return f"{self.volume}"


class GenerationEngine(models.Model):
    class GearType(models.TextChoices):
        FORWARD_CONTROL = 'FORWARD_CONTROL', 'Передний'
        REAR_DRIVE = 'REAR_DRIVE', 'Задний'
        ALL_WHEEL_DRIVE = 'ALL_WHEEL_DRIVE', 'Полный'

    class TransmissionType(models.TextChoices):
        AMT = 'AMT', 'Роботизированная'
        AV = 'AV', 'Автоматическая'
        CVT = 'CVT', 'Вариатор'
        MT = 'MT', 'Механическая'

    gen = models.ForeignKey(CarGeneration, on_delete=models.CASCADE, verbose_name="Поколение")
    engine = models.ForeignKey(CarEngine, on_delete=models.CASCADE, verbose_name="Двигатель")
    gear_type = models.CharField(choices=GearType.choices, max_length=20, verbose_name="Привод")
    transmission_type = models.CharField(choices=TransmissionType.choices, max_length=20,
                                         verbose_name="Коробка передач")


class GenerationRegion(models.Model):
    gen = models.ForeignKey(CarModel, on_delete=models.CASCADE, verbose_name="Поколение")
    region = models.CharField(max_length=255, verbose_name="Регион")
    total = models.IntegerField(verbose_name="Количество")
