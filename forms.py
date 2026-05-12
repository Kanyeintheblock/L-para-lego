from django import forms
from .models import Proyecto
from .models import Proyecto, Task
class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Título del Proyecto',
                'class': 'form-control',
                'style': 'width: 100%; padding: 10px; border-radius: 5px;'
            }),
            'descripcion': forms.TextInput(attrs={
                'placeholder': 'Descripción del proyecto',
                'class': 'form-control',
                'style': 'width: 100%; padding: 10px; border-radius: 5px;'
            }),
        }
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'column']