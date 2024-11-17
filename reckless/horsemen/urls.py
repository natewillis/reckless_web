from django.urls import path
from . import views

app_name = 'horsemen'

urlpatterns = [
    path('', views.home, name='home'),
    path('race/<int:race_id>/', views.race_detail, name='race_detail'),
]
