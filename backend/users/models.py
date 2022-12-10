"""Модели приложения users для управления пользователями.
Модель пользователя (user) основана на AbstractUser из Django.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Уникальный логин',
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=150,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
    )
    subscribe = models.ManyToManyField(
        'self',
        verbose_name='Подписка',
        related_name='subscribes',
        symmetrical=False,
    )

    class Meta:
        verbose_name = 'Пользователь',
        verbose_name_plural = 'Пользователи',
        ordering = ('username', )

    def __str__(self):
        return f'Логин: {self.username}, почта: {self.email}'
