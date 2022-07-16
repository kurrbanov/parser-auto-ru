from dataclasses import dataclass
from typing import NamedTuple, Union


class BrandData(NamedTuple):
    brand: str
    link: str


class ModelData(NamedTuple):
    brand: str
    model: str
    link: str


@dataclass
class GenerationData:
    brand: str
    model: str
    generation: str
    body_type: str
    link: str
    id: int
    photo_url: str
    start_year: int
    end_year: int
    average_price: Union[None, int]
    total: Union[None, int]
