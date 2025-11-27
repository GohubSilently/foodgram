from .import_data import ImportData
from recipes.models import User


class Command(ImportData):
    model = User
