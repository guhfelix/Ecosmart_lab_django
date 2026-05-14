import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import validate_email

from .models import Usuario


class RegistroForm(UserCreationForm):
    nome = forms.CharField(
        label='Nome completo',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome completo',
            'autocomplete': 'name',
        })
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
        })
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repita a senha',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = Usuario
        fields = ('nome', 'email', 'password1', 'password2')

    def clean_nome(self):
        """
        Valida o nome completo:
        - Mínimo de 3 caracteres e máximo de 100.
        - Deve conter pelo menos duas palavras (nome e sobrenome).
        - Não pode conter números ou caracteres especiais além de hífens e apóstrofos.
        """
        nome = self.cleaned_data.get('nome', '').strip()

        if len(nome) < 3:
            raise forms.ValidationError('O nome deve ter pelo menos 3 caracteres.')

        if len(nome.split()) < 2:
            raise forms.ValidationError('Por favor, informe o nome e o sobrenome.')

        if re.search(r'[0-9@#$%^&*()_+=\[\]{};:"\\|<>/?]', nome):
            raise forms.ValidationError(
                'O nome não pode conter números ou caracteres especiais.'
            )

        # Normaliza para Title Case (ex: "joão silva" → "João Silva")
        return nome.title()

    def clean_email(self):
        """
        Valida o e-mail:
        - Formato válido (delegado ao validator do Django).
        - Unicidade: verifica se já existe um utilizador com este e-mail.
        """
        email = self.cleaned_data.get('email', '').strip().lower()

        try:
            validate_email(email)
        except forms.ValidationError:
            raise forms.ValidationError('Informe um endereço de e-mail válido.')

        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Este e-mail já está cadastrado. '
                'Tente fazer login ou use outro endereço.'
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.nome = self.cleaned_data['nome']
        user.email = self.cleaned_data['email']
        # Gera username único a partir do e-mail para compatibilidade com AbstractUser
        base_username = self.cleaned_data['email'].split('@')[0]
        username = base_username
        counter = 1
        while Usuario.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1
        user.username = username
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'autofocus': True,
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha',
            'autocomplete': 'current-password',
        })
    )

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = (
            'nome',
            'telefone',
            'receber_notificacoes',
            'raio_busca_km',
        )

        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome completo',
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(65) 99999-9999',
            }),
            'receber_notificacoes': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'raio_busca_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '50',
            }),
        }

        labels = {
            'nome': 'Nome completo',
            'telefone': 'Telefone',
            'receber_notificacoes': 'Desejo receber notificações',
            'raio_busca_km': 'Raio de busca por pontos de coleta',
        }

    def clean_nome(self):
        nome = self.cleaned_data.get('nome', '').strip()

        if len(nome) < 3:
            raise forms.ValidationError('O nome deve ter pelo menos 3 caracteres.')

        if len(nome.split()) < 2:
            raise forms.ValidationError('Informe nome e sobrenome.')

        return nome.title()

    def clean_raio_busca_km(self):
        raio = self.cleaned_data.get('raio_busca_km')

        if raio is None:
            return 5

        if raio < 1:
            raise forms.ValidationError('O raio mínimo é 1 km.')

        if raio > 50:
            raise forms.ValidationError('O raio máximo permitido é 50 km.')

        return raio