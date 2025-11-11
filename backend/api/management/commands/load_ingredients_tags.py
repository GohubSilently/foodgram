import json
from django.core.management.base import BaseCommand
from api.models import Ingredient, Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('/app/data/ingredients.json') as ingredients_file:
            data = json.load(ingredients_file)
            for ingredient in data:
                Ingredient.objects.create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit'],
                )
        with open('/app/data/tags.json') as tags_file:
            data = json.load(tags_file)
            for tag in data:
                Tag.objects.create(
                    name=tag['name'],
                    slug=tag['slug'],
                )
