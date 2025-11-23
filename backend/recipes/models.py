from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    RegexValidator, MaxValueValidator, MinValueValidator
)
from django.db import models


class User(AbstractUser):
    # Так как я не переопределяю username - у него уже есть валидаци.
    email = models.EmailField(max_length=254, unique=True)
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
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers'
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
    name = models.CharField(max_length=32, unique=True, help_text='Имя')
    slug = models.SlugField(
        max_length=32,
        validators=[RegexValidator(
            regex='^[-a-zA-Z0-9_]+$',
            message='Некоретктный ник',
            code='invalid_username'
            )
        ],
        unique=True,
        help_text='Уникальный идентификатор'
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
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(525600)],
        help_text='Время приготовления'
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
        related_name='recipe_ingredients',
        help_text='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        help_text='Рецепт'
    )
    amount = models.PositiveIntegerField(
        help_text='Рецепт',
        validators=[MinValueValidator(1)]
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


class RecipeInteraction(models.Model):
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


class ShoppingCart(RecipeInteraction):
    class Meta(RecipeInteraction.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favorite(RecipeInteraction):
    class Meta(RecipeInteraction.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'