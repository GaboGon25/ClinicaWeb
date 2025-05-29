from django.urls import path

from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.login_view, name='login'),  # Ahora la raiz es el login para que se muestre primero
    path('index/', views.index, name='index'),  # ojo aca
    path('agregar_paciente/', views.agregar_paciente, name='agregar_paciente'),
    path('login/', views.login_view, name='login'),

]
