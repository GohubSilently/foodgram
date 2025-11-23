from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import (IngredientFilter,
                      RecipeFilter
)
from recipes.models import (
    Tag, Ingredient,
    Recipe, ShoppingCart, Favorite, User, Subscription
)
from .pagination import Pagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    TagSerializer, IngredientReadSerializer, RecipeReadSerializer,
    RecipeCreateUpdateSerializer,
    # FavoriteSerializer, ShoppingCartSerializer,
    UserAvatarSerializer, UserSubscriptionSerializer, UserSerializer,
    RecipeShortSerializer
)

class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination

    @action(
        detail=False, methods=['put', 'delete'], url_path='me/avatar',
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request, *args, **kwargs):
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(
                request.user, data=request.data
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        if request.method == 'DELETE':
            request.user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False, methods=['get'], url_path='subscriptions',
        permission_classes=(IsAuthenticated,), pagination_class=Pagination
    )
    def subscriptions(self, request):
        return Response(
            UserSubscriptionSerializer(
                User.objects.filter(followers__user=request.user),
                context={'request': request},
                many=True
            ).data
        )

    @action(
        detail=True, methods=['post', 'delete'], url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if user == author:
                raise ValidationError('Нельзя подписаться на самого себя!')
            if Subscription.objects.filter(user=user, author=author).exists():
                raise ValidationError('Вы уже подписаны на этого пользователя!')
            Subscription.objects.create(user=user, author=author)
            return Response(
                UserSubscriptionSerializer(
                    author, context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(Subscription.objects.filter(author_id=id)).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientReadSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError('Этот рецепт уже есть в списке покупок!')
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeShortSerializer(
                    recipe,
                    context={'request': request},
                ).data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            get_object_or_404(ShoppingCart.objects.filter(user=user, recipe=recipe)).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError('Этот рецепт уже есть в избранном!')
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeShortSerializer(
                    recipe,
                    context={'request': request},
                ).data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            get_object_or_404(Favorite.objects.filter(user=user, recipe=recipe)).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['get'], url_path='get-link',
        permission_classes=(IsAuthenticated,)
    )
    def get_link(self, request, pk=None):
        short_link = reverse('recipes:short_link', kwargs={'pk': pk})
        short_link = request.build_absolute_uri(short_link)
        return Response({'short_link': short_link})

