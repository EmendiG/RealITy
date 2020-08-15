from django.http import HttpResponse
from django.shortcuts import render
from .models import Post
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
    return render(request, 'home/about.html', {'title':'About RealityWeb'})