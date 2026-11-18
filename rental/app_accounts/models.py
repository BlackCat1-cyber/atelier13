from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    ROLE_CHOICES = [
        ("client", "Клиент"),
        ("consultant", "Консультант"),
        ("master", "Мастер"),
        ("admin", "Администратор"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="client", verbose_name="Роль")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Телефон")
    height_cm = models.IntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(140), MaxValueValidator(220)],
        verbose_name="Рост, см"
    )
    clothing_size = models.IntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(38), MaxValueValidator(62)],
        verbose_name="Размер одежды"
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"