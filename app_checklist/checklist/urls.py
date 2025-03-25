from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    
    # Google Forms
    path('forms/', views.gform_list, name='gform_list'),
    path('forms/create/', views.gform_create, name='gform_create'),
    path('forms/<int:form_id>/', views.gform_view, name='gform_view'),
    path('forms/<int:form_id>/edit/', views.gform_edit, name='gform_edit'),
    path('forms/<int:form_id>/delete/', views.gform_delete, name='gform_delete'),
    path('forms/<int:form_id>/toggle-publish/', views.gform_toggle_publish, name='gform_toggle_publish'),
    path('forms/<int:form_id>/responses/', views.gform_responses, name='gform_responses'),
    path('forms/<int:form_id>/thank-you/', views.gform_thank_you, name='gform_thank_you'),
    path('forms/<int:form_id>/respond/', views.gform_respond, name='gform_respond'),
    path('forms/<int:form_id>/add-question/', views.gform_add_question, name='gform_add_question'),
    path('forms/<int:form_id>/update-question-order/', views.gform_update_question_order, name='gform_update_question_order'),
    path('forms/question/<int:question_id>/edit/', views.gform_edit_question, name='gform_edit_question'),
    path('forms/question/<int:question_id>/delete/', views.gform_delete_question, name='gform_delete_question'),
    path('forms/question/<int:question_id>/add-option/', views.gform_add_option, name='gform_add_option'),
    path('forms/question/<int:question_id>/update-option-order/', views.gform_update_option_order, name='gform_update_option_order'),
    path('forms/option/<int:option_id>/edit/', views.gform_edit_option, name='gform_edit_option'),
    path('forms/option/<int:option_id>/delete/', views.gform_delete_option, name='gform_delete_option'),
    path('forms/response/<int:response_id>/', views.gform_response_detail, name='gform_response_detail'),
    path('forms/response/<int:response_id>/data/', views.gform_response_data, name='gform_response_data'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)