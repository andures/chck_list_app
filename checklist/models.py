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

# Modelos para Google Forms
class GForm(models.Model):
    """Modelo principal para formularios tipo Google Forms"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gforms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-updated_at']

class GQuestion(models.Model):
    """Modelo para preguntas del formulario"""
    QUESTION_TYPES = (
        ('short_text', 'Texto Corto'),
        ('paragraph', 'Párrafo'),
        ('multiple_choice', 'Opción Múltiple'),
        ('checkbox', 'Casillas de Verificación'),
        ('dropdown', 'Lista Desplegable'),
        ('linear_scale', 'Escala Lineal'),
        ('date', 'Fecha'),
        ('time', 'Hora'),
    )
    
    form = models.ForeignKey(GForm, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    help_text = models.CharField(max_length=255, blank=True, null=True)
    is_required = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    
    # Campos específicos para escala lineal
    min_value = models.IntegerField(default=1, null=True, blank=True)
    max_value = models.IntegerField(default=5, null=True, blank=True)
    min_label = models.CharField(max_length=50, blank=True, null=True)
    max_label = models.CharField(max_length=50, blank=True, null=True)
    
    # Imagen para la pregunta (opcional)
    image = models.ImageField(upload_to='gform_question_images/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.text} ({self.get_question_type_display()})"
    
    class Meta:
        ordering = ['position']

class GOption(models.Model):
    """Modelo para opciones de preguntas de selección"""
    question = models.ForeignKey(GQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    position = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.text
    
    class Meta:
        ordering = ['position']

class GResponse(models.Model):
    """Modelo para respuestas al formulario"""
    form = models.ForeignKey(GForm, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    respondent_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Respuesta a {self.form.title} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
    
    class Meta:
        ordering = ['-created_at']

class GAnswer(models.Model):
    """Modelo para respuestas individuales a preguntas"""
    response = models.ForeignKey(GResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(GQuestion, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    
    # Campos para archivos adjuntos en respuestas
    image = models.ImageField(upload_to='gform_answer_images/', blank=True, null=True)
    video = models.FileField(upload_to='gform_answer_videos/', blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"Respuesta a {self.question.text}"

class GSelectedOption(models.Model):
    """Modelo para opciones seleccionadas en preguntas de selección"""
    answer = models.ForeignKey(GAnswer, on_delete=models.CASCADE, related_name='selected_options')
    option = models.ForeignKey(GOption, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Opción seleccionada: {self.option.text}"