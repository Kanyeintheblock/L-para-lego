"""
SISTEMA DE GESTIÓN DE ACTIVIDADES 
Descripción: Gestión de autenticación, registro con restricciones robustas y Dashboard.
"""

import re  # Módulo para Expresiones Regulares
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages 
from django.shortcuts import render, redirect, get_object_or_404
from .models import Proyecto, Task, TAREAS_PRECARGADAS
from .forms import ProyectoForm, TaskForm, ManagerTaskForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q


# 1. VISTA DE LOGIN
def login_usuario(request):
    error = None
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        clave = request.POST.get('password')
        
        # El sistema aplica el algoritmo de cifrado y compara el hash
        user = authenticate(request, username=usuario, password=clave)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Correo o contraseña incorrectos."

    return render(request, 'ventas/index.html', {'error': error})

# 2. VISTA DE REGISTRO CON RESTRICCIONES ACTUALIZADAS
def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo_web = request.POST.get('correo') 
        clave_web = request.POST.get('pass1') 

        # --- RESTRICCIONES DE DOMINIO (VALIDACIONES) ---
        
        # 1. Restricción: Nombre (Solo letras y espacios)
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            messages.error(request, 'El nombre solo puede contener letras.')
            return render(request, 'ventas/registro.html')

        # 2. Restricción: Apellido (Solo letras y espacios) - ¡CORREGIDO!
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            messages.error(request, 'El apellido solo puede contener letras.')
            return render(request, 'ventas/registro.html')

        # 3. Restricción: Estructura de correo válida
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', correo_web):
            messages.error(request, 'Formato de correo inválido.')
            return render(request, 'ventas/registro.html')

        # 4. Restricción: Contraseña Robusta - ¡ACTUALIZADO!
        # Requisitos: Mínimo 8 caracteres, letras, números y al menos un símbolo (punto, coma, @, etc.)
        regex_clave = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[.!@#$%^&*(),?":{}|<>]).{8,}$'
        if not re.match(regex_clave, clave_web):
            messages.error(request, 'La clave debe tener al menos 8 caracteres, letras, números y un símbolo (.,@#).')
            return render(request, 'ventas/registro.html')

        # --- PERSISTENCIA Y SEGURIDAD ---
        if correo_web and clave_web:
            # Verifica si el usuario ya existe
            if not User.objects.filter(username=correo_web).exists():
                
                # create_user genera automáticamente el HASH de seguridad
                nuevo_usuario = User.objects.create_user(
                    username=correo_web,
                    email=correo_web,
                    password=clave_web, 
                    first_name=nombre,
                    last_name=apellido
                )
                nuevo_usuario.save() # Guarda en PostgreSQL
                
                messages.success(request, '🚀 ¡Cuenta creada con éxito! Ya puedes entrar.')
                return redirect('login_usuario') 
            else:
                messages.error(request, 'Este correo ya está registrado.')
    
    return render(request, 'ventas/registro.html')

# 3. VISTA DEL HOME
@login_required
def home(request):
    from datetime import date
    proyectos = []
    if request.user.is_authenticated:
        proyectos = Proyecto.objects.filter(activo=True)
        return render(request, 'ventas/home.html', {
            'proyectos': proyectos,
            'today': date.today(),
        })
    else:
        return redirect('login_usuario')

# 4. VISTA DE LOGOUT
def cerrar_sesion(request):
    logout(request)
    return redirect('login_usuario')

@login_required
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save()
            # --- Crear tareas pre-cargadas según el tipo de proyecto ---
            tareas_tipo = TAREAS_PRECARGADAS.get(proyecto.tipo, [])
            for titulo, descripcion in tareas_tipo:
                Task.objects.create(
                    title=titulo,
                    description=descripcion,
                    proyecto=proyecto,
                    created_by=request.user,
                    assigned_to=request.user,  # sin asignar aún: se asigna después
                    column='POR_HACER',
                )
            if tareas_tipo:
                messages.success(
                    request,
                    f'✅ Proyecto "{proyecto.nombre}" creado con {len(tareas_tipo)} tareas pre-cargadas. '
                    f'Ahora asigna cada tarea a un desarrollador.'
                )
            else:
                messages.success(request, '✅ Proyecto creado con éxito. Puedes crear las tareas manualmente.')
            return redirect('home')
    else:
        form = ProyectoForm()
    return render(request, 'ventas/crear_proyecto.html', {'form': form})
    
@login_required
def gestionar_asignaciones(request, proyecto_id):
    """
    Panel del gerente para gestionar la asignación de tareas de un proyecto.
    Permite:
      - Asignar desarrollador a una tarea individual (POST action=individual)
      - Asignar todas las tareas sin desarrollador a un mismo usuario (POST action=asignar_todos)
      - Crear nuevas tareas manualmente (POST action=nueva_tarea)
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    desarrolladores = User.objects.filter(is_active=True).order_by('first_name', 'username')
    tareas = Task.objects.filter(proyecto=proyecto).order_by('id')

    if request.method == 'POST':
        action = request.POST.get('action')

        # --- Asignación individual de una tarea ---
        if action == 'individual':
            tarea_id = request.POST.get('tarea_id')
            dev_id   = request.POST.get('dev_id')
            tarea = get_object_or_404(Task, pk=tarea_id, proyecto=proyecto)
            dev   = get_object_or_404(User, pk=dev_id)
            tarea.assigned_to = dev
            tarea.save()
            messages.success(request, f'✅ Tarea "{tarea.title}" asignada a {dev.get_full_name() or dev.username}.')

        # --- Asignar TODAS las tareas sin asignar a un desarrollador ---
        elif action == 'asignar_todos':
            dev_id = request.POST.get('dev_id_todos')
            dev    = get_object_or_404(User, pk=dev_id)
            # Solo reasigna las que aún tienen assigned_to = gerente (el que creó el proyecto)
            sin_asignar = tareas.filter(assigned_to=proyecto.tasks.first().created_by if tareas.exists() else request.user)
            count = sin_asignar.count()
            sin_asignar.update(assigned_to=dev)
            messages.success(request, f'✅ {count} tarea(s) asignadas a {dev.get_full_name() or dev.username}.')

        # --- Crear nueva tarea (solo para Proyecto Personalizado) ---
        elif action == 'nueva_tarea':
            titulo      = request.POST.get('titulo', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            dev_id      = request.POST.get('dev_id_nueva')
            if titulo:
                dev = get_object_or_404(User, pk=dev_id) if dev_id else request.user
                Task.objects.create(
                    title=titulo,
                    description=descripcion,
                    proyecto=proyecto,
                    created_by=request.user,
                    assigned_to=dev,
                    column='POR_HACER',
                )
                messages.success(request, f'✅ Tarea "{titulo}" creada y asignada correctamente.')
            else:
                messages.error(request, '⚠️ El título de la tarea no puede estar vacío.')

        return redirect('gestionar_asignaciones', proyecto_id=proyecto.id)

    # --- Contexto para el template ---
    # Separar tareas asignadas vs. sin asignar (asignadas al gerente = pendientes)
    tareas_info = []
    gerente_ids = set(Task.objects.filter(proyecto=proyecto).values_list('created_by', flat=True))
    for tarea in tareas:
        asignada = tarea.assigned_to_id not in gerente_ids or tarea.assigned_to != tarea.created_by
        # Consideramos "sin asignar" si assigned_to == created_by (es el mismo gerente)
        sin_asignar = (tarea.assigned_to_id == tarea.created_by_id)
        tareas_info.append({
            'tarea': tarea,
            'sin_asignar': sin_asignar,
        })

    return render(request, 'ventas/gestionar_asignaciones.html', {
        'proyecto': proyecto,
        'desarrolladores': desarrolladores,
        'tareas_info': tareas_info,
        'total': tareas.count(),
        'sin_asignar': sum(1 for t in tareas_info if t['sin_asignar']),
    })


@login_required
def asignar_tarea(request, proyecto_id):
    """Redirecciona al nuevo panel de gestión de asignaciones."""
    return redirect('gestionar_asignaciones', proyecto_id=proyecto_id)

@login_required
def lista_devs(request):
    usuarios = User.objects.annotate(
        total_tareas=Count('assigned_tasks', filter=Q(assigned_tasks__proyecto__activo=True)),
        tareas_pendientes=Count('assigned_tasks', filter=Q(assigned_tasks__column='POR_HACER', assigned_tasks__proyecto__activo=True)),
        tareas_en_proceso=Count('assigned_tasks', filter=Q(assigned_tasks__column='EN_PROCESO', assigned_tasks__proyecto__activo=True)),
        tareas_en_revision=Count('assigned_tasks', filter=Q(assigned_tasks__column='EN_REVISION', assigned_tasks__proyecto__activo=True)),
        tareas_finalizadas=Count('assigned_tasks', filter=Q(assigned_tasks__column='LISTO', assigned_tasks__proyecto__activo=True))
    ).order_by('-total_tareas')
    
    return render(request, 'ventas/desarrolladores.html', {'usuarios': usuarios})

# 5. EDICIÓN DEL PROYECTO
def editar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == "POST":
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProyectoForm(instance=proyecto)
    return render(request, 'ventas/editar_proyecto.html', {'form': form, 'proyecto': proyecto})

# 6. INHABILITACION DEL PROYECTO
@login_required
def inhabilitar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == "POST":
        nombre = proyecto.nombre
        proyecto.activo = False
        proyecto.save()
        messages.success(request, f'⚠️ Proyecto "{nombre}" inhabilitado. Puedes restaurarlo desde la sección de proyectos inhabilitados.')
        return redirect('home')
    return redirect('home')

@login_required
def proyectos_inhabilitados(request):
    cancelados = Proyecto.objects.filter(activo=False)
    return render(request, 'ventas/cancelados.html', {'proyectos': cancelados})

@login_required
def restaurar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == "POST":
        nombre = proyecto.nombre
        proyecto.activo = True
        proyecto.save()
        messages.success(request, f'✅ Proyecto "{nombre}" restaurado correctamente.')
        return redirect('proyectos_inhabilitados')
    return redirect('proyectos_inhabilitados')

#Panel del desarollador
@login_required
def panel_desarrollador(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if not proyecto.activo:
        messages.error(request, 'Este proyecto se encuentra inhabilitado. No puedes ver ni gestionar sus tareas.')
        return redirect('home')
    
    # Si el desarrollador envía el formulario para crear una tarea
    if request.method == 'POST':
        form_tarea = TaskForm(request.POST)
        if form_tarea.is_valid():
            tarea = form_tarea.save(commit=False)
            tarea.proyecto = proyecto
            tarea.created_by = request.user
            tarea.save()
            messages.success(request, 'Tarea creada exitosamente.')
            return redirect('panel_desarrollador', proyecto_id=proyecto.id)
    else:
        form_tarea = TaskForm()
    
    # Obtener todas las tareas del proyecto
    tareas = Task.objects.filter(proyecto=proyecto)
    
    return render(request, 'ventas/desarrollador.html', {
        'proyecto': proyecto,
        'tareas': tareas,
        'form_tarea': form_tarea,
    })

# 7. INHABILITACIÓN DEL PROYECTO (alias para compatibilidad — redirige a inhabilitar)
@login_required
def eliminar_proyecto(request, pk):
    """Alias mantenido por compatibilidad. Redirige a inhabilitar_proyecto."""
    return inhabilitar_proyecto(request, pk)

@login_required
def eliminar_tarea(request, pk):
    tarea = get_object_or_404(Task, pk=pk)
    proyecto_id = tarea.proyecto.id
    if request.method == 'POST':
        # Un desarrollador solo puede borrar tareas que él mismo creó (y que no sean del gerente).
        # Un gerente (is_staff) puede borrar cualquier tarea.
        if request.user.is_staff or (tarea.created_by == request.user and not tarea.created_by.is_staff):
            tarea.delete()
            messages.success(request, '🗑️ Tarea eliminada correctamente.')
        else:
            messages.error(request, '⛔ No tienes permiso para eliminar esta tarea porque fue establecida por el gerente.')
    return redirect('panel_desarrollador', proyecto_id=proyecto_id)

@login_required
def finalizar_tarea(request, pk):
    tarea = get_object_or_404(Task, pk=pk)
    proyecto_id = tarea.proyecto.id
    if request.method == 'POST':
        tarea.column = 'EN_REVISION'
        tarea.save()
        messages.success(request, 'Tarea enviada a revisión.')
    return redirect('panel_desarrollador', proyecto_id=proyecto_id)

@login_required
def revision_tareas(request):
    # Obtener todas las tareas que están esperando revisión de proyectos activos
    tareas_revision = Task.objects.filter(column='EN_REVISION', proyecto__activo=True).order_by('-id')
    return render(request, 'ventas/revision_tareas.html', {'tareas': tareas_revision})

@login_required
def aprobar_tarea(request, pk):
    tarea = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        tarea.column = 'LISTO'
        tarea.save()
        messages.success(request, f'✅ Tarea "{tarea.title}" aprobada y finalizada.')
    return redirect('revision_tareas')