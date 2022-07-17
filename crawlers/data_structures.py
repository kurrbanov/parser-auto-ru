from dataclasses import dataclass
from typing import Union


@dataclass
class BrandData:
    brand: str
    link: str


@dataclass
class ModelData:
    brand: Union[str, int]
    model: str
    link: str


@dataclass
class GenerationData:
    brand: str
    model: Union[str, int]
    generation: str
    body_type: str
    link: str
    id: int
    photo_url: str
    start_year: int
    end_year: int
    average_price: Union[None, int]
    total: Union[None, int]
