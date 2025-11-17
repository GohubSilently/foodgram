from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import tag_validator


CustomUser = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True, help_text='Имя')
    slug = models.SlugField(
        max_length=32, validators=[tag_validator], unique=True,
        help_text='Слаг'
    )

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
    measurement_unit = models.CharField(
        max_length=64, help_text='Единица измерения'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            )
        ]
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(max_length=256, help_text='Имя')
    text = models.TextField(help_text='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        help_text='Время приготовления'
    )
    image = models.ImageField(help_text='Фото', upload_to='recipes')
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(Ingredient)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return f'{self.name} - {self.author}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        help_text='Рецепт'
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        help_text='Рецепт'
    )
    amount = models.PositiveIntegerField(
        help_text='Рецепт',
        validators=[MinValueValidator(0), MaxValueValidator(5000)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.ingredient.name} — {self.amount}'


class FavoriteShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, help_text='Рецепт'
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, help_text='Пользователь'
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)s'

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(FavoriteShoppingCart, models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_cart',
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favorite(FavoriteShoppingCart, models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite',
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
