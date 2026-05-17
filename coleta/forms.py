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
                'placeholder': 'Ex: Plástico, Vidro, Metal...',
                'list': 'tipos-residuos',  # Liga ao datalist no template
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Peso em kg',
            }),
        }
        labels = {
            'ponto': 'Ponto de Coleta',
            'tipo_residuo': 'Tipo de Resíduo',
            'peso_kg': 'Peso (kg)',
        }


    def clean_peso_kg(self):
        """
        Validação de backend para o campo peso_kg.
        Garante que o peso é positivo e dentro de um limite razoável,
        independentemente do que o cliente enviar (contornando validação HTML).
        """
        peso = self.cleaned_data.get('peso_kg')

        if peso is None:
            raise forms.ValidationError('O peso é obrigatório.')

        if peso <= 0:
            raise forms.ValidationError('O peso deve ser maior que zero.')

        if peso < 0.01:
            raise forms.ValidationError('O peso mínimo aceito é 0,01 kg (10 gramas).')

        if peso > 5000:
            raise forms.ValidationError(
                'Para descartes acima de 5.000 kg (5 toneladas), '
                'entre em contato com a gestão municipal.'
            )

        return round(peso, 2)

    def clean_tipo_residuo(self):
        """
        Validação de backend para o campo tipo_residuo.
        Normaliza o texto (capitaliza e remove espaços extras) e
        garante que o campo não está vazio ou com apenas espaços.
        """
        tipo = self.cleaned_data.get('tipo_residuo', '').strip()

        if not tipo:
            raise forms.ValidationError('O tipo de resíduo é obrigatório.')

        if len(tipo) < 3:
            raise forms.ValidationError(
                'O tipo de resíduo deve ter pelo menos 3 caracteres.'
            )

        if len(tipo) > 50:
            raise forms.ValidationError(
                'O tipo de resíduo não pode ter mais de 50 caracteres.'
            )

        # Normaliza para Title Case (ex: "plástico" → "Plástico")
        return tipo.title()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ponto'].queryset = PontoColeta.objects.filter(ativo=True).order_by('nome')

    def clean_ponto(self):
        """
        Validação de backend para o campo ponto.
        Garante que o ponto de coleta selecionado existe e está ativo.
        """
        ponto = self.cleaned_data.get('ponto')

        if not ponto:
            raise forms.ValidationError('Selecione um ponto de coleta válido.')

        if not PontoColeta.objects.filter(pk=ponto.pk, ativo=True).exists():
            raise forms.ValidationError(
                'O ponto de coleta selecionado não existe ou está inativo.'
            )

        return ponto
