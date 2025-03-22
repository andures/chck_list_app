from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils import timezone

#models todo_list
class TodoList(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

#models task
class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'Por Hacer'),
        ('progress', 'En Progreso'),
        ('done', 'Completado'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    position = models.IntegerField(default=0)
    todo_list = models.ForeignKey(TodoList, on_delete=models.CASCADE, related_name='tasks')
    due_date = models.DateTimeField(null=True, blank=True)
    
    def is_late(self):
        """determins if the task is late"""
        return self.due_date and self.due_date < timezone.now()
    
    def is_due_today(self):
        """determines if the task is due today"""
        if not self.due_date:
            return False
        today = timezone.now().date()
        return self.due_date.date() == today

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['status', 'position']

# Modelos para formularios dinámicos
class DynamicForm(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('short_text', 'Respuesta Corta'),
        ('paragraph', 'Párrafo'),
        ('multiple_choice', 'Opción Múltiple'),
        ('checkbox', 'Casillas de Verificación'),
        ('dropdown', 'Menú Desplegable'),
        ('file_upload', 'Carga de Archivos'),
        ('linear_scale', 'Escala Lineal'),
        ('multiple_choice_grid', 'Cuadrícula de Opción Múltiple'),
        ('checkbox_grid', 'Cuadrícula de Casillas de Verificación'),
        ('date', 'Fecha'),
        ('time', 'Hora'),
        ('datetime', 'Fecha y Hora'),
    )
    
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)
    position = models.IntegerField(default=0)
    help_text = models.CharField(max_length=255, blank=True, null=True)
    
    # Campos específicos para tipos de preguntas
    min_value = models.IntegerField(null=True, blank=True)  # Para escala lineal
    max_value = models.IntegerField(null=True, blank=True)  # Para escala lineal
    min_label = models.CharField(max_length=50, blank=True, null=True)  # Para escala lineal
    max_label = models.CharField(max_length=50, blank=True, null=True)  # Para escala lineal
    
    # Para cuadrículas
    rows_text = models.TextField(blank=True, null=True)  # Filas separadas por saltos de línea
    columns_text = models.TextField(blank=True, null=True)  # Columnas separadas por saltos de línea
    
    def __str__(self):
        return self.text
    
    class Meta:
        ordering = ['position']

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    position = models.IntegerField(default=0)
    
    def __str__(self):
        return self.text
    
    class Meta:
        ordering = ['position']

class FormResponse(models.Model):
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    
    def __str__(self):
        return f"Respuesta a {self.form.title}"

class Answer(models.Model):
    response = models.ForeignKey(FormResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Respuesta a {self.question.text}"

class SelectedOption(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='selected_options')
    option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Opción seleccionada: {self.option.text}"

class AnswerFile(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='form_answers/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.file_name