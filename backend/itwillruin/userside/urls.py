from django.urls import path
from . import views

app_name = 'userside'

urlpatterns = [
    path('', views.home, name='home'),
    path('dash', views.dashboard, name='dashboard'),
]
