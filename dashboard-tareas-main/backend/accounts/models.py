from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        EJECUTOR = "EJECUTOR", "Ejecutor"

    telefono = models.CharField(max_length=30, blank=True)
    rol = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.EJECUTOR,
    )
    force_password_change = models.BooleanField(default=False)
