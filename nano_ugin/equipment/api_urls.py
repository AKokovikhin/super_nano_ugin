from django.urls import path
from . import api_views

app_name = 'equipment_api'

urlpatterns = [
    path('device_types/', api_views.device_type_list, name='device_type_list'),
    path('device_types/<int:type_id>/', api_views.device_type_detail, name='device_type_detail'),
    path('device_models/', api_views.device_model_list, name='device_model_list'),
    path('device_models/<int:model_id>/', api_views.device_model_detail, name='device_model_detail'),
    path('devices/', api_views.device_list, name='device_list'),
    path('devices/<int:device_id>/', api_views.device_detail, name='device_detail'),
]