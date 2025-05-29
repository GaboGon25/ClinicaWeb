from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('agregar_paciente/', views.agregar_paciente, name='agregar_paciente'),
]
