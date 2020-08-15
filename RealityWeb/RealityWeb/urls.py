from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='index-about'),
    path('map', views.home, name='index-map'),
]
