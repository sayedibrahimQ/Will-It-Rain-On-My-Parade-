from django.urls import path
from . import views

app_name = 'userside'

urlpatterns = [
    path('', views.home, name='home'),
    path('dash/', views.dashboard, name='dashboard'),
    path('map/', views.map, name='map'),
    path('plan/', views.weather_planner_view, name='weather_planner'),
    path('about/', views.about, name='about'),
    path('team/', views.team, name='team'),
    # path('map', views.map, name='weather_planner'),
    path('download-report/', views.download_report, name='download_report'),
]
