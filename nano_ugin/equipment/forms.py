from django import forms
from .models import Parameter, ParameterValue,DeviceType

class ParameterForm(forms.ModelForm):
    class Meta:
        model = Parameter
        fields = ['name', 'key', 'parameter_type', 'device_types', 'description', 'required', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'parameter_type': forms.Select(attrs={'class': 'form-control'}),
            'device_types': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'key': 'Уникальный идентификатор параметра (только латинские буквы, цифры и подчёркивания)',
            'order': 'Порядок отображения параметров (меньше = выше)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['required'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['device_types'].queryset = DeviceType.objects.all()
        self.fields['device_types'].widget.attrs.update({'size': '6'})
        self.fields['device_types'].required = False 

class ParameterValueForm(forms.ModelForm):
    class Meta:
        model = ParameterValue
        fields = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.parameter:
            param = self.instance.parameter
            field_name = f'param_{param.id}'
            
            if param.parameter_type == 'text':
                self.fields[field_name] = forms.CharField(
                    label=param.name,
                    required=param.required,
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    initial=self.instance.value_text,
                    help_text=param.description
                )
            elif param.parameter_type == 'integer':
                self.fields[field_name] = forms.IntegerField(
                    label=param.name,
                    required=param.required,
                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                    initial=self.instance.value_int,
                    help_text=param.description
                )
            elif param.parameter_type == 'float':
                self.fields[field_name] = forms.FloatField(
                    label=param.name,
                    required=param.required,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
                    initial=self.instance.value_float,
                    help_text=param.description
                )
            elif param.parameter_type == 'boolean':
                self.fields[field_name] = forms.BooleanField(
                    label=param.name,
                    required=False,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                    initial=self.instance.value_bool,
                    help_text=param.description
                )