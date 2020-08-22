from django.http import HttpResponse
from django.shortcuts import render
from .models import Post
from .forms import GetPriceForm
import requests

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
    print('sessionid: ', request.COOKIES)
    print('\n_auth_user_hash: ', request.session.get('_auth_user_hash'))

    if form.is_valid():
        form.save()

    context = {
               'title': 'Map',
               'form': form
    }
    return render(request, 'miasta/map.html', context)

# on3ex0fog2elk6erid7tchq6h5dgu3kh

# csrf = YcPMp3I2jW47t11ero6OymLkcGVmgcRG7ImyxEU0L00xEzTenD8yMOiQbU8Qkimk