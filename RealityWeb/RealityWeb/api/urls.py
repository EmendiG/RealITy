from django.urls import path, include
from .views import (
    GetPriceApiModel,
    getprice
    )
from rest_framework import routers

router = routers.DefaultRouter()
router.register('allrequests', GetPriceApiModel)

urlpatterns = [
    path('', include(router.urls)),
    path('status/', getprice )
]
