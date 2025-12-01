from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import (
    Ingredient, Tag, Recipe, User, Subscription, ShoppingCart, Favorite,
    RecipeIngredient
)


admin.site.unregister(Group)


class Mixin:
    list_display = ('id', 'display_name', 'recipes_count',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipes_count=Count('recipes')
        )

    @admin.display(description='В рецептах')
    def recipes_count(self, obj):
        return obj.recipes_count

    @admin.display(description='Название')
    def display_name(self, obj):
        return f'{obj.name}'

    @admin.display(description='Идентификатор')
    def display_slug(self, tag):
        return f'{tag.slug}'


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'cooking time'
    parameter_name = 'cooking_time'

    TRESHOLD_1 = 60
    TRESHOLD_2 = 1440
    MAX_TIME = 60 * 24 * 365

    RANGES = {
        '1': ((0, TRESHOLD_1), 'Меньше одного часа'),
        '2': ((TRESHOLD_1 + 1, TRESHOLD_2), 'От одного часа до 24 часов'),
        '3': ((TRESHOLD_2 + 1, 525600), 'Больше 24 часов'),
    }

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)

        recipes = []
        for key, (range_time, text) in self.RANGES.items():
            start, end = range_time
            count = queryset.filter(cooking_time__range=(start, end)).count()
            recipes.append((key, f'{text} ({count})'))
        return recipes

    def queryset(self, request, queryset):
        if self.value() in self.RANGES:
            return queryset.filter(
                cooking_time__range=(self.RANGES[self.value()])
            )
        return queryset


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Tag)
class TagAdmin(Mixin, admin.ModelAdmin):
    list_display = (*Mixin.list_display, 'display_slug')

    @admin.display(description='Идентификатор')
    def display_slug(self, tag):
        return f'{tag.slug}'


@admin.register(Ingredient)
class IngredientAdmin(Mixin, admin.ModelAdmin):
    list_display = (*Mixin.list_display, 'display_measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Меры измерения')
    def display_measurement_unit(self, ingredient):
        return f'{ingredient.measurement_unit}'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = (
        'id', 'display_name', 'display_author', 'display_cooking_time',
        'display_tags', 'display_ingredients', 'display_favorites',
        'display_image',
    )
    list_select_related = ('author',)
    list_filter = ('author__username', 'tags__name', CookingTimeFilter)
    search_fields = (
        'name', 'author__username', 'tags__name', 'ingredients__name'
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            display_favorite=Count('favorites')
        ).prefetch_related(
            'tags', 'ingredients'
        )
        return queryset

    @admin.display(description='Название')
    def display_name(self, recipe):
        return f'{recipe.name}'

    @admin.display(description='Автор')
    def display_author(self, recipe):
        return f'{recipe.author}'

    @admin.display(description='Время приготовления')
    def display_cooking_time(self, recipe):
        return f'{recipe.cooking_time}'

    @admin.display(description='Избранное')
    def display_favorites(self, favorites):
        return favorites.display_favorite

    @admin.display(description='Теги')
    @mark_safe
    def display_tags(self, tag):
        return '<br>'.join(tag.name for tag in tag.tags.all())

    @admin.display(description='Ингредиенты')
    @mark_safe
    def display_ingredients(self, ingredient):
        return '<br>'.join(
            f'{ingredient.ingredient.name} ({ingredient.amount} '
            f'{ingredient.ingredient.measurement_unit})'
            for ingredient in ingredient.recipe_ingredients.select_related(
                'ingredient'
            )
        )

    @admin.display(description='Фото')
    @mark_safe
    def display_image(self, recipe):
        return f'<img src="{recipe.image.url}" height="100" width="100">'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    list_select_related = ('recipe', 'ingredient',)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id', 'display_email', 'display_username', 'display_fullname',
        'display_recipes', 'display_authors', 'display_followers',
        'display_favorites', 'display_avatar',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            display_favorites=Count('favorites'),
            display_followers=Count('followers'),
            display_authors=Count('authors'),
            display_recipes=Count('recipes'),
        )
        return queryset

    @admin.display(description='Почта')
    def display_email(self, user):
        return f'{user.email}'

    @admin.display(description='Ник')
    def display_username(self, user):
        return f'{user.username}'

    @admin.display(description='ФИО')
    def display_fullname(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Рецепты')
    def display_recipes(self, user):
        return user.display_recipes

    @admin.display(description='Избранное')
    def display_favorites(self, user):
        return user.display_favorites

    @admin.display(description='Подписки')
    def display_followers(self, user):
        return user.display_followers

    @admin.display(description='Подписчики')
    def display_authors(self, user):
        return user.display_authors

    @admin.display(description='Аватар')
    @mark_safe
    def display_avatar(self, user):
        if not user.avatar:
            return ''
        return f'<img src="{user.avatar.url}" height="100" width="100">'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    list_select_related = ('user', 'author',)


@admin.register(Favorite, ShoppingCart)
class ShoppingCartFavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_recipe', 'display_user',)
    list_select_related = ('recipe', 'user',)

    @admin.display(description='Рецепт')
    def display_recipe(self, obj):
        return f'{obj.recipe.name}'

    @admin.display(description='Пользователь')
    def display_user(self, obj):
        return f'{obj.user}'
