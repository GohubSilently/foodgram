from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    RegexValidator, MinValueValidator
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import MIN_AMOUNT, MIN_COOKING_TIME, USERNAME_REGEX


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(USERNAME_REGEX)],
        help_text='Ник',
        verbose_name=_('Авторы')
    )
    email = models.EmailField(max_length=254, unique=True, help_text='Почта')
    first_name = models.CharField(max_length=150, help_text='Имя')
    last_name = models.CharField(max_length=150, help_text='Фамилия')
    avatar = models.ImageField(upload_to='users/', help_text='Аватар')

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
        help_text='Пользователь'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authors',
        help_text='Подписка'
    )

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
        verbose_name=_('Теги')
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        help_text='Идентификатор'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name} - {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(max_length=128, help_text='Имя')
    measurement_unit = models.CharField(
        max_length=64, help_text='Единица измерения',
        verbose_name=_('Единица измерения'),
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
        max_length=256, help_text='Имя'
    )
    text = models.TextField(help_text='Описание')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME)],
        help_text='Время приготовления',
    )
    image = models.ImageField(help_text='Фото', upload_to='recipes')
    created_at = models.DateTimeField(
        auto_now_add=True, help_text='Время создания'
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Автор'
    )
    tags = models.ManyToManyField(Tag, help_text='Теги')
    ingredients = models.ManyToManyField(Ingredient, help_text='Ингредиенты')

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
        help_text='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        help_text='Рецепт'
    )
    amount = models.PositiveIntegerField(
        help_text='Рецепт',
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
        Recipe, on_delete=models.CASCADE, help_text='Рецепт'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Пользователь'
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
