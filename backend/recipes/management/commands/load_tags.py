from .import_data import ImportData
from recipes.models import Tag


class Command(ImportData):
    model = Tag
