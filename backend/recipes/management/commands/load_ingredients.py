import json

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Абсолюьный путь до файла'
        )

    def handle(self, *args, **kwargs):
        try:
            with open(kwargs['json_file'], 'r') as file:
                data = json.load(file)

            ingredients = Ingredient.objects.bulk_create(
                [Ingredient(**row) for row in data],
                ignore_conflicts=True
            )

            self.stdout.write(self.style.SUCCESS(
                f'Загружено {len(ingredients)} ингредиентов!')
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка {e}'))
