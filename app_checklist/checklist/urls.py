from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Todo Lists
    path('lists/', views.todo_lists, name='todo_lists'),
    path('lists/create/', views.create_todo_list, name='create_todo_list'),
    path('lists/<int:list_id>/', views.view_todo_list, name='view_todo_list'),
    path('lists/<int:list_id>/delete/', views.delete_todo_list, name='delete_todo_list'),
    
    # Tasks
    path('lists/<int:list_id>/add-task/', views.add_task, name='add_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    
    # API
    path('api/tasks/<int:task_id>/status/', views.update_task_status, name='update_task_status'),
    path('api/lists/<int:list_id>/order/', views.update_tasks_order, name='update_tasks_order'),
    
    # Dynamic Forms
    path('forms/', views.dynamic_forms, name='dynamic_forms'),
    path('forms/create/', views.create_form, name='create_form'),
    path('forms/<int:form_id>/', views.view_form, name='view_form'),
    path('forms/<int:form_id>/delete/', views.delete_form, name='delete_form'),
    path('forms/<int:form_id>/preview/', views.preview_form, name='preview_form'),
    path('forms/<int:form_id>/submit/', views.submit_form_response, name='submit_form_response'),
    path('forms/<int:form_id>/responses/', views.view_form_responses, name='view_form_responses'),
    path('responses/<int:response_id>/', views.view_response_detail, name='view_response_detail'),
    
    # Questions
    path('forms/<int:form_id>/add-question/', views.add_question, name='add_question'),
    path('questions/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('questions/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('api/questions/<int:question_id>/', views.get_question_data, name='get_question_data'),
    path('api/options/<int:option_id>/', views.get_option_data, name='get_option_data'),
    
    # Options
    path('questions/<int:question_id>/add-option/', views.add_option, name='add_option'),
    path('options/<int:option_id>/edit/', views.edit_option, name='edit_option'),
    path('options/<int:option_id>/delete/', views.delete_option, name='delete_option'),
    
    # API for Dynamic Forms
    path('api/forms/<int:form_id>/questions/order/', views.update_questions_order, name='update_questions_order'),
    path('api/questions/<int:question_id>/options/order/', views.update_options_order, name='update_options_order'),
]