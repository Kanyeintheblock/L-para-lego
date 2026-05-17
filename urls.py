"""
Configuración de rutas (URLs) '.
Este archivo mapea las direcciones web (URLs) a las funciones de vistas (views) correspondientes.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.login_usuario, name='login_usuario'), 
    path('home/', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # Proyectos
    path('crear/', views.crear_proyecto, name='crear_proyecto'),
    path('editar-proyecto/<int:pk>/', views.editar_proyecto, name='editar_proyecto'),
    path('eliminar/<int:pk>/', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('inhabilitar-proyecto/<int:pk>/', views.inhabilitar_proyecto, name='inhabilitar_proyecto'),
    path('proyectos-inhabilitados/', views.proyectos_inhabilitados, name='proyectos_inhabilitados'),
    path('restaurar-proyecto/<int:pk>/', views.restaurar_proyecto, name='restaurar_proyecto'),

    # Tareas (Gerente)
    path('asignar-tarea/<int:proyecto_id>/', views.asignar_tarea, name='asignar_tarea'),
    path('gestionar-asignaciones/<int:proyecto_id>/', views.gestionar_asignaciones, name='gestionar_asignaciones'),
    
    # Equipos y Revisión (Gerente)
    path('desarrolladores/', views.lista_devs, name='lista_desarrolladores'),
    path('revision-tareas/', views.revision_tareas, name='revision_tareas'),
    path('aprobar-tarea/<int:pk>/', views.aprobar_tarea, name='aprobar_tarea'),

    # Panel Desarrollador
    path('panel_desarrollador/<int:proyecto_id>/', views.panel_desarrollador, name='panel_desarrollador'),
    path('eliminar-tarea/<int:pk>/', views.eliminar_tarea, name='eliminar_tarea'),
    path('finalizar-tarea/<int:pk>/', views.finalizar_tarea, name='finalizar_tarea'),
]
