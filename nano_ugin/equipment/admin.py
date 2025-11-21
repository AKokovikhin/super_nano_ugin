from django.contrib import admin
from .models import DeviceType, Parameter, DeviceModel, Device, ParameterValue

@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'parameter_type', 'required', 'order']
    list_filter = ['parameter_type', 'required']
    filter_horizontal = ['device_types']

@admin.register(DeviceModel)
class DeviceModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_type', 'description']
    list_filter = ['device_type']
    search_fields = ['name']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_model', 'serial_number', 'status', 'created_at']
    list_filter = ['status', 'device_model__device_type']
    search_fields = ['name', 'serial_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ParameterValue)
class ParameterValueAdmin(admin.ModelAdmin):
    list_display = ['device', 'parameter', 'get_value']
    list_filter = ['parameter__device_types', 'parameter']
    search_fields = ['device__name', 'parameter__name']
    
    def get_value(self, obj):
        return obj.value
    get_value.short_description = 'Значение'