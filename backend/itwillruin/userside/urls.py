from django.urls import path
from . import views

app_name = 'userside'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('map/', views.map_view, name='map'),
    # path('prediction/', views.weather_planner_view, name='weather_planner'),
    path('about/', views.about_view, name='about'),
    # path('team/', views.team, name='team'),
    path('ai/', views.insights_view, name='insights'),
    # path('map', views.map, name='weather_planner'),
    path('weather_api/', views.weather_forecast_api, name='weather_forecast_api'),
]
