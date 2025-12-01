from django.shortcuts import get_object_or_404
from django.urls import reverse
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
    UserRecipeSerializer, UserSerializer, RecipeShortSerializer
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
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(authors__user=request.user)

        if self.paginate_queryset(queryset) is not None:
            return self.get_paginated_response(UserRecipeSerializer(
                self.paginate_queryset(queryset),
                context={'request': request},
                many=True
            ).data)
        return Response(UserRecipeSerializer(
            queryset, context={'request': request}, many=True
        ).data)

    @action(
        detail=True, methods=['post', 'delete'], url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        user = request.user
        author_id = self.kwargs.get('id')
        if user.id == int(author_id):
            raise ValidationError(
                'Нельзя подписаться или отписаться на самого себя!'
            )
        if request.method == 'POST':
            subscription, create = Subscription.objects.get_or_create(
                user=user, author_id=author_id
            )
            if not create:
                raise ValidationError(
                    f'Вы уже подписаны на пользователя '
                    f'{subscription.author.username}'
                )

            return Response(
                UserRecipeSerializer(
                    subscription.author, context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED)
        get_object_or_404(
            Subscription, user=user, author_id=author_id
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

    def user_iteraction(self, model, request, pk):
        user = request.user

        if request.method == 'POST':
            _, created = model.objects.get_or_create(
                user=user, recipe_id=pk
            )
            if not created:
                raise ValidationError(
                    f'{_.recipe.name} уже есть в '
                    f'{model._meta.verbose_name.lower()}!'
                )
            return Response(
                RecipeShortSerializer(
                    _.recipe,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(model, user=user, recipe_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self.user_iteraction(
            ShoppingCart,
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
            request,
            pk
        )

    @action(
        detail=True, methods=['get'], url_path='get-link',
    )
    def get_link(self, request, pk=None):
        return Response(
            {'short-link': request.build_absolute_uri(
                reverse('recipes:short_link', args=[pk])
            )
            }
        )
