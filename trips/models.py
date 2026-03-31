from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from cats.models import Cat

User = get_user_model()

STATUS_PLANNED = 'planned'
STATUS_ACTIVE = 'active'
STATUS_COMPLETED = 'completed'

STATUS_CHOICES = [
    (STATUS_PLANNED, 'Запланирована'),
    (STATUS_ACTIVE, 'В процессе'),
    (STATUS_COMPLETED, 'Завершена'),
]


class Trip(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='trips', verbose_name='Владелец'
    )
    cat = models.ForeignKey(
        Cat, on_delete=models.CASCADE, related_name='trips', verbose_name='Кот'
    )
    title = models.CharField(max_length=256, verbose_name='Название поездки')
    description = models.TextField(blank=True, verbose_name='Описание')
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_PLANNED, verbose_name='Статус'
    )
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата начала')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Поездка'
        verbose_name_plural = 'Поездки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.cat.name}'

    def clean(self):
        if self.started_at and self.completed_at:
            if self.completed_at <= self.started_at:
                raise ValidationError('Дата завершения должна быть позже даты начала.')


class Stop(models.Model):
    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name='stops', verbose_name='Поездка'
    )
    title = models.CharField(max_length=256, verbose_name='Название остановки')
    description = models.TextField(blank=True, verbose_name='Описание')
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Широта'
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Долгота'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    visited_at = models.DateTimeField(null=True, blank=True, verbose_name='Время посещения')

    class Meta:
        verbose_name = 'Остановка'
        verbose_name_plural = 'Остановки'
        ordering = ['order', 'id']
        unique_together = [('trip', 'order')]

    def __str__(self):
        return f'{self.trip.title} — остановка {self.order}: {self.title}'
