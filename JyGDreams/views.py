from django.shortcuts import render
from django.http import HttpResponse

def login(request):
    return render(request, 'login.html')

def index(request):
    return render(request, 'index.html')


def agregar_paciente(request):
    return render(request, 'add_patient.html')





# Create your views here.
