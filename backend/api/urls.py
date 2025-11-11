from django.urls import include, path
from rest_framework import routers

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet, FavoriteListView
)
from users.views import (
    CustomUserAvatarView, CustomUserSubscription, SubscriptionsListView
)


router_v1 = routers.DefaultRouter()
router_v1.register('tags', TagViewSet)
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('recipes', RecipeViewSet)


auth_patterns = [
    path('users/me/avatar/', CustomUserAvatarView.as_view()),
    path('users/<int:pk>/subscribe/', CustomUserSubscription.as_view()),
    path('users/favorites/', FavoriteListView.as_view()),
    path('users/subscriptions/', SubscriptionsListView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]

urlpatterns = [
    path('', include(auth_patterns)),
    path('', include(router_v1.urls)),
]
