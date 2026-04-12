from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from .models import Paciente, Cita, Procedimiento, CitaProcedimiento, Pago, Expediente, BiotipoCutaneo, CuidadoPiel, Habito, ExpedienteBiotipo, ExpedienteCuidadoPiel, PasswordResetCode
from django.utils import timezone
from django.forms import modelformset_factory
from django.db import models
from django.db.models import Q, Exists, OuterRef, Subquery, Sum, Count, F
from django.core.paginator import Paginator
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime, timedelta
from decimal import Decimal
import os
from django.conf import settings
import json
import secrets
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError

def home_view(request):
    return render(request, 'home_web.html')

def _has_perms(*perms):
    def check(user):
        return user.is_authenticated and user.has_perms(perms)
    return user_passes_test(check, login_url="login")

DOCTOR_GROUP_NAME = "Doctor/a"
SECRETARY_GROUP_NAME = "Secretario/a"
ROLE_GROUP_NAMES = [DOCTOR_GROUP_NAME, SECRETARY_GROUP_NAME]

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

@login_required(login_url="login")
def index(request):
    return render(request, 'index.html')


def password_reset_request(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        if not username:
            messages.error(request, "Ingresa tu usuario.")
            return render(request, "password_reset_request.html")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.success(request, "Si el usuario existe y tiene correo registrado, se ha enviado una clave temporal.")
            return redirect("login")

        if not user.is_active:
            messages.error(request, "Tu cuenta está inactiva. Contacta al administrador.")
            return redirect("login")

        if not user.email:
            messages.error(request, "El usuario no tiene un correo registrado en su perfil.")
            return render(request, "password_reset_request.html")

        code = secrets.token_urlsafe(8)
        expires_at = timezone.now() + timedelta(minutes=15)
        PasswordResetCode.objects.create(user=user, code=code, expires_at=expires_at)

        # Establece la contraseña temporal para que el usuario pueda iniciar sesión
        # con esta clave y luego cambiarla en el flujo de recuperación.
        user.set_password(code)
        user.save(update_fields=["password"])

        reset_url = request.build_absolute_uri(reverse("password_reset_confirm")) + f"?code={code}"

        context = {
            "user": user,
            "code": code,
            "expires_minutes": 15,
            "reset_url": reset_url,
            "clinic_name": "Clínica Estética JyGDreams",
            "logo_url": request.build_absolute_uri(
                settings.STATIC_URL + "JyGDreams/img/icon-clinica.png"
            ),
        }
        html_body = render_to_string("email_password_reset.html", context)

        subject = "Recuperación de contraseña - JyGDreams"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")
        to = [user.email]

        msg = EmailMultiAlternatives(subject, "", from_email, to)
        msg.attach_alternative(html_body, "text/html")
        try:
            msg.send()
            messages.success(request, "Si el usuario existe y tiene correo registrado, se ha enviado una clave temporal.")
        except Exception as e:
            messages.error(request, f"Error al enviar el email: {str(e)}")
        return redirect("login")

    return render(request, "password_reset_request.html")


def password_reset_confirm(request):
    if request.method == "POST":
        code = (request.POST.get("code") or "").strip()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""

        if not code:
            messages.error(request, "Ingresa la clave temporal.")
            return render(request, "password_reset_confirm.html")

        try:
            reset = PasswordResetCode.objects.select_related("user").get(code=code, used=False)
        except PasswordResetCode.DoesNotExist:
            messages.error(request, "Clave temporal inválida o ya usada.")
            return render(request, "password_reset_confirm.html")

        if not reset.is_valid():
            messages.error(request, "La clave temporal ha expirado. Solicita una nueva.")
            return render(request, "password_reset_confirm.html")

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "password_reset_confirm.html", {"code": code})

        try:
            validate_password(password1, user=reset.user)
        except Exception as e:
            msg = getattr(e, "messages", None)
            messages.error(request, msg[0] if msg else "La contraseña no cumple los requisitos.")
            return render(request, "password_reset_confirm.html", {"code": code})

        user = reset.user
        user.set_password(password1)
        user.save()

        reset.used = True
        reset.save()

        messages.success(request, "Tu contraseña ha sido actualizada. Ahora puedes iniciar sesión.")
        return redirect("login")

    code = request.GET.get("code", "")
    return render(request, "password_reset_confirm.html", {"code": code})


@login_required(login_url="login")
def mi_perfil(request):
    user = request.user
    if request.method == "POST":
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""

        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password1 or password2:
            if password1 != password2:
                messages.error(request, "Las contraseñas no coinciden.")
                return render(request, "mi_perfil.html", {"user_obj": user})
            try:
                validate_password(password1, user=user)
            except Exception as e:
                msg = getattr(e, "messages", None)
                messages.error(request, msg[0] if msg else "La contraseña no cumple los requisitos.")
                return render(request, "mi_perfil.html", {"user_obj": user})
            user.set_password(password1)
            user.save()
            # Reautenticar después de cambiar contraseña
            login(request, user)
            messages.success(request, "Perfil y contraseña actualizados correctamente.")
            return redirect("mi_perfil")

        user.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("mi_perfil")

    return render(request, "mi_perfil.html", {"user_obj": user})

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url="login")
def crear_usuario(request):
    roles = Group.objects.filter(name__in=ROLE_GROUP_NAMES).order_by("name")
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        role_id = request.POST.get("role")
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""

        if not username:
            messages.error(request, "El usuario es obligatorio.")
            return render(request, "create_user.html", {"roles": roles})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ese usuario ya existe.")
            return render(request, "create_user.html", {"roles": roles})

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "create_user.html", {"roles": roles})

        try:
            validate_password(password1)
        except Exception as e:
            # e puede ser ValidationError con lista de mensajes
            msg = getattr(e, "messages", None)
            messages.error(request, msg[0] if msg else "La contraseña no cumple los requisitos.")
            return render(request, "create_user.html", {"roles": roles})

        role = roles.filter(id=role_id).first()
        if not role:
            messages.error(request, "Selecciona un rol válido (Doctor o Secretaria).")
            return render(request, "create_user.html", {"roles": roles})

        user = User.objects.create_user(
            username=username,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        user.groups.add(role)
        messages.success(request, f"Usuario '{username}' creado y asignado a {role.name}.")
        return redirect("index")

    return render(request, "create_user.html", {"roles": roles})

@user_passes_test(lambda u: u.is_superuser, login_url="login")
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    roles = Group.objects.filter(name__in=ROLE_GROUP_NAMES).order_by("name")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        role_id = request.POST.get("role")
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""

        if not username:
            messages.error(request, "El usuario es obligatorio.")
            return render(request, "edit_user.html", {"usuario": usuario, "roles": roles})

        if User.objects.filter(username=username).exclude(id=usuario.id).exists():
            messages.error(request, "Ese usuario ya existe.")
            return render(request, "edit_user.html", {"usuario": usuario, "roles": roles})

        if password1 or password2:
            if password1 != password2:
                messages.error(request, "Las contraseñas no coinciden.")
                return render(request, "edit_user.html", {"usuario": usuario, "roles": roles})
            try:
                validate_password(password1, user=usuario)
            except Exception as e:
                msg = getattr(e, "messages", None)
                messages.error(request, msg[0] if msg else "La contraseña no cumple los requisitos.")
                return render(request, "edit_user.html", {"usuario": usuario, "roles": roles})
            usuario.set_password(password1)

        usuario.username = username
        usuario.first_name = first_name
        usuario.last_name = last_name
        usuario.email = email

        role = roles.filter(id=role_id).first()
        if role:
            usuario.groups.clear()
            usuario.groups.add(role)

        usuario.save()
        messages.success(request, f"Usuario '{usuario.username}' actualizado correctamente.")
        return redirect("lista_usuarios")

    return render(request, "edit_user.html", {"usuario": usuario, "roles": roles})

@login_required(login_url="login")
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')  # Redirige al login después de cerrar sesión


@permission_required("JyGDreams.add_paciente", raise_exception=True)
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

@permission_required("JyGDreams.view_paciente", raise_exception=True)
def tabla_paciente(request):
    pacientes = Paciente.objects.all()
    return render(request, 'tabla_patient.html', {'pacientes': pacientes})

@permission_required("JyGDreams.change_paciente", raise_exception=True)
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

@permission_required("JyGDreams.view_expediente", raise_exception=True)
def expediente_pacientes(request):
    query = request.GET.get('q', '')
    tiene_expediente = request.GET.get('tiene_expediente', '')
    
    pacientes = Paciente.objects.all()
    
    # Filtro por nombre/apellido
    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query)
        )
    
    # Filtro por si tiene expediente o no
    if tiene_expediente == 'si':
        pacientes = pacientes.filter(expediente__isnull=False)
    elif tiene_expediente == 'no':
        pacientes = pacientes.filter(expediente__isnull=True)
    
    # Agrega un campo booleano para mostrar si el paciente tiene expediente
    pacientes = pacientes.annotate(
        has_expediente=Exists(Expediente.objects.filter(paciente=OuterRef('pk')))
    )
    
    # Paginación
    paginator = Paginator(pacientes, 6)  # 6 pacientes por página
    page_number = request.GET.get('page')
    
    # Convertir page_number a entero si existe
    if page_number:
        try:
            page_number = int(page_number)
        except (ValueError, TypeError):
            page_number = 1
    else:
        page_number = 1
    
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'cards_expediente.html', {
        'pacientes': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'tiene_expediente': tiene_expediente,
    })

@permission_required("JyGDreams.add_expediente", raise_exception=True)
def agregar_expediente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    biotipos = BiotipoCutaneo.objects.all()
    cuidados = CuidadoPiel.objects.all()

    if request.method == 'POST':
        # 1. Crear expediente
        expediente = Expediente.objects.create(
            paciente=paciente,
            fecha_registro=request.POST.get('fecha'),
            usa_marcapasos=request.POST.get('marcapasos'),
            historial_clinico=request.POST.get('historial_clinico')
        )

        # 2. Crear hábitos
        Habito.objects.create(
            expediente=expediente,
            vasos_agua=request.POST.get('vasos_agua', ''),
            trasnoche=request.POST.get('trasnoche', ''),
            tabaco=request.POST.get('consumo_tabaco', ''),
            cafe=request.POST.get('consumo_cafe', ''),
            licor=request.POST.get('consumo_licor', ''),
            medicamentos=request.POST.get('medicamentos', ''),
            suplementos=request.POST.get('suplementos', '')
        )

        # 3. Relacionar biotipo
        biotipo_nombre = request.POST.get('biotipo')
        biotipo = BiotipoCutaneo.objects.get(nombre=biotipo_nombre)
        ExpedienteBiotipo.objects.create(expediente=expediente, biotipo=biotipo)

        # 4. Relacionar cuidados de piel seleccionados
        cuidado_nombres = [
            ('jabon', 'Jabón Facial'),
            ('cremas', 'Cremas'),
            ('serum', 'Serum'),
            ('aceites', 'Aceites'),
            ('tonico', 'Tónico'),
            ('protector', 'Protector Solar'),
            ('ninguno', 'Ninguno'),
        ]
        for field, nombre in cuidado_nombres:
            if request.POST.get(field):
                cuidado = CuidadoPiel.objects.get(nombre=nombre)
                ExpedienteCuidadoPiel.objects.create(expediente=expediente, cuidado=cuidado)

        # Campo "otro"
        if request.POST.get('otro_check'):
            otro_valor = request.POST.get('otro_input', '')
            if otro_valor:
                cuidado_otro, _ = CuidadoPiel.objects.get_or_create(nombre='Otros')
                ExpedienteCuidadoPiel.objects.create(expediente=expediente, cuidado=cuidado_otro, otro=otro_valor)

        return redirect(f'/detalle_expediente/{expediente.id}/?success=1')

    return render(request, 'add_expediente.html', {
        'paciente': paciente,
        'biotipos': biotipos,
        'cuidados': cuidados,
    })

@permission_required("JyGDreams.view_expediente", raise_exception=True)
def detalle_expediente(request, expediente_id):
    expediente = get_object_or_404(Expediente, id=expediente_id)
    habito = Habito.objects.filter(expediente=expediente).first()
    biotipo = ExpedienteBiotipo.objects.filter(expediente=expediente).first()
    cuidados = ExpedienteCuidadoPiel.objects.filter(expediente=expediente)
    cuidados_lista = [
    "Jabón Facial", "Cremas", "Serum", "Aceites",
    "Tónico", "Protector Solar", "Ninguno"
]
    cuidados_nombres = [c.cuidado.nombre for c in cuidados]
    otro_valor = ""
    for c in cuidados:
        if c.cuidado.nombre == "Otros":
            otro_valor = c.otro
    
    # Obtener citas realizadas (con pago)
    citas_realizadas = Cita.objects.filter(
        paciente=expediente.paciente,
        pago__isnull=False
    ).order_by('-fecha', '-hora')
    
    # Calcular totales para cada cita y total general
    citas_con_totales = []
    total_general = 0
    for cita in citas_realizadas:
        total_cita = sum([float(proc.costo) for proc in cita.procedimientos.all()])
        total_general += total_cita
        citas_con_totales.append({
            'cita': cita,
            'total': total_cita
        })

    return render(request, 'detail_expediente.html', {
        'expediente': expediente,
        'habito': habito,
        'biotipo': biotipo,
        'cuidados_nombres': cuidados_nombres,
        'otro_valor': otro_valor,
        'cuidados_lista': cuidados_lista,
        'citas_con_totales': citas_con_totales,
        'total_general': total_general,
    })

@permission_required("JyGDreams.change_expediente", raise_exception=True)
def editar_expediente(request, expediente_id):
    expediente = get_object_or_404(Expediente, id=expediente_id)
    paciente = expediente.paciente
    biotipos = BiotipoCutaneo.objects.all()
    habito = Habito.objects.filter(expediente=expediente).first()
    expediente_biotipo = ExpedienteBiotipo.objects.filter(expediente=expediente).first()
    cuidados = ExpedienteCuidadoPiel.objects.filter(expediente=expediente)
    cuidados_nombres = [c.cuidado.nombre for c in cuidados]
    otro_valor = ""
    for c in cuidados:
        if c.cuidado.nombre == "Otros":
            otro_valor = c.otro

    if request.method == 'POST':
        # Actualizar expediente
        expediente.fecha_registro = request.POST.get('fecha')
        expediente.usa_marcapasos = request.POST.get('marcapasos')
        expediente.historial_clinico = request.POST.get('historial_clinico')
        expediente.save()

        # Actualizar hábitos
        if habito:
            habito.vasos_agua = request.POST.get('vasos_agua', '')
            habito.trasnoche = request.POST.get('trasnoche', '')
            habito.tabaco = request.POST.get('consumo_tabaco', '')
            habito.cafe = request.POST.get('consumo_cafe', '')
            habito.licor = request.POST.get('consumo_licor', '')
            habito.medicamentos = request.POST.get('medicamentos', '')
            habito.suplementos = request.POST.get('suplementos', '')
            habito.save()
        else:
            Habito.objects.create(
                expediente=expediente,
                vasos_agua=request.POST.get('vasos_agua', ''),
                trasnoche=request.POST.get('trasnoche', ''),
                tabaco=request.POST.get('consumo_tabaco', ''),
                cafe=request.POST.get('consumo_cafe', ''),
                licor=request.POST.get('consumo_licor', ''),
                medicamentos=request.POST.get('medicamentos', ''),
                suplementos=request.POST.get('suplementos', '')
            )

        # Actualizar biotipo
        biotipo_nombre = request.POST.get('biotipo')
        biotipo = BiotipoCutaneo.objects.get(nombre=biotipo_nombre)
        if expediente_biotipo:
            expediente_biotipo.biotipo = biotipo
            expediente_biotipo.save()
        else:
            ExpedienteBiotipo.objects.create(expediente=expediente, biotipo=biotipo)

        # Actualizar cuidados de piel
        ExpedienteCuidadoPiel.objects.filter(expediente=expediente).delete()
        cuidado_nombres = [
            ('jabon', 'Jabón Facial'),
            ('cremas', 'Cremas'),
            ('serum', 'Serum'),
            ('aceites', 'Aceites'),
            ('tonico', 'Tónico'),
            ('protector', 'Protector Solar'),
            ('ninguno', 'Ninguno'),
            ('otro', 'Otro'),
        ]
        for field, nombre in cuidado_nombres:
            if request.POST.get(field):
                cuidado = CuidadoPiel.objects.get(nombre=nombre)
                ExpedienteCuidadoPiel.objects.create(expediente=expediente, cuidado=cuidado)
        # Campo "otro"
        if request.POST.get('otro_check'):
            otro_valor = request.POST.get('otro_input', '')
            if otro_valor:
                cuidado_otro, _ = CuidadoPiel.objects.get_or_create(nombre='Otros')
                ExpedienteCuidadoPiel.objects.create(expediente=expediente, cuidado=cuidado_otro, otro=otro_valor)

        return redirect(f'/detalle_expediente/{expediente.id}/?edited=1')

    # Para el formulario, pasa los valores actuales
    return render(request, 'edit_expediente.html', {
        'paciente': paciente,
        'expediente': expediente,
        'biotipos': biotipos,
        'habito': habito,
        'expediente_biotipo': expediente_biotipo,
        'cuidados_nombres': cuidados_nombres,
        'otro_valor': otro_valor,
    })


@permission_required("JyGDreams.view_expediente", raise_exception=True)
def seleccionar_exp(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    expediente = Expediente.objects.filter(paciente=paciente).first()
    if expediente:
        return redirect('detalle_expediente', expediente_id=expediente.id)
    else:
        return redirect('agregar_expediente', paciente_id=paciente.id)

@permission_required("JyGDreams.view_cita", raise_exception=True)
def cita_pacientes(request):
    query = request.GET.get('q', '')
    fecha = request.GET.get('fecha', '')
    orden = request.GET.get('orden', '')

    pacientes = Paciente.objects.all()

    # Filtrar por doctor si es doctor y no superuser
    if request.user.groups.filter(name=DOCTOR_GROUP_NAME).exists() and not request.user.is_superuser:
        pacientes = pacientes.filter(
            Exists(
                Cita.objects.filter(
                    paciente=OuterRef('pk'),
                    doctor=request.user
                )
            )
        )

    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query)
        )

    if fecha:
        pacientes = pacientes.filter(
            Exists(
                Cita.objects.filter(
                    paciente=OuterRef('pk'),
                    fecha=fecha
                )
            )
        )

    if orden == 'alfabetico':
        pacientes = pacientes.order_by('nombre', 'apellido')
    elif orden == 'fecha':
        fecha_actual = timezone.localdate()
        pacientes = pacientes.filter(
            Exists(
                Cita.objects.filter(
                    paciente=OuterRef('pk'),
                    estado__in=['AGENDADO', 'REPROGRAMADO'],
                    fecha__gte=fecha_actual
                )
            )
        ).annotate(
            proxima_cita=Subquery(
                Cita.objects.filter(
                    paciente=OuterRef('pk'),
                    estado__in=['AGENDADO', 'REPROGRAMADO'],
                    fecha__gte=fecha_actual
                ).order_by('fecha').values('fecha')[:1]
            )
        ).order_by('proxima_cita')

    cita_filter = Q(cita__estado__in=['AGENDADO', 'REPROGRAMADO'])
    if request.user.groups.filter(name=DOCTOR_GROUP_NAME).exists() and not request.user.is_superuser:
        cita_filter &= Q(cita__doctor=request.user)

    pacientes = pacientes.annotate(
        has_expediente=Exists(Expediente.objects.filter(paciente=OuterRef('pk'))),
        citas_por_atender=Count('cita', filter=cita_filter, distinct=True)
    )

    # --- Paginación ---
    paginator = Paginator(pacientes, 6)  # 6 cards por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- Eventos para el calendario ---
    citas = Cita.objects.select_related('paciente').filter(estado__in=['AGENDADO', 'REPROGRAMADO'])
    if request.user.groups.filter(name=DOCTOR_GROUP_NAME).exists() and not request.user.is_superuser:
        citas = citas.filter(doctor=request.user)
    eventos = []
    for cita in citas:
        procedimientos = ", ".join([p.titulo for p in cita.procedimientos.all()])
        eventos.append({
            "title": f"{cita.paciente.nombre} {cita.paciente.apellido} - {procedimientos}",
            "start": f"{cita.fecha}T{cita.hora}",
            "allDay": False,
        })

    eventos_json = json.dumps(eventos, ensure_ascii=False)

    return render(request, 'cards_patient.html', {
        'pacientes': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'fecha': fecha,
        'orden': orden,
        'eventos_json': eventos_json,
    })

#def cuadros_citas(request):
    #return render(request, 'home_citas.html')


@permission_required("JyGDreams.change_cita", raise_exception=True)
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    procedimientos = Procedimiento.objects.all()
    procedimientos_dict = {p.id: float(p.costo) for p in procedimientos}
    doctores = User.objects.filter(groups__name=DOCTOR_GROUP_NAME, is_active=True).order_by("first_name", "last_name", "username").distinct()

    # Obtener los procedimientos actuales de la cita
    procedimientos_actuales = list(cita.procedimientos.values_list('id', flat=True))

    if request.method == 'POST':
        fecha_nueva = request.POST['fecha']
        hora_nueva = request.POST['hora']
        motivo = request.POST['motivo']
        estado = request.POST['estado']
        doctor_id = request.POST.get('doctor')

        procedimiento1_id = request.POST.get('procedimiento1')
        procedimiento2_id = request.POST.get('procedimiento2') if request.POST.get('agregar_otro') else None

        # Si la fecha cambió, el estado pasa a REPROGRAMADO
        if str(cita.fecha) != fecha_nueva:
            estado = 'REPROGRAMADO'

        cita.fecha = fecha_nueva
        cita.hora = hora_nueva
        cita.motivo_cita = motivo
        cita.estado = estado
        cita.doctor_id = doctor_id or None
        try:
            cita.full_clean()
            cita.save()
            # Actualizar procedimientos asociados
            cita.procedimientos.clear()
            if procedimiento1_id:
                cita.procedimientos.add(procedimiento1_id)
            if procedimiento2_id:
                cita.procedimientos.add(procedimiento2_id)
            messages.success(request, 'Cita editada correctamente.')
            return redirect('home_citas', paciente_id=cita.paciente.id)
        except ValidationError as e:
            # Para prellenar el formulario
            proc1 = procedimientos_actuales[0] if len(procedimientos_actuales) > 0 else None
            proc2 = procedimientos_actuales[1] if len(procedimientos_actuales) > 1 else None
            messages.error(request, e.message_dict.get('__all__', e.messages)[0])
            return render(request, 'edit_cita.html', {
                'cita': cita,
                'procedimientos': procedimientos,
                'procedimientos_dict': procedimientos_dict,
                'proc1': proc1,
                'proc2': proc2,
                'doctores': doctores,
            })

    # Para prellenar el formulario
    proc1 = procedimientos_actuales[0] if len(procedimientos_actuales) > 0 else None
    proc2 = procedimientos_actuales[1] if len(procedimientos_actuales) > 1 else None

    return render(request, 'edit_cita.html', {
        'cita': cita,
        'procedimientos': procedimientos,
        'procedimientos_dict': procedimientos_dict,
        'proc1': proc1,
        'proc2': proc2,
        'doctores': doctores,
    })

@permission_required("JyGDreams.view_cita", raise_exception=True)
def detalle_cita(request , cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    is_doctor = request.user.groups.filter(name=DOCTOR_GROUP_NAME).exists() and not request.user.is_superuser
    return render(request, 'detail_cita.html', {'cita': cita, 'is_doctor': is_doctor})


@permission_required("JyGDreams.add_cita", raise_exception=True)
def agregar_cita(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    procedimientos = Procedimiento.objects.all()
    procedimientos_dict = {p.id: float(p.costo) for p in procedimientos}
    doctores = (
        User.objects.filter(is_active=True)
        .filter(models.Q(is_superuser=True) | models.Q(groups__name=DOCTOR_GROUP_NAME))
        .order_by("first_name", "last_name", "username")
        .distinct()
    )

    if request.method == 'POST':
        fecha = request.POST['fecha']
        hora = request.POST['hora']
        motivo = request.POST['motivo']
        estado = request.POST['estado']
        doctor_id = request.POST.get('doctor')
        procedimiento1_id = request.POST.get('procedimiento1')
        procedimiento2_id = request.POST.get('procedimiento2')

        cita = Cita(
            paciente=paciente,
            doctor_id=doctor_id or None,
            fecha=fecha,
            hora=hora,
            motivo_cita=motivo,
            estado=estado
        )
        try:
            cita.full_clean()
            cita.save()
            if procedimiento1_id:
                CitaProcedimiento.objects.create(cita=cita, procedimiento_id=procedimiento1_id)
            if procedimiento2_id:
                CitaProcedimiento.objects.create(cita=cita, procedimiento_id=procedimiento2_id)
            messages.success(request, 'Cita agregada correctamente.')
            return redirect('home_citas', paciente_id=paciente.id)
        except ValidationError as e:
            messages.error(request, e.message_dict.get('__all__', e.messages)[0])
            return render(request, 'add_cita.html', {
                'paciente': paciente,
                'procedimientos': procedimientos,
                'procedimientos_dict': procedimientos_dict,
                'doctores': doctores,
                'doctor_id': doctor_id,
            })

    return render(request, 'add_cita.html', {
        'paciente': paciente,
        'procedimientos': procedimientos,
        'procedimientos_dict': procedimientos_dict,
        'doctores': doctores,
    })

@permission_required("JyGDreams.view_cita", raise_exception=True)
def home_citas(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    citas = Cita.objects.filter(paciente=paciente).order_by('-fecha', '-hora')
    
    # Verificar si el paciente tiene al menos una cita con estado REALIZADO
    tiene_citas_realizadas = Cita.objects.filter(paciente=paciente, estado='REALIZADO').exists()
    
    # Filtrar por doctor si es doctor y no superuser
    if request.user.groups.filter(name=DOCTOR_GROUP_NAME).exists() and not request.user.is_superuser:
        citas = citas.filter(doctor=request.user)
    
    # Obtener parámetro de filtro por estado
    estado = request.GET.get('estado', '')
    
    # Aplicar filtro por estado
    if estado:
        citas = citas.filter(estado=estado)
    
    # Paginación
    paginator = Paginator(citas, 9)  # 9 citas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    is_doctor = request.user.groups.filter(name=DOCTOR_GROUP_NAME).exists() and not request.user.is_superuser
    
    return render(request, 'home_citas.html', {
        'paciente': paciente,
        'citas': page_obj.object_list,
        'page_obj': page_obj,
        'estado': estado,
        'is_doctor': is_doctor,
        'tiene_citas_realizadas': tiene_citas_realizadas,
    })


@_has_perms("JyGDreams.add_pago", "JyGDreams.change_citaprocedimiento")
def agregar_pago(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    # Verifica si ya existe un pago para esta cita
    if Pago.objects.filter(cita=cita).exists():
        messages.warning(request, "Ya se ha registrado un pago para esta cita.")
        return redirect('home_citas', paciente_id=cita.paciente.id)

    cita_procedimientos = CitaProcedimiento.objects.filter(cita=cita)
    monto_final = sum([cp.procedimiento.costo for cp in cita_procedimientos])

    if request.method == 'POST':
        # Guardar descuentos por procedimiento
        errores = []
        for cp in cita_procedimientos:
            descuento_key = f'descuento_{cp.id}'
            descuento = request.POST.get(descuento_key, '0')
            try:
                descuento = Decimal(descuento) if descuento else Decimal('0')
            except (ValueError, TypeError):
                descuento = Decimal('0')
            
            # Validar el descuento
            if descuento < 0:
                errores.append(f"El descuento del procedimiento {cp.procedimiento.titulo} no puede ser negativo.")
            elif descuento > cp.procedimiento.costo:
                errores.append(f"El descuento del procedimiento {cp.procedimiento.titulo} no puede exceder su costo de C${cp.procedimiento.costo:.2f}.")
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'add_pago.html', {
                'cita': cita,
                'cita_procedimientos': cita_procedimientos,
                'monto_final': monto_final
            })
        
        # Si no hay errores, guardar todos los descuentos
        for cp in cita_procedimientos:
            descuento_key = f'descuento_{cp.id}'
            descuento = request.POST.get(descuento_key, '0')
            try:
                descuento = Decimal(descuento) if descuento else Decimal('0')
            except (ValueError, TypeError):
                descuento = Decimal('0')
            cp.descuento = descuento
            cp.save()
        
        # Refrescar los procedimientos desde la base de datos para asegurar que los descuentos estén guardados
        cita_procedimientos = CitaProcedimiento.objects.filter(cita=cita)
        
        pago = Pago.objects.create(
            cita=cita,
            fecha=timezone.localdate(),
            total=0
        )
        # El método save() del modelo Pago calculará el total automáticamente
        cita.estado = 'REALIZADO'
        cita.save()
        messages.success(request, "Pago registrado exitosamente.")
        return redirect('home_citas', paciente_id=cita.paciente.id)

    return render(request, 'add_pago.html', {
        'cita': cita,
        'cita_procedimientos': cita_procedimientos,
        'monto_final': monto_final
    })

@_has_perms("JyGDreams.change_pago", "JyGDreams.change_citaprocedimiento")
def editar_pago(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    cita_procedimientos = CitaProcedimiento.objects.filter(cita=cita)
    CitaProcedimientoFormSet = modelformset_factory(CitaProcedimiento, fields=('id', 'descuento',), extra=0)
    pago = Pago.objects.filter(cita=cita).first()

    if request.method == 'POST':
        formset = CitaProcedimientoFormSet(request.POST, queryset=cita_procedimientos)
        if formset.is_valid():
            # Validar cada descuento antes de guardar
            errores = []
            for form in formset:
                if form.is_valid():
                    cp = form.instance
                    descuento = form.cleaned_data.get('descuento', Decimal('0'))
                    if descuento < 0:
                        errores.append(f"El descuento del procedimiento {cp.procedimiento.titulo} no puede ser negativo.")
                    elif descuento > cp.procedimiento.costo:
                        errores.append(f"El descuento del procedimiento {cp.procedimiento.titulo} no puede exceder su costo de C${cp.procedimiento.costo:.2f}.")
            
            if errores:
                for error in errores:
                    messages.error(request, error)
                monto_final = sum([cp.subtotal for cp in cita_procedimientos])
                return render(request, 'edit_pago.html', {
                    'cita': cita,
                    'formset': formset,
                    'cita_procedimientos': cita_procedimientos,
                    'monto_final': monto_final,
                })
            
            formset.save()
            # Refresca los procedimientos desde la base de datos
            cita_procedimientos = CitaProcedimiento.objects.filter(cita=cita)
            if pago:
                pago.save()  # Esto recalcula el total usando los subtotales
            messages.success(request, "Pago editado correctamente.")
            return redirect('detalle_pago', cita_id=cita.id)
        else:
            print(formset.errors)
    else:
        formset = CitaProcedimientoFormSet(queryset=cita_procedimientos)

    monto_final = sum([cp.subtotal for cp in cita_procedimientos])
    return render(request, 'edit_pago.html', {
        'cita': cita,
        'formset': formset,
        'cita_procedimientos': cita_procedimientos,
        'monto_final': monto_final,
    })

@permission_required("JyGDreams.view_pago", raise_exception=True)
def detalle_pago(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    pago = Pago.objects.filter(cita=cita).first()
    if not pago:
        messages.warning(request, "Primero debe registrar el pago para ver el detalle")
        return redirect('home_citas', paciente_id=cita.paciente.id)
    cita_procedimientos = CitaProcedimiento.objects.filter(cita=cita)
    # Usar el total del pago que ya incluye los descuentos aplicados
    monto_final = pago.total
    subtotal_total = sum([cp.procedimiento.costo for cp in cita_procedimientos])
    descuento_total = sum([cp.descuento for cp in cita_procedimientos])
    paciente = cita.paciente

    return render(request, 'detail_pago.html', {
        'cita': cita,
        'pago': pago,
        'cita_procedimientos': cita_procedimientos,
        'monto_final': monto_final,
        'subtotal_total': subtotal_total,
        'descuento_total': descuento_total,
        'paciente': paciente,
    })
    
@permission_required("JyGDreams.view_paciente", raise_exception=True)
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

@permission_required("JyGDreams.view_paciente", raise_exception=True)
def ajax_sugerencias_pacientes(request):
    q = request.GET.get('q', '')
    sugerencias = Paciente.objects.filter(
        Q(nombre__icontains=q) | Q(apellido__icontains=q)
    ).values_list('nombre', flat=True).distinct()[:5]
    return JsonResponse(list(sugerencias), safe=False)


@permission_required("JyGDreams.view_cita", raise_exception=True)
def ajax_filtrar_pacientes(request):
    query = request.GET.get('q', '')
    fecha = request.GET.get('fecha', '')
    orden = request.GET.get('orden', '')
    page_number = request.GET.get('page', 1)

    pacientes = Paciente.objects.all()

    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query)
        )

    if fecha:
        pacientes = pacientes.filter(
            Exists(
                Cita.objects.filter(
                    paciente=OuterRef('pk'),
                    fecha=fecha
                )
            )
        )

    if orden == 'alfabetico':
        pacientes = pacientes.order_by('nombre', 'apellido')
    elif orden == 'fecha':
        # Obtener la fecha actual
        fecha_actual = timezone.localdate()
        # Filtrar solo pacientes que tengan citas futuras con estados válidos
        pacientes = pacientes.filter(
            Exists(
                Cita.objects.filter(
                    paciente=OuterRef('pk'),
                    estado__in=['AGENDADO', 'REPROGRAMADO'],
                    fecha__gte=fecha_actual
                )
            )
        ).annotate(
            proxima_cita=Subquery(
                Cita.objects.filter(
                    paciente=OuterRef('pk'),
                    estado__in=['AGENDADO', 'REPROGRAMADO'],
                    fecha__gte=fecha_actual
                ).order_by('fecha').values('fecha')[:1]
            )
        ).order_by('proxima_cita')

    cita_filter = Q(cita__estado__in=['AGENDADO', 'REPROGRAMADO'])
    if request.user.groups.filter(name=DOCTOR_GROUP_NAME).exists() and not request.user.is_superuser:
        cita_filter &= Q(cita__doctor=request.user)

    pacientes = pacientes.annotate(
        has_expediente=Exists(Expediente.objects.filter(paciente=OuterRef('pk'))),
        citas_por_atender=Count('cita', filter=cita_filter, distinct=True)
    )

    # Paginación
    paginator = Paginator(pacientes, 6)
    page_obj = paginator.get_page(page_number)

    # Renderiza el bloque parcial con paginación y filtros
    html = render_to_string(
        'partials/cards_pacientes_block.html',
        {
            'pacientes': page_obj.object_list,
            'page_obj': page_obj,
            'query': query,
            'fecha': fecha,
            'orden': orden,
        },
        request=request
    )
    return JsonResponse({'html': html})
# Create your views here.

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url="login")
def estadisticas(request):
    # Filtros de fechas
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Obtener solo las citas que tienen pagos asociados (citas pagadas)
    citas_pagadas = Cita.objects.filter(pago__isnull=False)
    
    # Aplicar filtros de fecha a las citas pagadas
    if fecha_inicio:
        citas_pagadas = citas_pagadas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        citas_pagadas = citas_pagadas.filter(fecha__lte=fecha_fin)
    
    # Obtener los pagos correspondientes a las citas filtradas
    pagos = Pago.objects.filter(cita__in=citas_pagadas)
    
    # Ganancias totales (suma de todos los pagos en el rango)
    ganancias_totales = pagos.aggregate(total=Sum('total'))['total'] or 0
    
    # Citas atendidas (citas pagadas) en el rango de fechas
    total_citas = citas_pagadas.count()
    
    # Procedimientos realizados y ganancias por procedimiento
    procedimientos = Procedimiento.objects.all()
    ganancias_por_procedimiento = []
    cantidad_por_procedimiento = []
    
    for proc in procedimientos:
        # Todas las citas pagadas con ese procedimiento en el rango de fechas
        citas_proc = CitaProcedimiento.objects.filter(
            procedimiento=proc, 
            cita__in=citas_pagadas
        )
        cantidad = citas_proc.count()
        
        # Ganancia por procedimiento: suma de los subtotales (costo - descuento) de cada procedimiento
        ganancia = sum([float(cp.subtotal) for cp in citas_proc])
        
        # Solo agregar procedimientos que tengan datos
        if cantidad > 0:
            ganancias_por_procedimiento.append({
                'titulo': proc.titulo,
                'ganancia': ganancia
            })
            cantidad_por_procedimiento.append({
                'titulo': proc.titulo,
                'cantidad': cantidad
            })
    
    # Total de procedimientos realizados
    total_procedimientos = sum([c['cantidad'] for c in cantidad_por_procedimiento])
    
    # Datos para el gráfico de pastel (veces realizado)
    labels_veces = [c['titulo'] for c in cantidad_por_procedimiento]
    data_veces = [c['cantidad'] for c in cantidad_por_procedimiento]
    
    context = {
        'ganancias_totales': ganancias_totales,
        'total_procedimientos': total_procedimientos,
        'total_citas': total_citas,
        'ganancias_por_procedimiento': ganancias_por_procedimiento,
        'cantidad_por_procedimiento': cantidad_por_procedimiento,
        'labels_veces': labels_veces,
        'data_veces': data_veces,
        'fecha_inicio': fecha_inicio or '',
        'fecha_fin': fecha_fin or '',
    }
    return render(request, 'dashboard.html', context)

@permission_required("JyGDreams.view_cita", raise_exception=True)
def generar_pdf_citas(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener solo las citas pagadas (realizadas)
    citas_realizadas = Cita.objects.filter(
        paciente=paciente,
        pago__isnull=False
    ).order_by('fecha')
    
    # Crear el buffer para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Centrado
        textColor=colors.darkgreen  # Cambiado a verde
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        alignment=1,  # Centrado
        textColor=colors.darkgreen
    )
    
    # Agregar logo justo arriba del título principal
    logo_path = os.path.join(settings.STATIC_ROOT, 'JyGDreams', 'img', 'icon-clinica.png')
    # Si no existe en STATIC_ROOT, usar STATICFILES_DIRS o la ruta relativa
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'JyGDreams', 'static', 'JyGDreams', 'img', 'icon-clinica.png')
    
    if os.path.exists(logo_path):
        # Crear imagen con tamaño apropiado (1 pulgada de ancho)
        logo = Image(logo_path, width=1*inch, height=1*inch)
        # Posicionar centrado
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 10))  # Espacio después del logo
    
    # Título principal
    elements.append(Paragraph("Clínica Estética JyGDreams", title_style))
    elements.append(Spacer(1, 20))
    
    # Información del paciente
    elements.append(Paragraph(f"<b>Paciente:</b> {paciente.nombre} {paciente.apellido}", styles['Normal']))
    elements.append(Paragraph(f"<b>Ocupación:</b> {paciente.ocupacion}", styles['Normal']))
    elements.append(Paragraph(f"<b>Teléfono:</b> {paciente.telefono}", styles['Normal']))
    elements.append(Paragraph(f"<b>Correo:</b> {paciente.correo}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Subtítulo
    elements.append(Paragraph("Citas Realizadas", subtitle_style))
    elements.append(Spacer(1, 15))
    
    if citas_realizadas.exists():
        # Preparar datos para la tabla
        table_data = [
            ['Fecha', 'Procedimientos', 'Precios', 'Total']
        ]
        
        total_general = 0.0
        
        for cita in citas_realizadas:
            # Obtener los CitaProcedimiento de la cita para considerar descuentos
            cps = CitaProcedimiento.objects.filter(cita=cita).select_related('procedimiento')
            procedimientos_texto = []
            precios_texto = []
            total_cita = 0.0
            
            for cp in cps:
                procedimientos_texto.append(cp.procedimiento.titulo)
                precios_texto.append(f"C$ {float(cp.subtotal):,.2f}")  # subtotal = costo - descuento
                total_cita += float(cp.subtotal)
            
            fecha_formateada = cita.fecha.strftime("%d/%m/%Y")
            table_data.append([
                fecha_formateada,
                '\n'.join(procedimientos_texto) if procedimientos_texto else 'Sin procedimientos',
                '\n'.join(precios_texto) if precios_texto else '-',
                f"C$ {total_cita:,.2f}"
            ])
            
            total_general += total_cita
        
        # Agregar fila de total general
        table_data.append(['', '', 'TOTAL GENERAL', f"C$ {total_general:,.2f}"])
        
        # Crear tabla
        table = Table(table_data, colWidths=[1.2*inch, 2.5*inch, 1.5*inch, 1.2*inch])
        
        # Estilo de la tabla
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -2), 'LEFT'),
            ('ALIGN', (2, 1), (2, -2), 'RIGHT'),
            ('ALIGN', (3, 1), (3, -2), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Total de citas realizadas:</b> {citas_realizadas.count()}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    else:
        elements.append(Paragraph("No hay citas realizadas para este paciente.", styles['Normal']))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el valor del buffer y devolver respuesta
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="citas_realizadas_{paciente.apellido}_{paciente.nombre}.pdf"'
    response.write(pdf)
    return response

@permission_required("JyGDreams.view_cita", raise_exception=True)
def ajax_filtrar_citas(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    citas = Cita.objects.filter(paciente=paciente).order_by('-fecha', '-hora')
    
    # Obtener parámetros
    estado = request.GET.get('estado', '')
    page_number = request.GET.get('page', 1)
    
    # Aplicar filtro por estado
    if estado:
        citas = citas.filter(estado=estado)
    
    # Paginación
    paginator = Paginator(citas, 9)  # 9 citas por página
    page_obj = paginator.get_page(page_number)
    
    # Renderiza el bloque parcial con paginación y filtros
    html = render_to_string(
        'partials/citas_block.html',
        {
            'citas': page_obj.object_list,
            'page_obj': page_obj,
            'estado': estado,
        },
        request=request
    )
    return JsonResponse({'html': html})

@permission_required("JyGDreams.view_expediente", raise_exception=True)
def ajax_filtrar_expedientes(request):
    query = request.GET.get('q', '')
    tiene_expediente = request.GET.get('tiene_expediente', '')
    page_number = request.GET.get('page', 1)
    
    # Convertir page_number a entero
    try:
        page_number = int(page_number)
    except (ValueError, TypeError):
        page_number = 1
    
    pacientes = Paciente.objects.all()
    
    # Filtro por nombre/apellido
    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query)
        )
    
    # Filtro por si tiene expediente o no
    if tiene_expediente == 'si':
        pacientes = pacientes.filter(expediente__isnull=False)
    elif tiene_expediente == 'no':
        pacientes = pacientes.filter(expediente__isnull=True)
    
    # Agrega un campo booleano para mostrar si el paciente tiene expediente
    pacientes = pacientes.annotate(
        has_expediente=Exists(Expediente.objects.filter(paciente=OuterRef('pk')))
    )
    
    # Paginación
    paginator = Paginator(pacientes, 6)  # 6 pacientes por página
    page_obj = paginator.get_page(page_number)
    
    # Renderiza el bloque parcial con paginación y filtros
    html = render_to_string(
        'partials/expedientes_block.html',
        {
            'pacientes': page_obj.object_list,
            'page_obj': page_obj,
            'query': query,
            'tiene_expediente': tiene_expediente,
        },
        request=request
    )
    return JsonResponse({'html': html})

@user_passes_test(lambda u: u.is_superuser, login_url="login")
def lista_usuarios(request):
    query = request.GET.get('q', '')
    usuarios = User.objects.filter(groups__name__in=ROLE_GROUP_NAMES).distinct()

    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    # Paginación
    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=user_id)
        if action == 'activate':
            user.is_active = True
            user.save()
            messages.success(request, f'Usuario {user.username} activado.')
        elif action == 'deactivate':
            user.is_active = False
            user.save()
            messages.success(request, f'Usuario {user.username} desactivado.')
        return redirect('lista_usuarios')

    return render(request, 'tabla_usuarios.html', {
        'usuarios': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
    })

@permission_required("JyGDreams.view_expediente", raise_exception=True)
def generar_pdf_expediente(request, expediente_id):
    expediente = get_object_or_404(Expediente, id=expediente_id)
    paciente = expediente.paciente
    habito = Habito.objects.filter(expediente=expediente).first()
    biotipo = ExpedienteBiotipo.objects.filter(expediente=expediente).first()
    cuidados = ExpedienteCuidadoPiel.objects.filter(expediente=expediente)
    cuidados_nombres = [c.cuidado.nombre for c in cuidados]
    otro_valor = ""
    for c in cuidados:
        if c.cuidado.nombre == "Otros":
            otro_valor = c.otro

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=18,
        alignment=1,
        textColor=colors.white,
        backColor=colors.HexColor('#198754'),
        leading=24,
        borderPadding=(8, 8, 8, 8),
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        alignment=0,
        textColor=colors.HexColor('#198754'),
        leading=18,
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#198754'),
        spaceAfter=8,
        spaceBefore=12,
        leading=16,
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10.5,
        leading=14,
    )

    # Cabecera con fondo y logo
    header_table_data = []
    logo_path = os.path.join(settings.STATIC_ROOT, 'JyGDreams', 'img', 'icon-clinica.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'JyGDreams', 'static', 'JyGDreams', 'img', 'icon-clinica.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=0.9*inch, height=0.9*inch)
        logo.hAlign = 'LEFT'
        header_table_data.append([logo, Paragraph("<b>Clínica Estética JyGDreams</b>", title_style)])
        header_table = Table(header_table_data, colWidths=[1*inch, 5.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#198754')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(header_table)
    else:
        elements.append(Paragraph("Clínica Estética JyGDreams", title_style))
    elements.append(Spacer(1, 18))

    # Info paciente
    elements.append(Paragraph("<b>Datos del Paciente</b>", section_title))
    paciente_data = [
        ["Nombre", f"{paciente.nombre} {paciente.apellido}"],
        ["Ocupación", paciente.ocupacion],
        ["Teléfono", paciente.telefono],
        ["Correo", paciente.correo],
    ]
    paciente_table = Table(paciente_data, colWidths=[1.7*inch, 4.3*inch])
    paciente_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e9f7ef')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#198754')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#b2dfdb')),
    ]))
    elements.append(paciente_table)
    elements.append(Spacer(1, 10))

    # Expediente info
    elements.append(Paragraph("<b>Expediente Clínico</b>", section_title))
    expediente_data = [
        ["Fecha de Registro", expediente.fecha_registro.strftime('%d/%m/%Y')],
        ["Uso de Marcapasos", "Sí" if expediente.usa_marcapasos == 'si' else "No"]
    ]
    expediente_table = Table(expediente_data, colWidths=[1.7*inch, 4.3*inch])
    expediente_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f9fbe7')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#b7950b')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#f7ca18')),
    ]))
    elements.append(expediente_table)
    elements.append(Spacer(1, 10))

    # Hábitos
    elements.append(Paragraph("<b>Hábitos</b>", section_title))
    if habito:
        habitos_data = [
            ["Vasos de agua", habito.vasos_agua],
            ["Trasnoche", habito.trasnoche],
            ["Consumo Tabaco", habito.tabaco],
            ["Consumo Café", habito.cafe],
            ["Consumo Licor", habito.licor],
            ["Medicamentos", habito.medicamentos],
            ["Suplementos", habito.suplementos],
        ]
        habitos_table = Table(habitos_data, colWidths=[1.7*inch, 4.3*inch])
        habitos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1565c0')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#90caf9')),
        ]))
        elements.append(habitos_table)
    else:
        elements.append(Paragraph("No hay información de hábitos registrada.", normal_style))
    elements.append(Spacer(1, 10))

    # Biotipo
    elements.append(Paragraph("<b>Biotipo Cutáneo</b>", section_title))
    if biotipo:
        elements.append(Paragraph(biotipo.biotipo.nombre, normal_style))
    else:
        elements.append(Paragraph("No registrado.", normal_style))
    elements.append(Spacer(1, 10))

    # Cuidados de piel
    elements.append(Paragraph("<b>Cuidados de Piel</b>", section_title))
    if cuidados_nombres:
        lista = ', '.join([n for n in cuidados_nombres if n != 'Otros'])
        if otro_valor:
            lista += f", Otros: {otro_valor}"
        elements.append(Paragraph(lista, normal_style))
    else:
        elements.append(Paragraph("No registrado.", normal_style))
    elements.append(Spacer(1, 10))

    # Historial clínico
    elements.append(Paragraph("<b>Historial Clínico</b>", section_title))
    elements.append(Paragraph(expediente.historial_clinico or "No registrado.", normal_style))
    elements.append(Spacer(1, 16))

    # Citas realizadas
    elements.append(Paragraph("<b>Historial de Citas Realizadas</b>", section_title))
    citas_realizadas = Cita.objects.filter(
        paciente=paciente,
        pago__isnull=False
    ).order_by('fecha')
    
    if citas_realizadas.exists():
        # Preparar datos para la tabla
        table_data = [
            ['Fecha', 'Hora', 'Procedimientos']
        ]
        
        for cita in citas_realizadas:
            # Obtener procedimientos de la cita
            procedimientos_cita = cita.procedimientos.all()
            
            # Preparar información de procedimientos
            procedimientos_texto = []
            
            for proc in procedimientos_cita:
                procedimientos_texto.append(proc.titulo)
            
            # Formatear fecha y hora
            fecha_formateada = cita.fecha.strftime("%d/%m/%Y")
            hora_formateada = cita.hora.strftime("%H:%M")
            
            # Agregar fila a la tabla
            table_data.append([
                fecha_formateada,
                hora_formateada,
                '\n'.join(procedimientos_texto) if procedimientos_texto else 'Sin procedimientos'
            ])
        
        # Crear tabla
        table = Table(table_data, colWidths=[1.5*inch, 1*inch, 3.5*inch])
        
        # Estilo de la tabla
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8f5')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#198754')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Fecha centrada
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),   # Hora centrada
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),     # Procedimientos alineados a la izquierda
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Total de citas realizadas:</b> {citas_realizadas.count()}", normal_style))
    else:
        elements.append(Paragraph("No hay citas realizadas registradas.", normal_style))
    
    elements.append(Spacer(1, 16))

    # Fecha de generación
    elements.append(Paragraph(f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="expediente_{paciente.apellido}_{paciente.nombre}.pdf"'
    response.write(pdf)
    return response

@permission_required("JyGDreams.view_cita", raise_exception=True)
def calendario_citas(request):
    citas = Cita.objects.select_related('paciente').filter(estado__in=['AGENDADO', 'REPROGRAMADO'])
    eventos = []
    for cita in citas:
        procedimientos = ", ".join([p.titulo for p in cita.procedimientos.all()])
        eventos.append({
            "title": f"{cita.paciente.nombre} {cita.paciente.apellido} - {procedimientos}",
            "start": f"{cita.fecha}T{cita.hora}",
            "allDay": False,
        })
    eventos_json = json.dumps(eventos, ensure_ascii=False)
    return render(request, 'calendario_citas.html', {'eventos_json': eventos_json})


def mis_citas(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if not (request.user.groups.filter(name=DOCTOR_GROUP_NAME).exists() or request.user.is_superuser):
        return redirect("index")
    citas = Cita.objects.select_related("paciente").filter(
        doctor=request.user,
        estado__in=["AGENDADO", "REPROGRAMADO"],
    )
    eventos = []
    for cita in citas:
        procedimientos = ", ".join([p.titulo for p in cita.procedimientos.all()])
        eventos.append({
            "title": f"{cita.paciente.nombre} {cita.paciente.apellido} - {procedimientos}",
            "start": f"{cita.fecha}T{cita.hora}",
            "allDay": False,
        })
    eventos_json = json.dumps(eventos, ensure_ascii=False)
    return render(request, "calendario_citas.html", {"eventos_json": eventos_json})
