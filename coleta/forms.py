from django import forms
from .models import Descarte, PontoColeta


class DescarteForm(forms.ModelForm):
    class Meta:
        model = Descarte
        fields = ('ponto', 'tipo_residuo', 'peso_kg')
        widgets = {
            'ponto': forms.Select(attrs={'class': 'form-select'}),
            'tipo_residuo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Plastico, Vidro, Metal...'
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.1',
                'placeholder': 'Peso em kg'
            }),
        }
        labels = {
            'ponto': 'Ponto de Coleta',
            'tipo_residuo': 'Tipo de Residuo',
            'peso_kg': 'Peso (kg)',
        }
