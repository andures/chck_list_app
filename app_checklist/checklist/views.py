from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib import messages
from .forms import UserRegistrationForm, TodoListForm, TaskForm, DynamicFormForm, QuestionForm, QuestionOptionForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .models import TodoList, Task, DynamicForm, Question, QuestionOption, FormResponse, Answer, SelectedOption, AnswerFile
import json
from datetime import date, datetime

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    todo_lists = TodoList.objects.filter(user=request.user)
    recent_todo_lists = TodoList.objects.filter(user=request.user).order_by('-created_at')[:5]
    dynamic_forms = DynamicForm.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'dashboard.html', {
        'todo_lists': todo_lists, 
        'recent_todo_lists': recent_todo_lists,
        'dynamic_forms': dynamic_forms
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

# Vistas para formularios dinámicos
@login_required
def dynamic_forms(request):
    """Muestra todos los formularios dinámicos del usuario"""
    forms = DynamicForm.objects.filter(user=request.user)
    return render(request, 'dynamic_forms/forms_list.html', {'forms': forms})

@login_required
def view_form(request, form_id):
    """Vista unificada para ver, editar y gestionar un formulario dinámico"""
    dynamic_form = get_object_or_404(DynamicForm, id=form_id)
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return HttpResponseForbidden("No tienes permiso para ver este formulario")
    
    # Obtener todas las preguntas del formulario
    questions = Question.objects.filter(form=dynamic_form).order_by('position')
    
    # Formulario para editar el formulario
    if request.method == 'POST' and 'form_details' in request.POST:
        form = DynamicFormForm(request.POST, instance=dynamic_form)
        if form.is_valid():
            form.save()
            messages.success(request, "Formulario actualizado correctamente")
            return redirect('view_form', form_id=dynamic_form.id)
    else:
        form = DynamicFormForm(instance=dynamic_form)
    
    # Formulario para añadir una nueva pregunta
    question_form = QuestionForm()
    
    return render(request, 'dynamic_forms/view_form.html', {
        'form': form,
        'dynamic_form': dynamic_form,
        'questions': questions,
        'question_form': question_form
    })

@login_required
def create_form(request):
    """Crea un nuevo formulario dinámico"""
    if request.method == 'POST':
        form = DynamicFormForm(request.POST)
        if form.is_valid():
            dynamic_form = form.save(commit=False)
            dynamic_form.user = request.user
            dynamic_form.save()
            return redirect('view_form', form_id=dynamic_form.id)
    else:
        form = DynamicFormForm()
    
    return render(request, 'dynamic_forms/create_form.html', {'form': form})

@login_required
def delete_form(request, form_id):
    """Elimina un formulario dinámico"""
    dynamic_form = get_object_or_404(DynamicForm, id=form_id, user=request.user)
    
    if request.method == 'POST':
        dynamic_form.delete()
        return redirect('dynamic_forms')
    
    return render(request, 'dynamic_forms/delete_form.html', {'dynamic_form': dynamic_form})

@login_required
@require_POST
def add_question(request, form_id):
    """Añade una pregunta a un formulario dinámico"""
    dynamic_form = get_object_or_404(DynamicForm, id=form_id)
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar este formulario")
    
    form = QuestionForm(request.POST)
    if form.is_valid():
        question = form.save(commit=False)
        question.form = dynamic_form
        
        # Obtener la posición máxima actual
        max_position = Question.objects.filter(form=dynamic_form).order_by('-position').first()
        
        if max_position:
            question.position = max_position.position + 1
        else:
            question.position = 0
        
        question.save()
        
        # Si es una solicitud AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': question.id,
                'text': question.text,
                'question_type': question.question_type,
                'is_required': question.is_required,
                'position': question.position,
                'help_text': question.help_text
            })
        
        return redirect('view_form', form_id=dynamic_form.id)
    
    # Si hay errores en el formulario y es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'errors': form.errors}, status=400)
    
    # Si hay errores en el formulario y no es AJAX, volver a la vista del formulario
    messages.error(request, "Error al añadir la pregunta. Por favor, verifica los datos.")
    return redirect('view_form', form_id=dynamic_form.id)

@login_required
@require_POST
def edit_question(request, question_id):
    """Edita una pregunta existente"""
    question = get_object_or_404(Question, id=question_id)
    dynamic_form = question.form
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar esta pregunta")
    
    form = QuestionForm(request.POST, instance=question)
    if form.is_valid():
        form.save()
        
        # Si es una solicitud AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': question.id,
                'text': question.text,
                'question_type': question.question_type,
                'is_required': question.is_required,
                'position': question.position,
                'help_text': question.help_text
            })
        
        return redirect('view_form', form_id=dynamic_form.id)
    
    # Si hay errores en el formulario y es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'errors': form.errors}, status=400)
    
    # Si hay errores en el formulario y no es AJAX, volver a la vista del formulario
    messages.error(request, "Error al editar la pregunta. Por favor, verifica los datos.")
    return redirect('view_form', form_id=dynamic_form.id)

@login_required
@require_POST
def delete_question(request, question_id):
    """Elimina una pregunta"""
    question = get_object_or_404(Question, id=question_id)
    dynamic_form = question.form
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar esta pregunta")
    
    question.delete()
    
    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('view_form', form_id=dynamic_form.id)

@login_required
@require_POST
def add_option(request, question_id):
    """Añade una opción a una pregunta de selección"""
    question = get_object_or_404(Question, id=question_id)
    dynamic_form = question.form
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar esta pregunta")
    
    # Verificar que sea una pregunta de selección
    if question.question_type not in ['multiple_choice', 'checkbox', 'dropdown', 'multiple_choice_grid', 'checkbox_grid']:
        return HttpResponseForbidden("Esta pregunta no admite opciones")
    
    form = QuestionOptionForm(request.POST)
    if form.is_valid():
        option = form.save(commit=False)
        option.question = question
        
        # Obtener la posición máxima actual
        max_position = QuestionOption.objects.filter(question=question).order_by('-position').first()
        
        if max_position:
            option.position = max_position.position + 1
        else:
            option.position = 0
        
        option.save()
        
        # Si es una solicitud AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': option.id,
                'text': option.text,
                'position': option.position
            })
        
        return redirect('view_form', form_id=dynamic_form.id)
    
    # Si hay errores en el formulario y es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'errors': form.errors}, status=400)
    
    # Si hay errores en el formulario y no es AJAX, volver a la vista del formulario
    messages.error(request, "Error al añadir la opción. Por favor, verifica los datos.")
    return redirect('view_form', form_id=dynamic_form.id)

@login_required
@require_POST
def edit_option(request, option_id):
    """Edita una opción existente"""
    option = get_object_or_404(QuestionOption, id=option_id)
    question = option.question
    dynamic_form = question.form
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return HttpResponseForbidden("No tienes permiso para modificar esta opción")
    
    form = QuestionOptionForm(request.POST, instance=option)
    if form.is_valid():
        form.save()
        
        # Si es una solicitud AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': option.id,
                'text': option.text,
                'position': option.position
            })
        
        return redirect('view_form', form_id=dynamic_form.id)
    
    # Si hay errores en el formulario y es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'errors': form.errors}, status=400)
    
    # Si hay errores en el formulario y no es AJAX, volver a la vista del formulario
    messages.error(request, "Error al editar la opción. Por favor, verifica los datos.")
    return redirect('view_form', form_id=dynamic_form.id)

@login_required
@require_POST
def delete_option(request, option_id):
    """Elimina una opción"""
    option = get_object_or_404(QuestionOption, id=option_id)
    question = option.question
    dynamic_form = question.form
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar esta opción")
    
    option.delete()
    
    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('view_form', form_id=dynamic_form.id)

@login_required
@require_POST
def update_questions_order(request, form_id):
    """API para actualizar el orden de las preguntas"""
    dynamic_form = get_object_or_404(DynamicForm, id=form_id)
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para modificar este formulario'}, status=403)
    
    try:
        data = json.loads(request.body)
        question_ids = data.get('questions', [])
        
        with transaction.atomic():
            for i, question_id in enumerate(question_ids):
                Question.objects.filter(id=question_id, form=dynamic_form).update(position=i)
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
def update_options_order(request, question_id):
    """API para actualizar el orden de las opciones"""
    question = get_object_or_404(Question, id=question_id)
    dynamic_form = question.form
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para modificar esta pregunta'}, status=403)
    
    try:
        data = json.loads(request.body)
        option_ids = data.get('options', [])
        
        with transaction.atomic():
            for i, option_id in enumerate(option_ids):
                QuestionOption.objects.filter(id=option_id, question=question).update(position=i)
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def preview_form(request, form_id):
    """Vista previa del formulario para responder"""
    dynamic_form = get_object_or_404(DynamicForm, id=form_id)
    
    # Verificar que el usuario sea el propietario o que el formulario esté publicado
    if dynamic_form.user != request.user and not dynamic_form.is_published:
        return HttpResponseForbidden("No tienes permiso para ver este formulario")
    
    # Obtener todas las preguntas del formulario
    questions = Question.objects.filter(form=dynamic_form).order_by('position')
    
    return render(request, 'dynamic_forms/preview_form.html', {
        'dynamic_form': dynamic_form,
        'questions': questions
    })

@login_required
@require_POST
def submit_form_response(request, form_id):
    """Procesa la respuesta a un formulario"""
    dynamic_form = get_object_or_404(DynamicForm, id=form_id)
    
    # Verificar que el formulario esté publicado
    if not dynamic_form.is_published:
        return HttpResponseForbidden("Este formulario no está disponible para respuestas")
    
    # Crear una nueva respuesta
    form_response = FormResponse.objects.create(
        form=dynamic_form,
        respondent=request.user
    )
    
    # Procesar cada pregunta
    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = key.split('_')[1]
            question = get_object_or_404(Question, id=question_id)
            
            # Crear respuesta
            answer = Answer.objects.create(
                response=form_response,
                question=question
            )
            
            # Procesar según el tipo de pregunta
            if question.question_type in ['short_text', 'paragraph', 'date', 'time', 'datetime', 'linear_scale']:
                answer.text_answer = value
                answer.save()
            elif question.question_type in ['multiple_choice', 'dropdown']:
                option = get_object_or_404(QuestionOption, id=value)
                SelectedOption.objects.create(answer=answer, option=option)
            elif question.question_type == 'checkbox':
                # Para checkbox, value puede ser una lista
                option_ids = request.POST.getlist(key)
                for option_id in option_ids:
                    option = get_object_or_404(QuestionOption, id=option_id)
                    SelectedOption.objects.create(answer=answer, option=option)
    
    # Procesar archivos
    for key, file in request.FILES.items():
        if key.startswith('question_'):
            question_id = key.split('_')[1]
            question = get_object_or_404(Question, id=question_id)
            
            if question.question_type == 'file_upload':
                # Buscar o crear la respuesta
                answer, created = Answer.objects.get_or_create(
                    response=form_response,
                    question=question
                )
                
                # Guardar el archivo
                answer_file = AnswerFile.objects.create(
                    answer=answer,
                    file=file,
                    file_name=file.name,
                    file_type=file.content_type
                )
    
    messages.success(request, "Tu respuesta ha sido enviada correctamente")
    return redirect('preview_form', form_id=dynamic_form.id)

@login_required
def view_form_responses(request, form_id):
    """Ver las respuestas a un formulario"""
    dynamic_form = get_object_or_404(DynamicForm, id=form_id)
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return HttpResponseForbidden("No tienes permiso para ver las respuestas de este formulario")
    
    # Obtener todas las respuestas
    responses = FormResponse.objects.filter(form=dynamic_form).order_by('-created_at')
    
    return render(request, 'dynamic_forms/view_responses.html', {
        'dynamic_form': dynamic_form,
        'responses': responses
    })

# Modificar la función view_response_detail para manejar el caso sin filtros personalizados
@login_required
def view_response_detail(request, response_id):
    """Ver el detalle de una respuesta"""
    response = get_object_or_404(FormResponse, id=response_id)
    dynamic_form = response.form
    
    # Verificar que el usuario sea el propietario del formulario
    if dynamic_form.user != request.user:
        return HttpResponseForbidden("No tienes permiso para ver esta respuesta")
    
    # Obtener todas las preguntas y respuestas
    questions = Question.objects.filter(form=dynamic_form).order_by('position')
    answers = Answer.objects.filter(response=response)
    
    # Crear un diccionario para facilitar el acceso a las respuestas
    answer_dict = {}
    for answer in answers:
        answer_dict[answer.question.id] = answer
    
    # Usar la plantilla simple que no requiere templatetags personalizados
    return render(request, 'dynamic_forms/response_detail_simple.html', {
        'dynamic_form': dynamic_form,
        'response': response,
        'questions': questions,
        'answers': answers,
        'answer_dict': answer_dict
    })

@login_required
def get_question_data(request, question_id):
    """API para obtener datos de una pregunta"""
    question = get_object_or_404(Question, id=question_id)
    dynamic_form = question.form
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para ver esta pregunta'}, status=403)
    
    # Obtener opciones si es una pregunta de selección
    options = []
    if question.question_type in ['multiple_choice', 'checkbox', 'dropdown', 'multiple_choice_grid', 'checkbox_grid']:
        options = list(question.options.order_by('position').values('id', 'text', 'position'))
    
    # Construir respuesta
    response_data = {
        'id': question.id,
        'text': question.text,
        'question_type': question.question_type,
        'is_required': question.is_required,
        'help_text': question.help_text or '',
        'position': question.position,
        'options': options
    }
    
    # Añadir campos específicos según el tipo de pregunta
    if question.question_type == 'linear_scale':
        response_data.update({
            'min_value': question.min_value,
            'max_value': question.max_value,
            'min_label': question.min_label,
            'max_label': question.max_label
        })
    elif question.question_type in ['multiple_choice_grid', 'checkbox_grid']:
        response_data.update({
            'rows_text': question.rows_text,
            'columns_text': question.columns_text
        })
    
    return JsonResponse(response_data)

@login_required
def get_option_data(request, option_id):
    """API para obtener datos de una opción"""
    option = get_object_or_404(QuestionOption, id=option_id)
    question = option.question
    dynamic_form = question.form
    
    # Verificar que el usuario sea el propietario
    if dynamic_form.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para ver esta opción'}, status=403)
    
    # Construir respuesta
    response_data = {
        'id': option.id,
        'text': option.text,
        'position': option.position
    }
    
    return JsonResponse(response_data)