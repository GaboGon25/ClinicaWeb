from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Paciente, Cita, Procedimiento, CitaProcedimiento, Pago
from django.utils import timezone
from django.forms import modelformset_factory
from django.db.models import Q

#def login(request):
    #return render(request, 'login.html')
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso')
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

#def cuadros_citas(request):
    #return render(request, 'home_citas.html')


def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    procedimientos = Procedimiento.objects.all()
    procedimientos_dict = {p.id: float(p.costo) for p in procedimientos}

    # Obtener los procedimientos actuales de la cita
    procedimientos_actuales = list(cita.procedimientos.values_list('id', flat=True))

    if request.method == 'POST':
        fecha_nueva = request.POST['fecha']
        hora_nueva = request.POST['hora']
        motivo = request.POST['motivo']
        estado = request.POST['estado']

        procedimiento1_id = request.POST.get('procedimiento1')
        procedimiento2_id = request.POST.get('procedimiento2') if request.POST.get('agregar_otro') else None

        # Si la fecha cambió, el estado pasa a REPROGRAMADO
        if str(cita.fecha) != fecha_nueva:
            estado = 'REPROGRAMADO'

        cita.fecha = fecha_nueva
        cita.hora = hora_nueva
        cita.motivo_cita = motivo
        cita.estado = estado
        cita.save()

        # Actualizar procedimientos asociados
        cita.procedimientos.clear()
        if procedimiento1_id:
            cita.procedimientos.add(procedimiento1_id)
        if procedimiento2_id:
            cita.procedimientos.add(procedimiento2_id)

        messages.success(request, 'Cita editada correctamente.')
        return redirect('home_citas', paciente_id=cita.paciente.id)

    # Para prellenar el formulario
    proc1 = procedimientos_actuales[0] if len(procedimientos_actuales) > 0 else None
    proc2 = procedimientos_actuales[1] if len(procedimientos_actuales) > 1 else None

    return render(request, 'edit_cita.html', {
        'cita': cita,
        'procedimientos': procedimientos,
        'procedimientos_dict': procedimientos_dict,
        'proc1': proc1,
        'proc2': proc2,
    })

def detalle_cita(request , cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    return render(request, 'detail_cita.html', {'cita': cita})


def agregar_cita(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    procedimientos = Procedimiento.objects.all()
    procedimientos_dict = {p.id: float(p.costo) for p in procedimientos}

    if request.method == 'POST':
        fecha = request.POST['fecha']
        hora = request.POST['hora']
        motivo = request.POST['motivo']
        estado = request.POST['estado']
        procedimiento1_id = request.POST.get('procedimiento1')
        procedimiento2_id = request.POST.get('procedimiento2')

        cita = Cita.objects.create(
            paciente=paciente,
            fecha=fecha,
            hora=hora,
            motivo_cita=motivo,
            estado=estado
        )
        if procedimiento1_id:
            CitaProcedimiento.objects.create(cita=cita, procedimiento_id=procedimiento1_id)
        if procedimiento2_id:
            CitaProcedimiento.objects.create(cita=cita, procedimiento_id=procedimiento2_id)

        messages.success(request, 'Cita agregada correctamente.')
        return redirect('home_citas', paciente_id=paciente.id)

    return render(request, 'add_cita.html', {
        'paciente': paciente,
        'procedimientos': procedimientos,
        'procedimientos_dict': procedimientos_dict
    })

def home_citas(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    citas = Cita.objects.filter(paciente=paciente).order_by('-fecha', '-hora')
    return render(request, 'home_citas.html', {
        'paciente': paciente,
        'citas': citas,
    })


def agregar_pago(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    # Verifica si ya existe un pago para esta cita
    if Pago.objects.filter(cita=cita).exists():
        messages.warning(request, "Ya se ha registrado un pago para esta cita.")
        return redirect('home_citas', paciente_id=cita.paciente.id)

    procedimientos = cita.procedimientos.all()[:2]
    monto_final = sum([p.costo for p in procedimientos])

    if request.method == 'POST':
        pago = Pago.objects.create(
            cita=cita,
            fecha=timezone.localdate(),
            total=0
        )
        cita.estado = 'REALIZADO'
        cita.save()
        messages.success(request, "Pago registrado exitosamente.")
        return redirect('home_citas', paciente_id=cita.paciente.id)

    return render(request, 'add_pago.html', {
        'cita': cita,
        'procedimientos': procedimientos,
        'monto_final': monto_final
    })

def editar_pago(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    procedimientos = cita.procedimientos.all()
    ProcedimientoFormSet = modelformset_factory(Procedimiento, fields=('id', 'costo',), extra=0)

    if request.method == 'POST':
        formset = ProcedimientoFormSet(request.POST, queryset=procedimientos)
        if formset.is_valid():
            formset.save()
            # Refresca los procedimientos desde la base de datos
            procedimientos = cita.procedimientos.all()
            pago = Pago.objects.filter(cita=cita).first()
            if pago:
                pago.save()  # Esto recalcula el total
            messages.success(request, "Pago editado correctamente.")
            return redirect('detalle_pago', cita_id=cita.id)
        else:
            print(formset.errors)
    else:
        formset = ProcedimientoFormSet(queryset=procedimientos)

    monto_final = sum([p.costo for p in procedimientos])
    return render(request, 'edit_pago.html', {
        'cita': cita,
        'formset': formset,
        'monto_final': monto_final,
    })

def detalle_pago(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    pago = Pago.objects.filter(cita=cita).first()
    if not pago:
        messages.warning(request, "Primero debe registrar el pago para ver el detalle.")
        return redirect('home_citas', paciente_id=cita.paciente.id)
    procedimientos = cita.procedimientos.all()
    monto_final = sum([p.costo for p in procedimientos])
    paciente = cita.paciente

    return render(request, 'detail_pago.html', {
        'cita': cita,
        'pago': pago,
        'procedimientos': procedimientos,
        'monto_final': monto_final,
        'paciente': paciente,
    })
    
def lista_pacientes(request):
    query = request.GET.get('q', '')
    pacientes = Paciente.objects.all()
    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query)
        )
    return render(request, 'tabla_patient.html', {
        'pacientes': pacientes,
        'query': query,
    })

def ajax_sugerencias_pacientes(request):
    q = request.GET.get('q', '')
    sugerencias = Paciente.objects.filter(
        Q(nombre__icontains=q) | Q(apellido__icontains=q)
    ).values_list('nombre', flat=True).distinct()[:5]
    return JsonResponse(list(sugerencias), safe=False)


# Create your views here.
