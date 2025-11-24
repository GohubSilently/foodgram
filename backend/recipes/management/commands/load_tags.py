import json

from django.core.management import BaseCommand

from recipes.models import Tag


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

            ingredients = Tag.objects.bulk_create(
                [Tag(**row) for row in data],
                ignore_conflicts=True
            )

            self.stdout.write(self.style.SUCCESS(
                f'Загружено {len(ingredients)} тега!')
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка {e}'))
