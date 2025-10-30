from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .filters import IngredientFilter
from .models import Tag, Ingredient
from .permissions import IsAdminOrReadOnly
from .serializers import TagSerializer, IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter