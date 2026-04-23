from django.conf import settings
from django.db import models


class Task(models.Model):
    class Status(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_PROGRESO = "EN_PROGRESO", "En progreso"
        COMPLETADA = "COMPLETADA", "Completada"

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    estado = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDIENTE,
    )

    asignada_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tareas_asignadas",
    )

    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tareas_creadas",
    )

    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

from django.core.exceptions import ValidationError

def validate_file_size(value):
    filesize = value.size
    if filesize > 4 * 1024 * 1024:
        raise ValidationError("El archivo no puede pesar más de 4MB.")

def get_upload_path(instance, filename):
    return f"uploads/{filename}"

class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comentarios")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_comments",
    )
    texto = models.TextField()
    archivo = models.FileField(upload_to=get_upload_path, validators=[validate_file_size], null=True, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creada_en"]

    def __str__(self):
        return f"Comment #{self.id} on Task #{self.task_id}"

class ActivityLog(models.Model):
    class ActionChoices(models.TextChoices):
        STATUS_CHANGE = "STATUS_CHANGE", "Cambio de Estado"
        ASSIGNMENT = "ASSIGNMENT", "Asignación"
        NEW_COMMENT = "NEW_COMMENT", "Nuevo Comentario"
        TASK_CREATED = "TASK_CREATED", "Tarea Creada"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="activities")
    action = models.CharField(max_length=20, choices=ActionChoices.choices)
    
    # Podemos guardar detalles en JSON o texto plano
    details = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.actor} - {self.action} on {self.task}"

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    action = models.CharField(max_length=50) # EJ: 'ASSIGNMENT', 'STATUS_CHANGE', 'NEW_COMMENT'
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"To: {self.recipient} - {self.message}"

class ChatMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_messages")
    texto = models.TextField(blank=True)
    archivo = models.FileField(upload_to=get_upload_path, validators=[validate_file_size], null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender} at {self.timestamp}"
