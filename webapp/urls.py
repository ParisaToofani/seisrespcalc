from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.main_project, name='home'), 
    path('resp_estimate/', views.resp_estimate, name='resp_estimate'),
]