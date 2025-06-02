from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from .models import Paciente

#def login(request):
    #return render(request, 'login.html')
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # messages.success(request, 'Inicio de sesión exitoso')
            return redirect('index')  # Cambia 'home' por el nombre de tu vista principal
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'login.html')

def index(request):
    return render(request, 'index.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')  # Redirige al login después de cerrar sesión


def agregar_paciente(request):
    if request.method == "POST":
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        ocupacion = request.POST['ocupacion']
        correo = request.POST['correo']
        telefono = request.POST['telefono']
        direccion = request.POST['direccion']

        # Paso 1: Instanciar el objeto
        paciente = Paciente(
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
            ocupacion=ocupacion,
            correo=correo,
            telefono=telefono,
            direccion=direccion
        )

        # (Aquí podrías hacer validaciones si quisieras)

        # Paso 2: Guardar en la base de datos
        paciente.save()

        messages.success(request, 'Paciente agregado correctamente.')
        return redirect('tabla_paciente')
    return render(request, 'add_patient.html')

def tabla_paciente(request):
    pacientes = Paciente.objects.all()
    return render(request, 'tabla_patient.html', {'pacientes': pacientes})

def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        # Paso 1: Asignar datos
        paciente.nombre = request.POST['nombre']
        paciente.apellido = request.POST['apellido']
        paciente.fecha_nacimiento = request.POST['fecha_nacimiento']
        paciente.ocupacion = request.POST['ocupacion']
        paciente.correo = request.POST['correo']
        paciente.telefono = request.POST['telefono']
        paciente.direccion = request.POST['direccion']

        # Paso 2: Guardar cambios
        paciente.save()

        messages.success(request, 'Datos del paciente actualizados correctamente.')
        return redirect('tabla_paciente')
    return render(request, 'edit_patient.html', {'paciente': paciente})

def cita_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'cards_patient.html', {'pacientes': pacientes})

def cuadros_citas(request):
    return render(request, 'home_citas.html')

def agregar_cita(request):
    return render(request, 'add_cita.html')

def editar_cita(request):
    return render(request, 'edit_cita.html')

def detalle_cita(request):
    return render(request, 'detail_cita.html')






# Create your views here.
