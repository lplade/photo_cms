from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# TODO get from global config file
SITE_TITLE = 'Photos'


def index(request):
    return render(request, 'dam/home.html',
                  {'title': SITE_TITLE, })
