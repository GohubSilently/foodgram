from .import_data import ImportData
from recipes.models import Ingredient


class Command(ImportData):
    model = Ingredient
