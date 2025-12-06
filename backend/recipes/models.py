from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import (
    RegexValidator, MinValueValidator
)
from django.db import models

from .constants import MIN_AMOUNT, MIN_COOKING_TIME, USERNAME_REGEX


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(USERNAME_REGEX)],
        verbose_name='Ник'
    )
    email = models.EmailField(
        max_length=254, unique=True, verbose_name='Почта'
    )
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='users/', verbose_name='Аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('email',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.email} - {self.username}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authors',
        verbose_name='Подписка'
    )

    def clean(self):
        if self.user_id == self.author_id:
            raise ValidationError("Нельзя подписаться на самого себя.")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subsribtion',
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} - {self.author}'


class Tag(models.Model):
    name = models.CharField(
        max_length=32, unique=True, help_text='Имя',
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name} - {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения'
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
    name = models.CharField(
        max_length=256, verbose_name='Название'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME)],
        verbose_name='Время приготовления',
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Время создания'
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты'
    )
    image = models.ImageField(verbose_name='Фото', upload_to='recipes')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return f'{self.name} - {self.author}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(MIN_AMOUNT)],
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
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return f'{self.ingredient.name} — {self.amount}'


class RecipeUserRelation(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_%(class)s',
            )
        ]
        default_related_name = '%(class)ss'

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(RecipeUserRelation):
    class Meta(RecipeUserRelation.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favorite(RecipeUserRelation):
    class Meta(RecipeUserRelation.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
