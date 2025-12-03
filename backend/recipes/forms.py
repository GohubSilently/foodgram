from django import forms
from .models import Recipe, User


class RecipeImageForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('image',)
