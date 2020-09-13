from django.http import HttpResponse
from django.shortcuts import render
from .models import Post
from .forms import GetPriceForm
import requests

from rest_framework.decorators import api_view
import pandas as pd
import pickle
from django.http import JsonResponse
from django.contrib import messages
from rest_framework import status
from rest_framework.response import Response

from .RealityPython import test
# Create your views here.

def index(request):
    context = {
                'title': 'RealityWeb',
                'nieruchomosci': Post.objects.all()
    }
    return render(request, 'home/index.html', context)


def about(request):
    context ={
                'title':'About RealityWeb'
    }
    return render(request, 'home/about.html', context)


def show_map(request):

    latlonDict = {
                    'warszawa':[52.237, 21.017], 
                    'krakow':[50.05, 19.945],
                    'lodz': [51.76, 19.457],  
                    'wroclaw': [51.108, 17.039], 
                    'poznan': [52.409, 16.932], 
                    'gdansk': [54.372, 18.638], 
                    'szczecin': [53.428, 14.553], 
                    'bydgoszcz': [53.123, 18.008], 
                    'lublin': [51.246, 22.568],
                    'bialystok': [53.118, 23.126]
    }
    if request.COOKIES['city']:
        latlon = latlonDict[request.COOKIES['city']]

    # print('sessionid: ', request.COOKIES)
    # print('\n_auth_user_hash: ', request.session.get('_auth_user_hash'))

    if request.method == 'POST':
        form = GetPriceForm(request.POST)
        if form.is_valid():
            form.save()
            price = test.RealityPython_MLREP_getPrice(request)
            messages.success(request, f"Estymowana cena za metr kwadratowy wynosi {round(price,2)} PLN boghactwo :D ")
            context = {
            'title': 'Map',
            'form': form,
            'latlon': latlon,
            'price': round(price,2)
            }
            return render(request, 'miasta/map.html', context)
    else:
        form = GetPriceForm()

    context = {
            'title': 'Map',
            'form': form,
            'latlon': latlon
    }
    return render(request, 'miasta/map.html', context)

# @api_view(["POST"])
# def getprice(request):
#     try:
#         myData = request.POST
#         messages.success(request, myData['csrfmiddlewaretoken'])
#         messages.success(request, table_preparation())
#         return JsonResponse(myData, safe=False)
#     except ValueError as e:
#         return Response(e.args[0], status.HTTP_400_BAD_REQUEST)