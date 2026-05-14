from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import RegistroForm, LoginForm, PerfilForm
from .models import Usuario


class EcosmartLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, 'E-mail ou senha inválidos.')
        return super().form_invalid(form)

    def form_valid(self, form):
        user = form.get_user()

        if not user.is_active:
            messages.error(
                self.request,
                'A sua conta está desativada. Entre em contato com o administrador.'
            )
<<<<<<< HEAD
            return HttpResponseRedirect(reverse('accounts:login'))
=======
            return redirect('accounts:login')

>>>>>>> 07f5b55 (Commit das atualizações)
        messages.success(self.request, 'Login realizado com sucesso!')
        return super().form_valid(form)


class EcosmartLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Sessão encerrada.')

        return super().dispatch(request, *args, **kwargs)


class RegistroView(CreateView):
    model = Usuario
    form_class = RegistroForm
    template_name = 'register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Cadastro realizado! Agora faça login.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Corrija os erros abaixo.')
        return super().form_invalid(form)


class PerfilView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = PerfilForm
    template_name = 'perfil.html'
    success_url = reverse_lazy('accounts:perfil')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Corrija os erros do formulário.')
        return super().form_invalid(form)