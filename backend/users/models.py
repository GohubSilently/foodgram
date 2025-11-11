from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, help_text='Имя')
    last_name = models.CharField(max_length=150, help_text='Фамилия')
    is_subscribed = models.BooleanField(default=False, help_text='Подписан')
    avatar = models.ImageField(upload_to='users/', help_text='Аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('email',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.email} - {self.username}'


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='subscriptions'
    )
    follower = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='followers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'follower'],
                name='unique_subsribtion',
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} - {self.follower}'
