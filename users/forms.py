from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import AdvUser
from .models import user_registrated


class RegisterUserForm(forms.ModelForm):
    """Форма для регистрации"""
    email = forms.EmailField(label='Адресс электронной почты', required=True, help_text='example@mail.com')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation._password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', help_text='Введите пароль повторно', widget=forms.PasswordInput)

    def clean_password(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1
    
    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        email = self.cleaned_data['email']
        errors = {}

        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают', code='password_mismatch')}
    
        if email and AdvUser.objects.filter(email=email).values('email'):  # проверяем на уникальность емейла
            errors['email'] = ValidationError('Пользователь с таким email уже зарегистрирован!', code='invalid_email')

        if errors:
            raise ValidationError(errors)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registrated.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'send_messages')


class UserUpdateForm(forms.ModelForm):
    """Форма для апдейта данных пользователя"""

    class Meta:
        model = AdvUser
        fields = ('username', 'first_name', 'last_name', 'send_messages')
