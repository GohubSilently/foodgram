from django.urls import path

from .views import short_link


app_name = 'recipes'


urlpatterns = [
    path('s/<int:pk>/', short_link, name='short_link'),
]
