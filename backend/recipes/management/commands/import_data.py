import csv

from django.core.management import BaseCommand, CommandError
from django.apps import apps
from django.db import transaction


# Можно также установить библиотеку (django-import-export)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Абсолюьный путь до файла'
        )
        parser.add_argument(
            'model_name',
            type=str,
            help='Название модели'
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        model_name = kwargs['model_name']

        model = None
        for app_config in apps.get_app_configs():
            try:
                model = apps.get_model(app_config.label, model_name)
                break
            except Exception as e:
                print(f'{e}')
        if not model:
            raise CommandError(f'Модель - {model_name} не найдена!')

        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                objects = []
                try:
                    for row in reader:
                        object = model(**row)
                        object.full_clean()
                        objects.append(object)
                except Exception as e:
                    print(f'{e}')
            try:
                with transaction.atomic():
                    model.objects.bulk_create(objects)
                    self.stdout.write(self.style.SUCCESS('Данные загружены!'))
            except Exception as e:
                print(f'{e}')
        except Exception as e:
            print(f'{e}')
