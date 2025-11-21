from django.db import models
from django.contrib.auth.models import User

class DeviceType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название типа")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Тип устройства"
        verbose_name_plural = "Типы устройств"
    
    def __str__(self):
        return self.name


class Parameter(models.Model):
    
    PARAMETER_TYPES = (
        ('text', 'Текст'),
        ('integer', 'Целое число'),
        ('float', 'Дробное число'),
        ('boolean', 'Да/Нет'),
        ('date', 'Дата'),
        ('datetime', 'Дата и время'),
    )
    
    name = models.CharField(max_length=100, verbose_name="Название параметра")
    key = models.SlugField(max_length=100, unique=True, verbose_name="Ключ параметра")
    parameter_type = models.CharField(
        max_length=20, 
        choices=PARAMETER_TYPES, 
        default='text',
        verbose_name="Тип параметра"
    )
    device_types = models.ManyToManyField(
        DeviceType, 
        related_name='parameters',
        verbose_name="Типы устройств",
        blank=True
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    required = models.BooleanField(default=False, verbose_name="Обязательный")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Параметры"
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_parameter_type_display()})"


class DeviceModel(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название модели")
    device_type = models.ForeignKey(
        DeviceType, 
        on_delete=models.CASCADE,
        related_name='models',
        verbose_name="Тип устройства"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    
    class Meta:
        verbose_name = "Модель устройства"
        verbose_name_plural = "Модели устройств"
        unique_together = ['name', 'device_type']
    
    def __str__(self):
        return f"{self.name} ({self.device_type})"


class Device(models.Model):
    
    STATUS_CHOICES = (
        ('online', 'На сети'),
        ('offline', 'Не на сети')
    )
    
    name = models.CharField(max_length=200, verbose_name="Название устройства")
    device_model = models.ForeignKey(
        DeviceModel,
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name="Модель устройства"
    )
    serial_number = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Серийный номер"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='online',
        verbose_name="Статус"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_devices'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"
    
    def __str__(self):
        return f"{self.name} ({self.device_model})"
    
    @property
    def device_type(self):
        return self.device_model.device_type


class ParameterValue(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='parameter_values'
    )
    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name='values'
    )

    value_text = models.TextField(blank=True, null=True)
    value_int = models.IntegerField(blank=True, null=True)
    value_float = models.FloatField(blank=True, null=True)
    value_bool = models.BooleanField(blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)
    value_datetime = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Значение параметра"
        verbose_name_plural = "Значения параметров"
        unique_together = ['device', 'parameter']
    
    def __str__(self):
        return f"{self.device} - {self.parameter}: {self.value}"
    
    @property
    def value(self):
        if self.parameter.parameter_type == 'text':
            return self.value_text
        elif self.parameter.parameter_type == 'integer':
            return self.value_int
        elif self.parameter.parameter_type == 'float':
            return self.value_float
        elif self.parameter.parameter_type == 'boolean':
            return self.value_bool
        elif self.parameter.parameter_type == 'date':
            return self.value_date
        elif self.parameter.parameter_type == 'datetime':
            return self.value_datetime
        return None
    
    @value.setter
    def value(self, data):
        param_type = self.parameter.parameter_type
        self.value_text = None
        self.value_int = None
        self.value_float = None
        self.value_bool = None
        self.value_date = None
        self.value_datetime = None
        
        if param_type == 'text':
            self.value_text = str(data) if data is not None else None
        elif param_type == 'integer':
            self.value_int = int(data) if data is not None else None
        elif param_type == 'float':
            self.value_float = float(data) if data is not None else None
        elif param_type == 'boolean':
            self.value_bool = bool(data) if data is not None else None
        elif param_type == 'date':
            self.value_date = data
        elif param_type == 'datetime':
            self.value_datetime = data