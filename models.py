from django.db import models
from django.contrib.auth.models import User

# --- 1. DEFINICIÓN DE OPCIONES EN CÓDIGO ---

ESTADOS_TAREA = [
    ('POR_HACER', 'Por Hacer'),
    ('EN_PROCESO', 'En Proceso'),
    ('EN_REVISION', 'En Revisión'),
    ('LISTO', 'Listo / Finalizado'),
]

TIPOS_PROYECTO = [
    ('FRONTEND', 'Frontend'),
    ('BACKEND', 'Backend'),
    ('BASE_DE_DATOS', 'Base de Datos'),
    ('PERSONALIZADO', 'Proyecto Personalizado'),
]

# Tareas que se crean automáticamente según el tipo de proyecto
TAREAS_PRECARGADAS = {
    'FRONTEND': [
        ('Análisis de Requerimientos UI',
         'Reunión con el cliente para definir mockups, paleta de colores y flujos de navegación.'),
        ('Diseño de Wireframes',
         'Crear prototipos de baja fidelidad para cada pantalla principal del sistema.'),
        ('Maquetación HTML/CSS Base',
         'Estructura semántica y estilos globales: variables CSS, tipografía y colores.'),
        ('Desarrollo de Componentes',
         'Implementar componentes reutilizables: botones, cards, formularios y modales.'),
        ('Integración con API/Backend',
         'Conectar vistas con endpoints REST y manejar estados de carga y error.'),
        ('Validaciones de Formularios',
         'Implementar validaciones en el lado del cliente con mensajes de error claros.'),
        ('Responsive Design',
         'Adaptar todas las vistas a dispositivos móviles, tablet y escritorio.'),
        ('Pruebas de Compatibilidad',
         'Verificar funcionamiento en Chrome, Firefox, Edge y Safari.'),
        ('Optimización de Rendimiento',
         'Minimizar CSS/JS, lazy loading de imágenes y revisión de Core Web Vitals.'),
        ('Entrega y Documentación',
         'Documentar componentes, estilos usados y guía de uso del proyecto.'),
    ],
    'BACKEND': [
        ('Análisis de Requerimientos del Sistema',
         'Definir endpoints, modelos de datos y reglas de negocio con el equipo.'),
        ('Diseño de Arquitectura',
         'Definir estructura de carpetas, patrones (MVC/MVT) y servicios externos.'),
        ('Configuración del Entorno',
         'Setup del proyecto: variables de entorno, dependencias y base de datos.'),
        ('Modelado de Base de Datos',
         'Definir y crear los modelos/entidades y sus relaciones en el ORM.'),
        ('Desarrollo de Endpoints REST',
         'Implementar los endpoints CRUD con validaciones y serialización de datos.'),
        ('Autenticación y Autorización',
         'Implementar JWT/sesiones, roles y permisos de acceso al sistema.'),
        ('Lógica de Negocio',
         'Desarrollar las reglas y procesos del dominio de la aplicación.'),
        ('Manejo de Errores y Logging',
         'Centralizar el manejo de excepciones y configurar logs del sistema.'),
        ('Pruebas Unitarias e Integración',
         'Escribir y ejecutar tests que cubran los casos críticos del sistema.'),
        ('Documentación de API',
         'Generar documentación (Swagger/Postman) y guía de despliegue del proyecto.'),
    ],
    'BASE_DE_DATOS': [
        ('Levantamiento de Información',
         'Entender los datos existentes, fuentes y necesidades del negocio.'),
        ('Diseño del Modelo Entidad-Relación',
         'Crear diagrama ER con entidades, atributos y cardinalidades.'),
        ('Normalización del Esquema',
         'Aplicar formas normales (1FN, 2FN, 3FN) para eliminar redundancias.'),
        ('Creación de Tablas y Relaciones',
         'Ejecutar scripts DDL para crear la estructura en el motor de base de datos.'),
        ('Definición de Índices y Constraints',
         'Crear índices, claves foráneas y restricciones de integridad referencial.'),
        ('Carga de Datos Iniciales (Seeding)',
         'Insertar datos de prueba o datos maestros necesarios para el sistema.'),
        ('Desarrollo de Procedimientos y Vistas',
         'Crear stored procedures, vistas y funciones reutilizables en la BD.'),
        ('Optimización de Consultas',
         'Analizar y optimizar queries lentas con EXPLAIN y ajuste de índices.'),
        ('Backup y Plan de Recuperación',
         'Configurar políticas de respaldo y realizar prueba de restauración.'),
        ('Documentación del Esquema',
         'Entregar diccionario de datos y diagrama actualizado del modelo final.'),
    ],
    'PERSONALIZADO': [],  # El gerente crea las tareas manualmente
}

# --- 1. MODELO DE COLUMNAS 
class KanbanColumn(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre")
    position = models.IntegerField(verbose_name="Posición")

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'columnas'
        verbose_name = 'Columna'
        verbose_name_plural = 'Columnas'


# --- 2. MODELO DE PROYECTO ---
class Proyecto(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_deadline = models.DateField(
        blank=True, null=True,
        verbose_name='Fecha Límite (Deadline)'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_PROYECTO,
        default='PERSONALIZADO',
        verbose_name='Tipo de Proyecto'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    def get_tipo_display_icon(self):
        icons = {
            'FRONTEND': '🎨',
            'BACKEND': '⚙️',
            'BASE_DE_DATOS': '🗄️',
            'PERSONALIZADO': '🔧',
        }
        return icons.get(self.tipo, '📂')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'proyectos'
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'


# --- 3. MODELO DE ETIQUETAS ---
class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=7, help_text="Código hexadecimal del color")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'etiquetas'
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'


# --- 4. MODELO PRINCIPAL: TAREAS 
class Task(models.Model):
    title = models.CharField(max_length=255, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")

    # CAMBIO AQUÍ: Ahora usa CharField con choices en lugar de ForeignKey
    column = models.CharField(
        max_length=20,
        choices=ESTADOS_TAREA,
        default='POR_HACER',
        verbose_name="Columna/Estado"
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='assigned_to',
        related_name='assigned_tasks',
        verbose_name="Asignado a"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='created_by',
        related_name='tasks_created',
        verbose_name="Creado por"
    )

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = True
        db_table = 'tareas'
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'


# --- 5. RELACIÓN MUCHOS A MUCHOS: TAREA - ETIQUETA ---
class TareaEtiqueta(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE)
    etiqueta = models.ForeignKey(Etiqueta, on_delete=models.CASCADE)
    asignado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tarea_etiquetas'
        verbose_name = "Relación Tarea-Etiqueta"
        verbose_name_plural = "Relaciones Tareas-Etiquetas"


# --- 6. DEPENDENCIAS ENTRE TAREAS ---
class Dependencia(models.Model):
    tarea_principal = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='bloquea_a'
    )

    tarea_dependiente = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='bloqueada_por'
    )

    class Meta:
        db_table = 'dependencias'
        verbose_name = "Dependencia"
        verbose_name_plural = "Dependencias"


# --- 7. HISTORIAL DE CAMBIOS ---
class HistorialTarea(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=50)
    estado_nuevo = models.CharField(max_length=50)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'historial_tareas'
        verbose_name = 'Historial de Tarea'
        verbose_name_plural = 'Historiales de Tareas'


# --- 8. TIEMPO DE TRABAJO ---
class TiempoTarea(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='tiempos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    horas_invertidas = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_registro = models.DateField()
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = 'tiempos_tareas'
        verbose_name = 'Tiempo de Tarea'
        verbose_name_plural = 'Tiempos de Tareas'


# --- 9. NOTAS / COMENTARIOS ---
class TaskNote(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, db_column='task_id', verbose_name="Tarea")
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', verbose_name="Usuario")
    content = models.TextField(verbose_name="Contenido")

    class Meta:
        managed = True
        db_table = 'notas'
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'


# --- 10. MODELO DE REPORTES ---
class Reporte(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Título")
    contenido = models.TextField(verbose_name="Contenido")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    tipo_reporte = models.CharField(max_length=50, verbose_name="Tipo de Reporte") 
    
    autor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Autor"
    )
    proyecto = models.ForeignKey(
        Proyecto, 
        on_delete=models.CASCADE, 
        related_name='reportes',
        verbose_name="Proyecto"
    )

    def __str__(self):
        return f"{self.titulo} - {self.fecha_creacion.strftime('%d/%m/%Y')}"

    class Meta:
        db_table = 'reporte'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes' 