import json
from django.core.management import BaseCommand


class ImportData(BaseCommand):
    model = None

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Абсолюьный путь до файла'
        )

    def handle(self, *args, **kwargs):
        try:
            with open(kwargs['json_file'], 'r') as file:
                data = self.model.objects.bulk_create(
                    [self.model(**row) for row in json.load(file)],
                    ignore_conflicts=True
                )

                self.stdout.write(self.style.SUCCESS(
                    f'Загружено {len(data)}, '
                    f'{self.model._meta.verbose_name}а!\n'
                    f'Из файла {file.name}'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка {e}\n'
            ))
