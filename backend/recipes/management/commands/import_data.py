import json
import os

from django.conf import settings
from django.core.management import BaseCommand


class ImportData(BaseCommand):
    model = None

    def handle(self, *args, **kwargs):
        file = os.path.join(
            settings.BASE_DIR, 'data', f'{self.model.__name__.lower()}s.json'
        )
        try:
            with open(file, 'r') as file:
                database_records = self.model.objects.bulk_create(
                    (self.model(**row) for row in json.load(file)),
                    ignore_conflicts=True
                )

                self.stdout.write(self.style.SUCCESS(
                    f'Загружено {len(database_records)}, '
                    f'{self.model._meta.verbose_name}а!\n'
                    f'Из файла {file.name}'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка {e}\n'
                f'Файл {file.name}\n'
            ))
