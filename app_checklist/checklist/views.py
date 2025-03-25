from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib import messages
from .forms import UserRegistrationForm, TodoListForm, TaskForm, GFormForm, GQuestionForm, GOptionForm, GFormResponseForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .models import TodoList, Task, GForm, GQuestion, GOption, GResponse, GAnswer, GSelectedOption
import json
import os
from datetime import date, datetime

# Añadir al principio del archivo
from datetime import datetime

# Restaurar las importaciones de pytz al principio del archivo
from django.utils import timezone
import pytz

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    todo_lists = TodoList.objects.filter(user=request.user)
    recent_todo_lists = TodoList.objects.filter(user=request.user).order_by('-created_at')[:5]
    # Usar GForm en lugar de DynamicForm
    forms = GForm.objects.filter(user=request.user).order_by('-updated_at')[:5]
    return render(request, 'dashboard.html', {
        'todo_lists': todo_lists, 
        'recent_todo_lists': recent_todo_lists,
        'forms': forms
    })

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('dashboard')

@login_required
def todo_lists(request):
    """Muestra todas las listas de tareas del usuario"""
    lists = TodoList.objects.filter(user=request.user)

    for todo_list in lists:
        todo_list.todo_count = todo_list.tasks.filter(status='todo').count()
        todo_list.progress_count = todo_list.tasks.filter(status='progress').count()
        todo_list.done_count = todo_list.tasks.filter(status='done').count()

    return render(request, 'todo_lists.html', {'lists': lists})

@login_required
def create_todo_list(request):
    """Crea una nueva lista de tareas"""
    if request.method == 'POST':
        form = TodoListForm(request.POST)
        if form.is_valid():
            todo_list = form.save(commit=False)
            todo_list.user = request.user
            todo_list.save()
            return redirect('view_todo_list', list_id=todo_list.id)
    else:
        form = TodoListForm()
    return render(request, 'create_todo_list.html', {'form': form})

@login_required
def view_todo_list(request, list_id):
    """Muestra el detalle de una lista de tareas con sus tareas agrupadas por estado"""
    todo_list = get_object_or_404(TodoList, id=list_id)
    
    # Verificar que el usuario sea el propietario
    if todo_list.user != request.user:
        return HttpResponseForbidden("No tienes permiso para ver esta lista")
    
    # Agrupar tareas por estado
    tasks = {
        'todo': todo_list.tasks.filter(status='todo').order_by('position'),
        'progress': todo_list.tasks.filter(status='progress').order_by('position'),
        'done': todo_list.tasks.filter(status='done').order_by('position')
    }
    
    today_date = date.today()

    return render(request, 'view_todo_list.html', {
        'todo_list': todo_list,
        'tasks': tasks,
        'today_date': today_date
    })

@login_required
def add_task(request, list_id):
    """Agrega una nueva tarea a una lista"""
    todo_list = get_object_or_404(TodoList, id=list_id)
    
    # Verificar que el usuario sea el propietario
    if todo_list.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar esta lista")
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.todo_list = todo_list
            
            # Obtener el estado de la columna donde se agregará la tarea
            status = form.cleaned_data['status']
            task.status = status
            
            # Obtener la posición máxima actual para el estado
            max_position = Task.objects.filter(
                todo_list=todo_list, 
                status=status
            ).order_by('-position').first()
            
            if max_position:
                task.position = max_position.position + 1
            else:
                task.position = 0
            
            task.save()
            
            # Si es una solicitud AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status,
                    'position': task.position,
                    'due_date': task.due_date,
                })
            
            return redirect('view_todo_list', list_id=todo_list.id)
    else:
        form = TaskForm()
    
    return render(request, 'add_task.html', {
        'form': form,
        'todo_list': todo_list
    })

@login_required
def edit_task(request, task_id):
    """Edita una tarea existente"""
    task = get_object_or_404(Task, id=task_id)
    todo_list = task.todo_list
    
    # Verificar que el usuario sea el propietario
    if todo_list.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar esta tarea")
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            
            # Si es una solicitud AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status,
                    'position': task.position,
                    'due_date': task.due_date,
                })
            
            return redirect('view_todo_list', list_id=todo_list.id)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'edit_task.html', {
        'form': form,
        'task': task,
        'todo_list': todo_list
    })

@login_required
def delete_task(request, task_id):
    """Elimina una tarea"""
    task = get_object_or_404(Task, id=task_id)
    todo_list = task.todo_list
    
    # Verificar que el usuario sea el propietario
    if todo_list.user != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar esta tarea")
    
    if request.method == 'POST':
        task.delete()
        
        # Si es una solicitud AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('view_todo_list', list_id=todo_list.id)
    
    return render(request, 'delete_task.html', {
        'task': task,
        'todo_list': todo_list
    })

@login_required
def delete_todo_list(request, list_id):
    """Elimina una lista de tareas"""
    todo_list = get_object_or_404(TodoList, id=list_id, user=request.user)
    
    if request.method == 'POST':
        todo_list.delete()
        return redirect('todo_lists')
    
    return render(request, 'delete_todo_list.html', {'todo_list': todo_list})

@login_required
@require_POST
def update_task_status(request, task_id):
    """API para actualizar el estado de una tarea"""
    task = get_object_or_404(Task, id=task_id)
    todo_list = task.todo_list
    
    # Verificar que el usuario sea el propietario
    if todo_list.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para modificar esta tarea'}, status=403)
    
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in ['todo', 'progress', 'done']:
            return JsonResponse({'error': 'Estado no válido'}, status=400)
        
        # Actualizar el estado
        task.status = new_status
        task.save()
        
        return JsonResponse({
            'id': task.id,
            'status': task.status
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
def update_tasks_order(request, list_id):
    """API para actualizar el orden de las tareas"""
    todo_list = get_object_or_404(TodoList, id=list_id)
    
    # Verificar que el usuario sea el propietario
    if todo_list.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para modificar esta lista'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        with transaction.atomic():
            for status, tasks in data.items():
                for i, task_id in enumerate(tasks):
                    Task.objects.filter(id=task_id, todo_list=todo_list).update(
                        status=status,
                        position=i
                    )
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Vistas para Google Forms
@login_required
def gform_list(request):
    """Vista para listar todos los formularios del usuario"""
    forms = GForm.objects.filter(user=request.user)
    return render(request, 'forms_google/form_list.html', {'forms': forms})

@login_required
def gform_create(request):
    """Vista para crear un nuevo formulario"""
    if request.method == 'POST':
        form = GFormForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            messages.success(request, "Formulario creado correctamente")
            return redirect('gform_edit', form_id=new_form.id)
        else:
            # Añadir mensaje de error si el formulario no es válido
            messages.error(request, "Error al crear el formulario. Por favor, verifica los datos.")
    else:
        form = GFormForm()
    
    return render(request, 'forms_google/create_form.html', {'form': form})

@login_required
def gform_edit(request, form_id):
    """Vista para editar un formulario existente"""
    gform = get_object_or_404(GForm, id=form_id)
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para editar este formulario")
    
    if request.method == 'POST':
        form = GFormForm(request.POST, instance=gform)
        if form.is_valid():
            form.save()
            messages.success(request, "Formulario actualizado correctamente")
            return redirect('gform_edit', form_id=gform.id)
    else:
        form = GFormForm(instance=gform)
    
    # Obtener todas las preguntas del formulario
    questions = GQuestion.objects.filter(form=gform).order_by('position')
    
    return render(request, 'forms_google/edit_form.html', {
        'form': form,
        'gform': gform,
        'questions': questions,
        'question_form': GQuestionForm(),
        'option_form': GOptionForm()
    })

@login_required
def gform_delete(request, form_id):
    """Vista para eliminar un formulario"""
    gform = get_object_or_404(GForm, id=form_id)
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar este formulario")
    
    if request.method == 'POST':
        gform.delete()
        messages.success(request, "Formulario eliminado correctamente")
        return redirect('gform_list')
    
    return render(request, 'forms_google/delete_form.html', {'gform': gform})

@login_required
@require_POST
def gform_add_question(request, form_id):
    """Vista para añadir una pregunta al formulario"""
    gform = get_object_or_404(GForm, id=form_id)
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar este formulario")
    
    form = GQuestionForm(request.POST, request.FILES)
    if form.is_valid():
        question = form.save(commit=False)
        question.form = gform
        
        # Obtener la posición máxima actual
        max_position = GQuestion.objects.filter(form=gform).order_by('-position').first()
        if max_position:
            question.position = max_position.position + 1
        else:
            question.position = 0
        
        question.save()
        
        # Si es una solicitud AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': question.id,
                'text': question.text,
                'type': question.get_question_type_display()
            })
        
        messages.success(request, "Pregunta añadida correctamente")
        return redirect('gform_edit', form_id=gform.id)
    
    # Si hay errores en el formulario
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    messages.error(request, "Error al añadir la pregunta")
    return redirect('gform_edit', form_id=gform.id)

@login_required
@require_POST
def gform_edit_question(request, question_id):
    """Vista para editar una pregunta existente"""
    question = get_object_or_404(GQuestion, id=question_id)
    gform = question.form
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar este formulario")
    
    form = GQuestionForm(request.POST, request.FILES, instance=question)
    if form.is_valid():
        form.save()
        
        # Si es una solicitud AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': question.id,
                'text': question.text,
                'type': question.get_question_type_display()
            })
        
        messages.success(request, "Pregunta actualizada correctamente")
        return redirect('gform_edit', form_id=gform.id)
    
    # Si hay errores en el formulario
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    messages.error(request, "Error al actualizar la pregunta")
    return redirect('gform_edit', form_id=gform.id)

@login_required
@require_POST
def gform_delete_question(request, question_id):
    """Vista para eliminar una pregunta"""
    question = get_object_or_404(GQuestion, id=question_id)
    gform = question.form
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar este formulario")
    
    question.delete()
    
    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, "Pregunta eliminada correctamente")
    return redirect('gform_edit', form_id=gform.id)

@login_required
@require_POST
def gform_add_option(request, question_id):
    """Vista para añadir una opción a una pregunta"""
    question = get_object_or_404(GQuestion, id=question_id)
    gform = question.form
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar este formulario")
    
    # Verificar que la pregunta sea de un tipo que admite opciones
    if question.question_type not in ['multiple_choice', 'checkbox', 'dropdown']:
        return HttpResponseForbidden("Este tipo de pregunta no admite opciones")
    
    form = GOptionForm(request.POST)
    if form.is_valid():
        option = form.save(commit=False)
        option.question = question
        
        # Obtener la posición máxima actual
        max_position = GOption.objects.filter(question=question).order_by('-position').first()
        if max_position:
            option.position = max_position.position + 1
        else:
            option.position = 0
        
        option.save()
        
        # Si es una solicitud AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': option.id,
                'text': option.text
            })
        
        messages.success(request, "Opción añadida correctamente")
        return redirect('gform_edit', form_id=gform.id)
    
    # Si hay errores en el formulario
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    messages.error(request, "Error al añadir la opción")
    return redirect('gform_edit', form_id=gform.id)

@login_required
@require_POST
def gform_edit_option(request, option_id):
    """Vista para editar una opción existente"""
    option = get_object_or_404(GOption, id=option_id)
    question = option.question
    gform = question.form
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar este formulario")
    
    form = GOptionForm(request.POST, instance=option)
    if form.is_valid():
        form.save()
        
        # Si es una solicitud AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': option.id,
                'text': option.text
            })
        
        messages.success(request, "Opción actualizada correctamente")
        return redirect('gform_edit', form_id=gform.id)
    
    # Si hay errores en el formulario
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    messages.error(request, "Error al actualizar la opción")
    return redirect('gform_edit', form_id=gform.id)

@login_required
@require_POST
def gform_delete_option(request, option_id):
    """Vista para eliminar una opción"""
    option = get_object_or_404(GOption, id=option_id)
    question = option.question
    gform = question.form
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar este formulario")
    
    option.delete()
    
    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, "Opción eliminada correctamente")
    return redirect('gform_edit', form_id=gform.id)

@login_required
@require_POST
def gform_update_question_order(request, form_id):
    """Vista para actualizar el orden de las preguntas"""
    gform = get_object_or_404(GForm, id=form_id)
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para modificar este formulario'}, status=403)
    
    try:
        data = json.loads(request.body)
        question_ids = data.get('question_ids', [])
        
        with transaction.atomic():
            for i, question_id in enumerate(question_ids):
                GQuestion.objects.filter(id=question_id, form=gform).update(position=i)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def gform_update_option_order(request, question_id):
    """Vista para actualizar el orden de las opciones"""
    question = get_object_or_404(GQuestion, id=question_id)
    gform = question.form
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para modificar este formulario'}, status=403)
    
    try:
        data = json.loads(request.body)
        option_ids = data.get('option_ids', [])
        
        with transaction.atomic():
            for i, option_id in enumerate(option_ids):
                GOption.objects.filter(id=option_id, question=question).update(position=i)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def gform_toggle_publish(request, form_id):
    """Vista para publicar/despublicar un formulario"""
    gform = get_object_or_404(GForm, id=form_id)
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar este formulario")
    
    gform.is_published = not gform.is_published
    gform.save()
    
    status = "publicado" if gform.is_published else "despublicado"
    messages.success(request, f"Formulario {status} correctamente")
    
    return redirect('gform_edit', form_id=gform.id)

def gform_view(request, form_id):
    """Vista para ver y responder a un formulario"""
    gform = get_object_or_404(GForm, id=form_id)
    
    # Verificar que el formulario esté publicado o que el usuario sea el propietario
    if not gform.is_published and (request.user.is_anonymous or gform.user != request.user):
        return HttpResponseForbidden("Este formulario no está disponible")
    
    questions = GQuestion.objects.filter(form=gform).order_by('position')
    
    # Crear contexto para las preguntas de tipo escala lineal
    for question in questions:
        if question.question_type == 'linear_scale':
            min_val = question.min_value or 1
            max_val = question.max_value or 5
            question.range_values = range(min_val, max_val + 1)
    
    if request.method == 'POST':
        # Procesar la respuesta al formulario
        if not gform.is_published and request.user != gform.user:
            return HttpResponseForbidden("Este formulario no está aceptando respuestas")
        
        # Crear una nueva respuesta
        response = GResponse.objects.create(
            form=gform,
            respondent=request.user if request.user.is_authenticated else None,
            respondent_email=request.POST.get('email', None)
        )
        
        # Procesar cada pregunta
        for question in questions:
            field_name = f'question_{question.id}'
            file_field_name = f'file_{question.id}'
            url_field_name = f'url_{question.id}'
            
            if field_name in request.POST or file_field_name in request.FILES or url_field_name in request.POST:
                answer = GAnswer.objects.create(
                    response=response,
                    question=question
                )
                
                if field_name in request.POST:
                    if question.question_type in ['short_text', 'paragraph', 'date', 'time', 'linear_scale']:
                        answer.text_answer = request.POST.get(field_name)
                        answer.save()
                    
                    elif question.question_type in ['multiple_choice', 'dropdown']:
                        option_id = request.POST.get(field_name)
                        if option_id:
                            option = get_object_or_404(GOption, id=option_id)
                            GSelectedOption.objects.create(answer=answer, option=option)
                    
                    elif question.question_type == 'checkbox':
                        # Para checkbox, value puede ser una lista
                        option_ids = request.POST.getlist(field_name)
                        for option_id in option_ids:
                            option = get_object_or_404(GOption, id=option_id)
                            GSelectedOption.objects.create(answer=answer, option=option)
                
                # Procesar archivos adjuntos
                if file_field_name in request.FILES:
                    file = request.FILES[file_field_name]
                    if file.content_type.startswith('image/'):
                        answer.image = file
                    elif file.content_type.startswith('video/'):
                        answer.video = file
                    answer.save()
                
                # Procesar URL
                if url_field_name in request.POST and request.POST.get(url_field_name):
                    answer.file_url = request.POST.get(url_field_name)
                    answer.save()
        
        messages.success(request, "¡Gracias por tu respuesta!")
        return redirect('gform_thank_you', form_id=gform.id)
    
    return render(request, 'forms_google/view_form.html', {
        'gform': gform,
        'questions': questions,
        'is_owner': request.user == gform.user
    })

# Añadir la nueva vista para responder formulario
def gform_respond(request, form_id):
    """Vista exclusiva para responder a un formulario sin opciones de edición"""
    gform = get_object_or_404(GForm, id=form_id)
    
    # Verificar que el formulario esté publicado
    if not gform.is_published:
        return HttpResponseForbidden("Este formulario no está disponible para respuestas")
    
    questions = GQuestion.objects.filter(form=gform).order_by('position')
    
    # Crear contexto para las preguntas de tipo escala lineal
    for question in questions:
        if question.question_type == 'linear_scale':
            min_val = question.min_value or 1
            max_val = question.max_value or 5
            question.range_values = range(min_val, max_val + 1)
    
    if request.method == 'POST':
        # Procesar la respuesta al formulario
        
        # Crear una nueva respuesta
        response = GResponse.objects.create(
            form=gform,
            respondent=request.user if request.user.is_authenticated else None,
            respondent_email=request.POST.get('email', None)
        )
        
        # Procesar cada pregunta
        for question in questions:
            field_name = f'question_{question.id}'
            file_field_name = f'file_{question.id}'
            url_field_name = f'url_{question.id}'
            
            if field_name in request.POST or file_field_name in request.FILES or url_field_name in request.POST:
                answer = GAnswer.objects.create(
                    response=response,
                    question=question
                )
                
                if field_name in request.POST:
                    if question.question_type in ['short_text', 'paragraph', 'date', 'time', 'linear_scale']:
                        answer.text_answer = request.POST.get(field_name)
                        answer.save()
                    
                    elif question.question_type in ['multiple_choice', 'dropdown']:
                        option_id = request.POST.get(field_name)
                        if option_id:
                            option = get_object_or_404(GOption, id=option_id)
                            GSelectedOption.objects.create(answer=answer, option=option)
                    
                    elif question.question_type == 'checkbox':
                        # Para checkbox, value puede ser una lista
                        option_ids = request.POST.getlist(field_name)
                        for option_id in option_ids:
                            option = get_object_or_404(GOption, id=option_id)
                            GSelectedOption.objects.create(answer=answer, option=option)
                
                # Procesar archivos adjuntos
                if file_field_name in request.FILES:
                    file = request.FILES[file_field_name]
                    if file.content_type.startswith('image/'):
                        answer.image = file
                    elif file.content_type.startswith('video/'):
                        answer.video = file
                    answer.save()
                
                # Procesar URL
                if url_field_name in request.POST and request.POST.get(url_field_name):
                    answer.file_url = request.POST.get(url_field_name)
                    answer.save()
        
        messages.success(request, "¡Gracias por tu respuesta!")
        return redirect('gform_thank_you', form_id=gform.id)
    
    return render(request, 'forms_google/respond_form.html', {
        'gform': gform,
        'questions': questions
    })

def gform_thank_you(request, form_id):
    """Vista de agradecimiento después de enviar una respuesta"""
    gform = get_object_or_404(GForm, id=form_id)
    return render(request, 'forms_google/thank_you.html', {'gform': gform})

# Añadir esta función para obtener datos en formato JSON para la exportación
@login_required
def gform_responses(request, form_id):
    """Vista para ver las respuestas a un formulario"""
    gform = get_object_or_404(GForm, id=form_id)
    
    # Verificar que el usuario sea el propietario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para ver las respuestas de este formulario")
    
    responses = GResponse.objects.filter(form=gform).order_by('-created_at')
    
    # Si es una solicitud AJAX para exportar a CSV, devolver JSON con todos los datos
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.GET.get('format') == 'json':
        # Obtener todas las preguntas
        questions = GQuestion.objects.filter(form=gform).order_by('position')
        questions_data = []
        
        for question in questions:
            question_data = {
                'id': question.id,
                'text': question.text,
                'question_type': question.question_type,
                'is_required': question.is_required
            }
            questions_data.append(question_data)
        
        # Obtener todas las respuestas con sus detalles
        responses_data = []
        
        for response in responses:
            response_data = {
                'id': response.id,
                'respondent': response.respondent.username if response.respondent else None,
                'respondent_email': response.respondent_email,
                'created_at': response.created_at.strftime('%d/%m/%Y %H:%M'),
                'answers': []
            }
            
            # Obtener respuestas para cada pregunta
            answers = GAnswer.objects.filter(response=response).select_related('question')
            
            for answer in answers:
                answer_data = {
                    'question_id': answer.question.id,
                    'text_answer': answer.text_answer,
                    'image': answer.image.url if answer.image else None,
                    'video': answer.video.url if answer.video else None,
                    'file_url': answer.file_url,
                    'selected_options': []
                }
                
                # Obtener opciones seleccionadas
                selected_options = GSelectedOption.objects.filter(answer=answer).select_related('option')
                
                for selected in selected_options:
                    answer_data['selected_options'].append({
                        'id': selected.option.id,
                        'text': selected.option.text
                    })
                
                response_data['answers'].append(answer_data)
            
            responses_data.append(response_data)
        
        return JsonResponse({
            'form': {
                'id': gform.id,
                'title': gform.title,
                'description': gform.description
            },
            'questions': questions_data,
            'responses': responses_data
        })
    
    return render(request, 'forms_google/view_responses.html', {
        'gform': gform,
        'responses': responses
    })

# Modificar la función gform_response_detail para ajustar la zona horaria
@login_required
def gform_response_detail(request, response_id):
    """Vista para ver el detalle de una respuesta"""
    response = get_object_or_404(GResponse, id=response_id)
    gform = response.form
    
    # Verificar que el usuario sea el propietario del formulario
    if gform.user != request.user:
        return HttpResponseForbidden("No tienes permiso para ver esta respuesta")
    
    # Obtener todas las preguntas y respuestas
    questions = GQuestion.objects.filter(form=gform).order_by('position')
    answers = GAnswer.objects.filter(response=response).select_related('question')
    
    # Crear un diccionario para facilitar el acceso a las respuestas
    answer_dict = {}
    for answer in answers:
        answer_dict[answer.question.id] = answer
    
    # Si es una solicitud AJAX para exportar a CSV, devolver JSON con los datos
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.GET.get('format') == 'json':
        # Preparar datos para exportación
        response_data = {
            'id': response.id,
            'respondent': response.respondent.username if response.respondent else None,
            'respondent_email': response.respondent_email,
            'created_at': response.created_at.strftime('%d/%m/%Y %H:%M'),
            'answers': []
        }
        
        # Obtener respuestas para cada pregunta
        for question in questions:
            answer_data = {
                'question_id': question.id,
                'question_text': question.text,
                'question_type': question.question_type,
                'text_answer': None,
                'image': None,
                'video': None,
                'file_url': None,
                'selected_options': []
            }
            
            if question.id in answer_dict:
                answer = answer_dict[question.id]
                answer_data['text_answer'] = answer.text_answer
                answer_data['image'] = answer.image.url if answer.image else None
                answer_data['video'] = answer.video.url if answer.video else None
                answer_data['file_url'] = answer.file_url
                
                # Obtener opciones seleccionadas
                selected_options = GSelectedOption.objects.filter(answer=answer).select_related('option')
                for selected in selected_options:
                    answer_data['selected_options'].append({
                        'id': selected.option.id,
                        'text': selected.option.text
                    })
            
            response_data['answers'].append(answer_data)
        
        return JsonResponse({
            'form': {
                'id': gform.id,
                'title': gform.title,
                'description': gform.description
            },
            'response': response_data
        })
    
    return render(request, 'forms_google/response_detail.html', {
        'gform': gform,
        'response': response,
        'questions': questions,
        'answer_dict': answer_dict
    })

@login_required
def gform_response_data(request, response_id):
    """Vista para obtener los datos de una respuesta en formato JSON"""
    response = get_object_or_404(GResponse, id=response_id)
    gform = response.form
    
    # Verificar que el usuario sea el propietario del formulario
    if gform.user != request.user:
        return JsonResponse({"error": "No tienes permiso para ver esta respuesta"}, status=403)
    
    # Obtener todas las preguntas y respuestas
    questions = GQuestion.objects.filter(form=gform).order_by('position')
    answers = GAnswer.objects.filter(response=response).select_related('question')
    
    # Crear un diccionario para facilitar el acceso a las respuestas
    answer_dict = {}
    for answer in answers:
        answer_dict[answer.question.id] = answer
    
    # Preparar datos para exportación
    response_data = {
        'id': response.id,
        'respondent': response.respondent.username if response.respondent else None,
        'respondent_email': response.respondent_email,
        'created_at': response.created_at.strftime('%d/%m/%Y %H:%M'),
        'answers': []
    }
    
    # Obtener respuestas para cada pregunta
    for question in questions:
        answer_data = {
            'question_id': question.id,
            'question_text': question.text,
            'question_type': question.question_type,
            'text_answer': None,
            'image': None,
            'video': None,
            'file_url': None,
            'selected_options': []
        }
        
        if question.id in answer_dict:
            answer = answer_dict[question.id]
            answer_data['text_answer'] = answer.text_answer
            answer_data['image'] = answer.image.url if answer.image else None
            answer_data['video'] = answer.video.url if answer.video else None
            answer_data['file_url'] = answer.file_url
            
            # Obtener opciones seleccionadas
            selected_options = GSelectedOption.objects.filter(answer=answer).select_related('option')
            for selected in selected_options:
                answer_data['selected_options'].append({
                    'id': selected.option.id,
                    'text': selected.option.text
                })
        
        response_data['answers'].append(answer_data)
    
    return JsonResponse({
        'form': {
            'id': gform.id,
            'title': gform.title,
            'description': gform.description
        },
        'response': response_data
    })