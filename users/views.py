from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.core.signing import BadSignature

from .models import AdvUser
from .forms import RegisterUserForm, UserUpdateForm
from .utilites import signer


class UserProfile(LoginRequiredMixin, TemplateView):
    """Инфо о пользователе"""
    template_name = 'users/profile_user.html'


class UserLogin(LoginView):
    """Вход"""
    template_name = 'users/login.html'


class UserLogout(LoginRequiredMixin, LogoutView):
    """Выход"""
    template_name = 'users/logout.html'


class UserRegister(CreateView):
    """Регистрация"""
    model = AdvUser
    template_name = 'users/register_user.html'
    success_url = reverse_lazy('users:register_done')
    form_class = RegisterUserForm


class UserRegisterDone(TemplateView):
    """Успешная регистрация"""
    template_name = 'users/register_done.html'


class UserUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Апдейт данных пользователя"""
    model = AdvUser
    form_class = UserUpdateForm
    template_name = 'users/update_user.html'
    success_url = reverse_lazy('users:profile')
    success_message = 'Данные успешно обновлены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class UserUpdatePass(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    """Смена пароля"""
    template_name = 'users/user_update_pass.html'
    success_url = reverse_lazy('users:profile')
    success_message = 'Пароль успешно изменен'


class UserResetPass(SuccessMessageMixin, PasswordResetView):
    """Отправка емаил для восстановления пароля"""
    template_name = 'users/user_pass_reset_send_email.html'
    subject_temolate_name = 'email/pass_reset_letter_subject.txt'
    email_template_name = 'email/pass_reset_letter_body.txt'
    success_url = reverse_lazy('main:index')
    success_message = 'Письмо с инструкциями по сбросу пароля отправлено вам на почту'


class UserResetPassConfirm(SuccessMessageMixin, PasswordResetConfirmView):
    """Смена пароля"""
    template_name = 'users/user_pass_reset.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Сброс пароля выполнен успешно'


def register_activate(request, sign):
    """Активация пользователя"""
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'users/bad_signature.html')

    user = AdvUser.objects.get(username=username)
    if user.is_activated:
        template = 'users/user_is_activated.html'
    else:
        user.is_active = True
        user.is_activated = True
        user.save()
        template = 'users/activation_done.html'
    return render(request, template)