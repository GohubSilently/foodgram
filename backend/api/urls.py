from django.urls import include, path
from rest_framework import routers

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet, UserViewSet
)


router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
