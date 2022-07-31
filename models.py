from pydantic import BaseModel, Field
from typing import List


class Author(BaseModel):
    name: str


class Book(BaseModel):
    title: str
    authors: List[Author]
