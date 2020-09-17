from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='index-about'),
    path('map', views.show_map, name='index-map'),
    path('choice', views.choice, name='index-choice'),
    path('features',  views.features, name='index-features'),
]
