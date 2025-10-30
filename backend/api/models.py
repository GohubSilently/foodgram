from django.db import models

from .validators import tag_validator

class Tag(models.Model):
    name = models.CharField(max_length=32, help_text='Имя')
    slug = models.SlugField(max_length=32, validators=[tag_validator], help_text='Слаг')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug'],
                name='unique_tag',
            )
        ]
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name} - {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(max_length=128, help_text='Имя')
    measurement_unit = models.CharField(max_length=64, help_text='Единица измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'