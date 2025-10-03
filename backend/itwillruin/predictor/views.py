from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Weather Predictor App is working!")
