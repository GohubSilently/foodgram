from django.urls import include, path
from rest_framework import routers

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet, RecipeUserViewSet
)


router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', RecipeUserViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
