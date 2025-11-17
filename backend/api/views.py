from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import (
    Tag, Ingredient, Recipe, ShoppingCart, Favorite,
)
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .serializers import (
    TagSerializer, IngredientReadSerializer, RecipeReadSerializer,
    RecipeCreateSerializer, FavoriteSerializer, ShoppingCartSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientReadSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not ShoppingCart.objects.filter(
                    user=user, recipe=recipe
            ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(
                data={'message': 'Рецепт удален!'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(
                data={'message': 'Рецепт успешно удален из избранного!'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True, methods=['get'], url_path='get-link',
        permission_classes=(IsAuthenticated,)
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        base_url = request.build_absolute_uri('/').rstrip('/')
        short_url = f'{base_url}/recipes/{recipe.id}'
        return Response({'short_url': short_url})


class FavoriteListView(generics.ListAPIView):
    serializer_class = RecipeReadSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Favorite.objects.filter(favorites__user=self.request.user)
