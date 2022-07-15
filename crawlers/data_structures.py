from typing import NamedTuple


class BrandData(NamedTuple):
    brand: str
    link: str


class ModelData(NamedTuple):
    brand: str
    model: str
    link: str


class GenerationData(NamedTuple):
    brand: str
    model: str
    generation: str
    body_type: str
    link: str
    photo_url: str
    start_year: int
    end_year: int
