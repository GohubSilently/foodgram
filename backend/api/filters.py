import django_filters

from .models import Ingredient


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter()
    class Meta:
        model = Ingredient
        fields = {
            'name': ('istartswith', 'icontains'),
        }
        # TODO: Если не будет работать фильтрация, тогда надо переписать этот код на более низком уровне
        #  сейчас фильтрация работает по методу name__istartwith, а не просто по поиску.