from django import forms
from .models import Proyecto, Task

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'tipo', 'fecha_deadline']
        widgets = {
            'fecha_deadline': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegura que la fecha se muestre pre-cargada en el input date
        if self.instance and self.instance.fecha_deadline:
            self.initial['fecha_deadline'] = self.instance.fecha_deadline.strftime('%Y-%m-%d')

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'column']

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # Quitar la opción de estado finalizado ('LISTO') para el desarrollador
        self.fields['column'].choices = [c for c in self.fields['column'].choices if c[0] != 'LISTO']

class ManagerTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to']