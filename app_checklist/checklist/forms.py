from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TodoList, Task, DynamicForm, Question, QuestionOption

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class TodoListForm(forms.ModelForm):
    class Meta:
        model = TodoList
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la lista'})
        }

class TaskForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('todo', 'Por Hacer'),
        ('progress', 'En Progreso'),
        ('done', 'Completado')
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'placeholder': 'Fecha de Entrega'
        })
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la tarea'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción (opcional)',
                'rows': 3
            })
        }

# Formularios para Dynamic Forms
class DynamicFormForm(forms.ModelForm):
    class Meta:
        model = DynamicForm
        fields = ['title', 'description', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del formulario'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del formulario (opcional)',
                'rows': 3
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'is_required', 'help_text', 
                 'min_value', 'max_value', 'min_label', 'max_label',
                 'rows_text', 'columns_text']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto de la pregunta'
            }),
            'question_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'help_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto de ayuda (opcional)'
            }),
            'min_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valor mínimo'
            }),
            'max_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valor máximo'
            }),
            'min_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Etiqueta para valor mínimo'
            }),
            'max_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Etiqueta para valor máximo'
            }),
            'rows_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Filas (una por línea)',
                'rows': 3
            }),
            'columns_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Columnas (una por línea)',
                'rows': 3
            }),
        }

class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto de la opción'
            })
        }