from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Device, DeviceType, Parameter, ParameterValue

def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
def device_list(request):
    return render(request, 'equipment/device_list.html', {
        'user': request.user
    })

@login_required
def device_detail(request, device_id):
    return render(request, 'equipment/device_detail.html', {
        'device_id': device_id,
        'user': request.user
    })


@login_required
@user_passes_test(is_admin)
def device_edit_parameters(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    
    device_type = device.device_type
    parameters = device_type.parameters.all()
    
    for parameter in parameters:
        ParameterValue.objects.get_or_create(
            device=device,
            parameter=parameter
        )
    
    parameter_values = ParameterValue.objects.filter(device=device).select_related('parameter')
    
    if request.method == 'POST':
        for pv in parameter_values:
            field_name = f'param_{pv.parameter.id}'
            if field_name in request.POST:
                value = request.POST[field_name]
                
                if pv.parameter.parameter_type == 'text':
                    pv.value_text = value
                elif pv.parameter.parameter_type == 'integer':
                    pv.value_int = int(value) if value else None
                elif pv.parameter.parameter_type == 'float':
                    pv.value_float = float(value) if value else None
                elif pv.parameter.parameter_type == 'boolean':
                    pv.value_bool = (value == 'on')
                
                pv.save()
        
        messages.success(request, f'Параметры устройства "{device.name}" обновлены!')
        return redirect('equipment:device_detail', device_id=device_id)
    
    return render(request, 'equipment/device_edit_parameters.html', {
        'device': device,
        'parameter_values': parameter_values
    })

@login_required
@user_passes_test(is_admin)
def device_create_parameters(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    
    ParameterValue.objects.filter(device=device).delete()
    
    device_type = device.device_type
    parameters = device_type.parameters.all()
    
    created_count = 0
    for parameter in parameters:
        ParameterValue.objects.create(
            device=device,
            parameter=parameter
        )
        created_count += 1
    
    messages.success(request, f'Создано {created_count} параметров для устройства "{device.name}"')
    return redirect('equipment:device_edit_parameters', device_id=device_id)



@login_required
@user_passes_test(is_admin)
def parameter_list(request):
    parameters = Parameter.objects.all().prefetch_related('device_types')
    return render(request, 'equipment/parameter_list.html', {
        'parameters': parameters
    })

@login_required
@user_passes_test(is_admin)
def parameter_create(request):
    from .forms import ParameterForm
    
    if request.method == 'POST':
        form = ParameterForm(request.POST)
        if form.is_valid():
            parameter = form.save()
            messages.success(request, f'Параметр "{parameter.name}" создан!')
            return redirect('equipment:parameter_list')
    else:
        form = ParameterForm()
    
    return render(request, 'equipment/parameter_form.html', {
        'form': form,
        'title': 'Создание параметра'
    })

@login_required
@user_passes_test(is_admin)
def parameter_edit(request, parameter_id):
    from .forms import ParameterForm
    parameter = get_object_or_404(Parameter, id=parameter_id)
    
    if request.method == 'POST':
        form = ParameterForm(request.POST, instance=parameter)
        if form.is_valid():
            parameter = form.save()
            messages.success(request, f'Параметр "{parameter.name}" обновлён!')
            return redirect('equipment:parameter_list')
    else:
        form = ParameterForm(instance=parameter)
    
    return render(request, 'equipment/parameter_form.html', {
        'form': form,
        'title': f'Редактирование: {parameter.name}',
        'parameter': parameter
    })

@login_required
@user_passes_test(is_admin)
def parameter_delete(request, parameter_id):
    parameter = get_object_or_404(Parameter, id=parameter_id)
    
    if request.method == 'POST':
        name = parameter.name
        parameter.delete()
        messages.success(request, f'Параметр "{name}" удалён!')
        return redirect('equipment:parameter_list')
    
    return render(request, 'equipment/parameter_confirm_delete.html', {
        'parameter': parameter
    })


@login_required
@user_passes_test(is_admin)
def device_type_manage_parameters(request, device_type_id):
    device_type = get_object_or_404(DeviceType, id=device_type_id)
    all_parameters = Parameter.objects.all()
    current_parameters = device_type.parameters.all()
    
    if request.method == 'POST':
        selected_parameter_ids = request.POST.getlist('parameters')
        device_type.parameters.set(selected_parameter_ids)
        
        messages.success(request, f'Параметры для типа "{device_type.name}" обновлены!')
        return redirect('equipment:device_type_manage_parameters', device_type_id=device_type_id)
    
    return render(request, 'equipment/device_type_manage_parameters.html', {
        'device_type': device_type,
        'all_parameters': all_parameters,
        'current_parameters': current_parameters,
    })

@login_required
@user_passes_test(is_admin) 
def device_type_list(request):
    device_types = DeviceType.objects.all().prefetch_related('parameters')
    return render(request, 'equipment/device_type_list.html', {
        'device_types': device_types
    })


@login_required
@user_passes_test(is_admin)
def device_delete(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    ParameterValue.objects.filter(device=device).delete()
    device.delete()
    return redirect('equipment:device_list')