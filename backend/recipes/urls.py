from django.urls import path

from .views import short_link


app_name = 'recipes'


urlpatterns = [
    path('recipes/<int:pk>/get-link', short_link, name='short_link'),
]
