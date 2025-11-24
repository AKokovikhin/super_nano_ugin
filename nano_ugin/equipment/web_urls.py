from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    path('', views.device_list, name='device_list'),
    path('equipment/device/<int:device_id>/', views.device_detail, name='device_detail'),
    
    path('equipment/device/<int:device_id>/edit-parameters/', views.device_edit_parameters, name='device_edit_parameters'),
    path('equipment/device/<int:device_id>/create-parameters/', views.device_create_parameters, name='device_create_parameters'),
    path('equipment/device/<int:device_id>/delete/', views.device_delete, name='device_delete'),
    
    path('parameters/', views.parameter_list, name='parameter_list'),
    path('parameters/create/', views.parameter_create, name='parameter_create'),
    path('parameters/<int:parameter_id>/edit/', views.parameter_edit, name='parameter_edit'),
    path('parameters/<int:parameter_id>/delete/', views.parameter_delete, name='parameter_delete'),

    path('device-types/', views.device_type_list, name='device_type_list'),
    path('device-types/<int:device_type_id>/manage-parameters/', views.device_type_manage_parameters, name='device_type_manage_parameters'),
]