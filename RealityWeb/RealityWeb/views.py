from django.http import HttpResponse
from django.shortcuts import render
from .forms import GetPriceForm, FindFeaturesForm
import requests
import json

from rest_framework.decorators import api_view
import pandas as pd
import pickle
from django.http import JsonResponse
from django.contrib import messages
from rest_framework import status
from rest_framework.response import Response

from .RealityPython import ml_engine, findfeatures
# Create your views here.

def index(request):
    context = {
                'title': 'RealityWeb'
    }
    return render(request, 'home/index.html', context)


def about(request):
    context ={
                'title':'About RealityWeb'
    }
    return render(request, 'home/about.html', context)

def choice(request):
    context ={
                'title':'Choose a service'
    }
    return render(request, 'home/choice.html', context)

def features(request):
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

    if request.method == 'POST':
        form = FindFeaturesForm(request.POST)
        if form.is_valid():
            form.save()
            features = findfeatures.FindNearFeatures(request)
            features_js = json.dumps(features)
            context = {
            'title': 'Map',
            'form': form,
            'latlon': latlon,
            'features': features_js
            }
            return render(request, 'home/features_found.html', context)
    else:
        form = FindFeaturesForm()

    context = {
            'title': 'Map',
            'form': form,
            'latlon': latlon
    }
    return render(request, 'home/features.html', context)

def graphs(request):
    def mobile(request):
        import re
        """Return True if the request comes from a mobile device."""

        MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            return True
        else:
            return False

    if request.COOKIES['city']:
        city = request.COOKIES['city']
        my_width = request.COOKIES['my_width']
        my_height = request.COOKIES['my_height']
        ratio = int(my_height)/int(my_width)
        if mobile(request):
            is_mobile = True
        else:
            is_mobile = False

        context ={
                    'title':'Graphs',
                    'map_context':{
                                    'city_name': {'value': city}
                    },
                    'my_ratio':ratio,
                    'is_mobile': is_mobile,
        }
        return render(request, 'home/graphs.html', context)
    

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
            price = ml_engine.RealityPython_MLREP_getPrice(request)
            context = {
            'title': 'Map',
            'form': form,
            'latlon': latlon,
            'price': round(price,2)
            }
            return render(request, 'home/map.html', context)
    else:
        form = GetPriceForm()

    context = {
            'title': 'Map',
            'form': form,
            'latlon': latlon
    }
    return render(request, 'home/map.html', context)
