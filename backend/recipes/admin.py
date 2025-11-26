from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import (
    Ingredient, Tag, Recipe, User, Subscription, ShoppingCart, Favorite,
    RecipeIngredient
)


class BaseAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            display_count=Count('recipes')
        )

    @admin.display(description='Количество использования в рецептах')
    def display_count(self, obj):
        return obj.display_count

    class Meta:
        abstract = True


class CookinTimeFilter(admin.SimpleListFilter):
    title = 'cooking time'
    parameter_name = 'cooking_time'

    RANGES = {
        '1': (0, 60),
        '2': (61, 1440),
        '3': (1441, 525600),
    }

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)

        recipes = []
        for key, (start, end) in self.RANGES.items():
            count = queryset.filter(cooking_time__range=(start, end)).count()
            if key == '1':
                value = f'Меньше 1 чаваса ({count})'
            elif key == '2':
                value = f'От одного часа до дня ({count})'
            elif key == '3':
                value = f'Больше суток ({count})'
            recipes.append((key, value))

        return recipes

    def queryset(self, request, queryset):
        if self.value() == self.RANGES:
            start, end = self.RANGES[self.value()]
            return queryset.filter(cooking_time__range=(start, end))
        return queryset


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    list_display = ('id', 'name', 'slug', 'display_count')
    list_filter = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'display_count')
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            display_favorite=Count('favorites')
        ).prefetch_related(
            'tags', 'ingredients',
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
            (f'{ingredient.name} ({ingredient.measurement_unit})'
             for ingredient in ingredient.ingredients.all())
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
        'display_following', 'display_followers', 'display_favorites',
        'display_avatar',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            display_favorites=Count('favorites'),
            display_followers=Count('followers'),
            display_following=Count('following'),
        )
        return queryset

    @admin.display(description='Избранное')
    def display_favorites(self, user):
        return user.display_favorites

    @admin.display(description='Подписки')
    def display_followers(self, user):
        return user.display_followers

    @admin.display(description='Подписчики')
    def display_following(self, user):
        return user.display_following

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
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user',)
    list_select_related = ('recipe', 'user',)
