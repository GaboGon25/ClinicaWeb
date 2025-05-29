from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def agregar_paciente(request):
    return render(request, 'add_patient.html')



# Create your views here.
