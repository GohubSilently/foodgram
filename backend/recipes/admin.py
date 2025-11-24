from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import (
    Ingredient, Tag, Recipe, User, Subscription, ShoppingCart, Favorite,
    RecipeIngredient
)


class CookinTimeFilter(admin.SimpleListFilter):
    title = 'cooking time'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        return (
            ('1', f'Меньше 1 часа ('
                  f'{queryset.filter(cooking_time__lt=60).count()})'),
            ('2', f'Больше 1 часа ('
                  f'{queryset.filter(
                      cooking_time__gte=60,
                      cooking_time__lt=1140).count()})'),
            ('3', f'Больше 1 дня ('
                  f'{queryset.filter(cooking_time__gte=1440).count()})'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(cooking_time__lt=60)
        elif self.value() == '2':
            return queryset.filter(cooking_time__gte=60, cooking_time__lt=1140)
        elif self.value() == '3':
            return queryset.filter(cooking_time__gte=1440)
        return queryset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'display_count')
    list_filter = ('name', 'slug')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            display_count=Count('recipes')
        )

    def display_count(self, tag):
        return tag.display_count

    display_count.short_description = 'Количество рецептов'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'display_count')
    list_filter = ('name', 'measurement_unit')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            display_count=Count('recipes')
        )

    def display_count(self, ingredient):
        return ingredient.display_count

    display_count.short_description = 'Количество рецептов'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'cooking_time', 'display_tags',
        'display_ingredients', 'display_favorites', 'display_image',
    )
    list_select_related = ('author',)
    list_filter = ('author__username', 'tags__name', CookinTimeFilter)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            display_favorite=Count('favorites')
        ).prefetch_related(
            'tags', 'ingredients',
        )
        return queryset

    def display_favorites(self, favorites):
        return favorites.display_favorite

    def display_tags(self, tag):
        return ', '.join((tag.name for tag in tag.tags.all()))

    def display_ingredients(self, ingredient):
        return ', '.join(
            (ingredient.name for ingredient in ingredient.ingredients.all())
        )

    @mark_safe
    def display_image(self, recipe):
        return f'<img src="{recipe.image.url}" height="100" width="100">/>'

    display_tags.short_description = 'Теги'
    display_ingredients.short_description = 'Ингредиенты'
    display_favorites.short_description = 'Избранное'
    display_image.short_description = 'Фотография'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    list_select_related = ('recipe', 'ingredient',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'username', 'first_name', 'last_name',
        'display_subscriptions', 'display_followers', 'display_favorites',
        'display_avatar',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            display_favorites=Count('favorites'),
            display_followers=Count('followers'),
            display_subscriptions=Count('subscriptions'),
        )
        return queryset

    def display_favorites(self, user):
        return user.display_favorites

    def display_followers(self, user):
        return user.display_followers

    def display_subscriptions(self, user):
        return user.display_subscriptions

    @mark_safe
    def display_avatar(self, user):
        if not user.avatar:
            return ''
        return f'<img src="{user.avatar.url}" height="100" width="100">/>'

    display_favorites.short_description = 'Избранное'
    display_followers.short_description = 'Подписки'
    display_subscriptions.short_description = 'Подписчики'
    display_avatar.short_description = 'Аватар'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    list_select_related = ('user', 'author',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user',)
    list_select_related = ('recipe', 'user',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user',)
    list_select_related = ('recipe', 'user',)
