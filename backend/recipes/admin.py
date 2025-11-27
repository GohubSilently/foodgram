from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.safestring import mark_safe

from .constants import TRESHOLD_1, TRESHOLD_2
from .models import (
    Ingredient, Tag, Recipe, User, Subscription, ShoppingCart, Favorite,
    RecipeIngredient
)


class TagIngredientMixin:
    list_display = ('id', 'name', 'display_recipes_count',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            display_recipes_count=Count('recipes')
        )

    @admin.display(description='В рецептах')
    def display_recipes_count(self, obj):
        return obj.display_recipes_count


class CookinTimeFilter(admin.SimpleListFilter):
    title = 'cooking time'
    parameter_name = 'cooking_time'

    RANGES = {
        '1': (0, TRESHOLD_1),
        '2': (TRESHOLD_1 + 1, TRESHOLD_2),
        '3': (TRESHOLD_2 + 1, 525600),
    }

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)

        recipes = []
        for key, range_time in self.RANGES.items():
            count = queryset.filter(cooking_time__range=(range_time)).count()
            if key == '1':
                value = f'Меньше 1 часа ({count})'
            elif key == '2':
                value = f'От одного часа до 24 часов ({count})'
            elif key == '3':
                value = f'Больше 24 часов ({count})'
            recipes.append((key, value))
        return recipes

    def queryset(self, request, queryset):
        if self.value() in self.RANGES:
            range_time = self.RANGES[self.value()]
            return queryset.filter(cooking_time__range=(range_time))
        return queryset


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Tag)
class TagAdmin(TagIngredientMixin, admin.ModelAdmin):
    list_display = ('slug', *TagIngredientMixin.list_display)
    list_filter = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(TagIngredientMixin, admin.ModelAdmin):
    list_display = ('measurement_unit', *TagIngredientMixin.list_display)
    list_filter = ('name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = (
        'id', 'name', 'author', 'cooking_time', 'display_tags',
        'display_ingredients', 'display_favorites', 'display_image',
    )
    list_select_related = ('author',)
    list_filter = ('author__username', 'tags__name', CookinTimeFilter)
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
            (f'{ingredient.ingredient.name} ({ingredient.amount} '
             f'{ingredient.ingredient.measurement_unit})'
             for ingredient in ingredient.recipe_ingredients.select_related(
                'ingredient')
             )
        )

    @admin.display(description='Фото')
    @mark_safe
    def display_image(self, recipe):
        return f'<img src="{recipe.image.url}" height="100" width="100">/>'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    list_select_related = ('recipe', 'ingredient',)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id', 'email', 'username', 'first_name', 'last_name',
        'display_authors', 'display_followers', 'display_favorites',
        'display_avatar',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            display_favorites=Count('favorites'),
            display_followers=Count('followers'),
            display_authors=Count('authors'),
        )
        return queryset

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
        return f'<img src="{user.avatar.url}" height="100" width="100">/>'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    list_select_related = ('user', 'author',)


@admin.register(Favorite, ShoppingCart)
class ShoppingCartFavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user',)
    list_select_related = ('recipe', 'user',)
