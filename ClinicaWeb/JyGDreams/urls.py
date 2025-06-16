from django.urls import path

from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.login_view, name='login'),  # Ahora la raiz es el login para que se muestre primero
    path('index/', views.index, name='index'),  # ojo aca
    path("logout", views.logout_view, name="logout"),
    path('agregar_paciente/', views.agregar_paciente, name='agregar_paciente'),
    path('tabla_paciente/', views.tabla_paciente, name='tabla_paciente'),
    path('editar_paciente/<int:paciente_id>/', views.editar_paciente, name='editar_paciente'),
    path('cita_pacientes/', views.cita_pacientes, name='cita_pacientes'),
    #path('cuadros_citas/', views.cuadros_citas, name='cuadros_citas'),
    #path('agregar_cita/', views.agregar_cita, name='agregar_cita'),
    #path('detalle_cita/', views.detalle_cita, name='detalle_cita'),
    path('detalle_cita/<int:cita_id>/', views.detalle_cita, name='detalle_cita'),
    path('editar_cita/<int:cita_id>/', views.editar_cita, name='editar_cita'),
    path('login/', views.login_view, name='login'),
    path('paciente/<int:paciente_id>/agregar_cita/', views.agregar_cita, name='agregar_cita'),
    path('paciente/<int:paciente_id>/citas/', views.home_citas, name='home_citas'),
    path('cita/<int:cita_id>/pago/', views.agregar_pago, name='agregar_pago'),
    path('editar_pago/<int:cita_id>/', views.editar_pago, name='editar_pago'),
    path('detalle_pago/<int:cita_id>/', views.detalle_pago, name='detalle_pago'),
]
