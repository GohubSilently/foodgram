from django.http import Http404
from django.shortcuts import redirect

from .models import Recipe


def short_link(request, pk):
    if not Recipe.objects.filter(recipe=pk).exists():
        raise Http404(f'Рецета {pk} не существует!')
    return redirect(f'/recipes/{pk}/')
