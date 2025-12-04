from django import forms
from django.contrib.auth.forms import UserChangeForm

from .models import User


class UserForm(UserChangeForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label='Пароль',
    )

    class Meta:
        model = User
        exclude = (
            'user_permissions', 'groups', 'is_staff', 'is_active',
            'date_joined', 'last_login', 'is_superuser'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user