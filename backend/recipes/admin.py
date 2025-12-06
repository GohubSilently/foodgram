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


class RecipeCountMixin:
    list_display = ('recipes_count',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipes_count=Count('recipes')
        )

    @admin.display(description='Рецепты')
    def recipes_count(self, obj):
        return obj.recipes_count


class RecipeBaseFilter(admin.SimpleListFilter):
    related_name = None
    LOOKUPS = (
        ('yes', 'Да'),
        ('no', 'Нет')
    )

    def lookups(self, request, model_admin):
        return self.LOOKUPS

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            queryset = queryset.annotate(
                count=Count(self.related_name)
            ).filter(count__gt=0)

        if self.value() == 'no':
            queryset = queryset.annotate(
                count=Count(self.related_name)
            ).filter(count=0)

        return queryset


class RecipeFilter(RecipeBaseFilter):
    title = 'Есть рецепты'
    parameter_name = 'recipes'
    related_name = 'recipes'


class SubscriptionFilter(RecipeBaseFilter):
    title = 'Есть подписки'
    parameter_name = 'subscription'
    related_name = 'followers'


class FollowerFilter(RecipeBaseFilter):
    title = 'Есть подписчики'
    parameter_name = 'follower'
    related_name = 'subscriptions'


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    TRESHOLD_1 = 60
    TRESHOLD_2 = 60 * 24
    MAX_TIME = 1000000

    LESS_ONE_HOUR = f'Меньше {TRESHOLD_1}(мин)'
    ONE_HOUR_TO_ONE_DAY = f'От {TRESHOLD_1}(мин) до {TRESHOLD_2}(мин)'
    MORE_ONE_DAY = f'Больше {TRESHOLD_2}(мин)'

    RANGES = {
        '1': ((0, TRESHOLD_1), LESS_ONE_HOUR),
        '2': ((TRESHOLD_1 + 1, TRESHOLD_2), ONE_HOUR_TO_ONE_DAY),
        '3': ((TRESHOLD_2 + 1, MAX_TIME), MORE_ONE_DAY),
    }

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        return [
            (
                key,
                "{} ({})".format(
                    text,
                    queryset.filter(cooking_time__range=range_time).count()
                )
            )
            for key, (range_time, text) in self.RANGES.items()
        ]

    def queryset(self, request, recipes):
        if self.value() in self.RANGES:
            return recipes.filter(
                cooking_time__range=(self.RANGES[self.value()])
            )
        return recipes


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Tag)
class TagAdmin(RecipeCountMixin, admin.ModelAdmin):
    list_display = (
        *RecipeCountMixin.list_display, 'id', 'display_name', 'display_slug')

    @admin.display(description='Название')
    def display_name(self, obj):
        return obj.name

    @admin.display(description='Идентификатор')
    def display_slug(self, tag):
        return tag.slug


@admin.register(Ingredient)
class IngredientAdmin(RecipeCountMixin, admin.ModelAdmin):
    list_display = (
        'id', 'display_name', 'display_measurement_unit',
        *RecipeCountMixin.list_display,
    )
    list_filter = ('measurement_unit',)

    @admin.display(description='Название')
    def display_name(self, obj):
        return obj.name

    @admin.display(description='Единица измерения')
    def display_measurement_unit(self, ingredient):
        return ingredient.measurement_unit

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['measurement_unit'].label = 'Единицы измерения'
        return form


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = (
        'id', 'display_name', 'display_author', 'display_cooking_time',
        'display_tags', 'display_ingredients',
        'display_favorites', 'display_image',
    )
    list_select_related = ('author',)
    list_filter = ('author__username', 'tags__name', CookingTimeFilter)
    search_fields = (
        'name', 'author__username', 'tags__name', 'ingredients__name'
    )
    readonly_fields = ('display_image',)
    exclude = ('ingredients',)

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
        return recipe.name

    @admin.display(description='Автор')
    def display_author(self, recipe):
        return recipe.author.username

    @admin.display(description='Время (мин)')
    def display_cooking_time(self, recipe):
        return recipe.cooking_time

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

    @admin.display(description='Картинка')
    @mark_safe
    def display_image(self, recipe):
        return (
            f'<img src="{recipe.image.url}" '
            f'style="max-width: 150px; max-height: 150px;'
            f'border-radius: 10px;">'
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    list_select_related = ('recipe', 'ingredient',)


@admin.register(User)
class UserAdmin(RecipeCountMixin, UserAdmin):
    list_display = (
        'id', 'display_email', 'display_username', 'display_fullname',
        *RecipeCountMixin.list_display, 'display_authors',
        'display_followers', 'display_favorites', 'display_avatar'
    )
    search_related_fields = ('shopping_cart', 'favorites',)
    list_filter = (RecipeFilter, SubscriptionFilter, FollowerFilter)
    readonly_fields = ('display_avatar', )
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                'fields': (
                    'avatar',
                    'display_avatar',
                ),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            display_favorites=Count('favorites'),
            display_followers=Count('followers', distinct=True),
            display_authors=Count('authors', distinct=True),
        )
        return queryset

    @admin.display(description='Почта')
    def display_email(self, user):
        return user.email

    @admin.display(description='Ник')
    def display_username(self, user):
        return user.username

    @admin.display(description='ФИО')
    def display_fullname(self, user):
        return f'{user.first_name} {user.last_name}'

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
        return (
            f'<img src="{user.avatar.url}" '
            f'style="max-width: 100px; max-height: 100px;'
            f'border-radius: 10px;">'
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_user', 'display_author',)
    list_select_related = ('user', 'author',)

    @admin.display(description='Пользователь')
    def display_user(self, obj):
        return obj.user.username

    @admin.display(description='Автор')
    def display_author(self, obj):
        return obj.author.username


@admin.register(Favorite, ShoppingCart)
class ShoppingCartFavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_recipe', 'display_user',)
    list_select_related = ('recipe', 'user',)

    @admin.display(description='Рецепт')
    def display_recipe(self, obj):
        return obj.recipe.name

    @admin.display(description='Пользователь')
    def display_user(self, obj):
        return obj.user.username
