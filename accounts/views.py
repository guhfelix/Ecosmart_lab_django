from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistroForm, LoginForm
from .models import Usuario


class EcosmartLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, 'E-mail ou senha invalidos.')
        return super().form_invalid(form)

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            messages.error(
                self.request,
                'A sua conta esta desativada. Entre em contato com o administrador.'
            )
            return redirect('accounts:login')
        messages.success(self.request, 'Login realizado com sucesso!')
        return super().form_valid(form)


class EcosmartLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Sessao encerrada.')
        return super().dispatch(request, *args, **kwargs)


class RegistroView(CreateView):
    model = Usuario
    form_class = RegistroForm
    template_name = 'register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Cadastro realizado! Agora faca login.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Corrija os erros abaixo.')
        return super().form_invalid(form)
