from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Device, DeviceType, DeviceModel, ParameterValue
from django.db import models

def device_type_list(request):
    device_types = DeviceType.objects.all()
    data = [
        {
            'id': dt.id,
            'name': dt.name,
            'description': dt.description,
            'created_at': dt.created_at,
        }
        for dt in device_types
    ]
    return JsonResponse({'device_types': data})

def device_type_detail(request, type_id):
    device_type = get_object_or_404(DeviceType, id=type_id)
    parameters = device_type.parameters.all()
    
    data = {
        'id': device_type.id,
        'name': device_type.name,
        'description': device_type.description,
        'parameters': [
            {
                'id': p.id,
                'name': p.name,
                'key': p.key,
                'type': p.parameter_type,
                'required': p.required,
            }
            for p in parameters
        ]
    }
    return JsonResponse(data)

def device_model_list(request):
    device_models = DeviceModel.objects.select_related('device_type').all()
    data = [
        {
            'id': dm.id,
            'name': dm.name,
            'device_type': {
                'id': dm.device_type.id,
                'name': dm.device_type.name,
            },
            'description': dm.description,
        }
        for dm in device_models
    ]
    return JsonResponse({'device_models': data})

def device_model_detail(request, model_id):
    device_model = get_object_or_404(
        DeviceModel.objects.select_related('device_type'),
        id=model_id
    )
    
    data = {
        'id': device_model.id,
        'name': device_model.name,
        'device_type': {
            'id': device_model.device_type.id,
            'name': device_model.device_type.name,
        },
        'description': device_model.description,
    }
    return JsonResponse(data)

def device_list(request):
    devices = Device.objects.select_related(
        'device_model', 
        'device_model__device_type'
    ).all()
    
    device_type = request.GET.get('type')
    if device_type:
        devices = devices.filter(device_model__device_type_id=device_type)

    status = request.GET.get('status')
    if status:
        devices = devices.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        devices = devices.filter(
            models.Q(name__icontains=search) |
            models.Q(serial_number__icontains=search) |
            models.Q(device_model__name__icontains=search)
        )
    
    data = [
        {
            'id': d.id,
            'name': d.name,
            'serial_number': d.serial_number,
            'status': d.status,
            'device_model': {
                'id': d.device_model.id,
                'name': d.device_model.name,
                'device_type': d.device_model.device_type.name,
            },
            'created_at': d.created_at,
        }
        for d in devices
    ]
    return JsonResponse({'devices': data})

def device_detail(request, device_id):
    device = get_object_or_404(
        Device.objects.select_related('device_model', 'device_model__device_type')
        .prefetch_related('parameter_values__parameter'),
        id=device_id
    )
    
    parameter_values = []
    for pv in device.parameter_values.all():
        parameter_values.append({
            'parameter_id': pv.parameter.id,
            'name': pv.parameter.name,
            'key': pv.parameter.key,
            'type': pv.parameter.parameter_type,
            'value': pv.value,
        })
    
    data = {
        'id': device.id,
        'name': device.name,
        'serial_number': device.serial_number,
        'status': device.status,
        'device_model': {
            'id': device.device_model.id,
            'name': device.device_model.name,
        },
        'device_type': {
            'id': device.device_type.id,
            'name': device.device_type.name,
        },
        'parameters': parameter_values,
        'created_at': device.created_at,
        'updated_at': device.updated_at,
    }
    return JsonResponse(data)