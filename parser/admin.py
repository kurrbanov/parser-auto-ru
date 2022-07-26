from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.html import mark_safe

from parser.models import CarGeneration


@admin.register(CarGeneration)
class CarGenerationAdmin(ModelAdmin):
    list_display = ('image_car', '__str__', 'average_price', 'total', 'auto_ru_link')

    def image_car(self, obj: CarGeneration):
        return mark_safe(f'<img src="{obj.photo_link}" width="300px" height="200px">')
