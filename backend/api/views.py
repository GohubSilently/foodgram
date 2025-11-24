from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Tag, Ingredient, Recipe, ShoppingCart, Favorite, User, Subscription
)
from .pagination import Pagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    TagSerializer, IngredientReadSerializer, RecipeReadSerializer,
    RecipeCreateUpdateSerializer, UserAvatarSerializer,
    UserSubscriptionSerializer, UserSerializer, RecipeShortSerializer
)


class RecipeUserViewSet(UserViewSet):
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
                User.objects.filter(subscriptions__user=request.user),
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
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя!')
        if request.method == 'POST':
            subscription, create = Subscription.objects.get_or_create(
                user=user, author=author
            )
            if not create:
                raise ValidationError(
                    'Вы уже подписаны на этого пользователя!'
                )

            return Response(
                UserSubscriptionSerializer(
                    author, context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED)
        get_object_or_404(
            Subscription.objects.filter(author_id=id)
        ).delete()
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

    def user_iteraction(self, model, serializer_class, request, pk):
        user = request.user
        recipe = model.objects.filter(user=user, recipe_id=pk)

        if request.method == 'POST':
            if recipe.exists():
                raise ValidationError('Рецепт уже есть в списке!')
            recipe = model.objects.create(user=user, recipe_id=pk)
            return Response(
                serializer_class(
                    recipe.recipe,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        if not recipe.exists():
            raise ValidationError('Такого рецепта нет!')
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self.user_iteraction(
            ShoppingCart,
            RecipeShortSerializer,
            request,
            pk
        )

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self.user_iteraction(
            Favorite,
            RecipeShortSerializer,
            request,
            pk
        )
