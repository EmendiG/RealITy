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

def home(request):
    return render(request, 'miasta/Warszawa.html')

def about(request):
    context ={
                'title':'About RealityWeb'
    }
    return render(request, 'home/about.html', context)


def show_map(request):

    # https://django-map-widgets.readthedocs.io/en/latest/
    # https://stackoverflow.com/questions/21387432/add-marker-on-a-map-and-catch-the-point-value-to-a-django-form-ajax-geodjango
    # https://stackoverflow.com/questions/21415765/passing-value-to-a-form-input-field-inside-a-jquery-dialogbox

    form = GetPriceForm(request.POST or None)
    # print('sessionid: ', request.COOKIES)
    # print('\n_auth_user_hash: ', request.session.get('_auth_user_hash'))

    if form.is_valid():
        form.save()
        price = test.RealityPython_MLREP_getPrice(request)
        messages.success(request, f"Estymowana cena za metr kwadratowy wynosi {round(price,2)} PLN boghactwo :D ")

    context = {
               'title': 'Map',
               'form': form
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
#
#
# def table_preparation():
#     file = open('RealityWeb/api/col_model_warszawa.sav', 'rb')
#     pickle_loaded = pickle.load(file)
#     return pickle_loaded
#     #df_pickle = pd.read_pickle('RealityWeb/api/finalized_model_warszawa.sav')
#     #print(pickle_loaded)
#
# # csrf = YcPMp3I2jW47t11ero6OymLkcGVmgcRG7ImyxEU0L00xEzTenD8yMOiQbU8Qkimk