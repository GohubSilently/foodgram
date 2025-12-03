from django import forms
from django.contrib.auth.hashers import make_password

from .models import User


class UserChangeForm(forms.ModelForm):
    new_password = forms.CharField(required=False, label='Новый пароль')

    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        password = self.cleaned_data.get('new_password')
        if password:
            instance.password = make_password(password)
        if commit:
            instance.save()
        return instance
