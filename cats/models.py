from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

COLOR_CHOICES = [
    ('black', 'Черный'),
    ('white', 'Белый'),
    ('orange', 'Рыжий'),
    ('gray', 'Серый'),
    ('mixed', 'Смешанный'),
]


class Cat(models.Model):
    name = models.CharField(max_length=256, verbose_name='Имя кота')
    color = models.CharField(max_length=16, choices=COLOR_CHOICES, verbose_name='Окрас')
    birth_year = models.PositiveIntegerField(verbose_name='Год рождения')
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cats', verbose_name='Владелец'
    )
    image = models.ImageField(
        upload_to='cats/images/', null=True, blank=True, verbose_name='Фото'
    )

    class Meta:
        verbose_name = 'Кот'
        verbose_name_plural = 'Коты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.owner.username})'
