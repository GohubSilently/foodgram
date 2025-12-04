from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from .models import Recipe


def short_link(request, link_code):
    recipe = get_object_or_404(Recipe, short_link=link_code)
    return redirect(reverse('recipe-detail', args=[recipe.pk]))
