from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from .models import Task, TaskComment, ActivityLog, Notification

channel_layer = get_channel_layer()
User = get_user_model()

def create_and_send_notification(recipient, task, action, message):
    # 1. Crear en BD
    notif = Notification.objects.create(
        recipient=recipient,
        task=task,
        action=action,
        message=message
    )
    
    # 2. Enviar por WebSocket al grupo correcto
    payload = {
        "type": "send_notification",
        "payload": {
            "id": notif.id,
            "type": "DIRECT",
            "action": notif.action,
            "task_id": task.id if task else None,
            "task_title": task.titulo if task else None,
            "message": notif.message,
            "timestamp": notif.timestamp.isoformat(),
            "is_read": False
        }
    }
    
    if getattr(recipient, "rol", "") == "ADMIN":
        group_name = "admin_feed"
    else:
        group_name = f"user_{recipient.id}_feed"
        
    async_to_sync(channel_layer.group_send)(group_name, payload)

def process_events(task, action, details, actor):
    actor_username = actor.username if actor else "Sistema"
    
    # === 1. MÓDULO DE AUDITORÍA (Historial Silencioso) ===
    # Siempre se registra el movimiento general
    ActivityLog.objects.create(
        actor=actor,
        task=task,
        action=action,
        details=details
    )

    # === 2. MÓDULO DE NOTIFICACIONES (Alertas) ===
    # Reglas estrictas:
    
    if action == "ASSIGNMENT":
        # Ejecutor: Recibe notif si se le asigna la tarea
        new_user_username = details.get("new_user")
        if new_user_username:
            try:
                new_user = User.objects.get(username=new_user_username)
                if new_user != actor:  # No notificarse a uno mismo
                    msg = f"{actor_username} te ha asignado la tarea '{task.titulo}'."
                    create_and_send_notification(new_user, task, action, msg)
            except User.DoesNotExist:
                pass

    elif action == "STATUS_CHANGE":
        # Superadmin: Recibe notif solo si cambió a 'Completada'
        if details.get("new") == "COMPLETADA":
            admins = User.objects.filter(rol="ADMIN")
            msg = f"{actor_username} marcó la tarea '{task.titulo}' como Completada."
            for admin in admins:
                if admin != actor:
                    create_and_send_notification(admin, task, action, msg)

    elif action == "NEW_COMMENT":
        # Superadmin: Recibe siempre si alguien comenta
        admins = User.objects.filter(rol="ADMIN")
        msg_admin = f"{actor_username} comentó en '{task.titulo}'."
        for admin in admins:
            if admin != actor:
                create_and_send_notification(admin, task, action, msg_admin)
                
        # Ejecutor: Recibe si la tarea la tiene asignada él
        if task.asignada_a and getattr(task.asignada_a, "rol", "") != "ADMIN":
            if task.asignada_a != actor:
                msg_ejecutor = f"{actor_username} comentó en tu tarea '{task.titulo}'."
                create_and_send_notification(task.asignada_a, task, action, msg_ejecutor)


@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance, **kwargs):
    if instance.id:
        old_instance = Task.objects.get(id=instance.id)
        instance._old_estado = old_instance.estado
        instance._old_asignada = old_instance.asignada_a
    else:
        instance._old_estado = None
        instance._old_asignada = None

@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    import datetime
    now = datetime.datetime.now().isoformat()
    actor = None

    if not created:
        if hasattr(instance, '_old_estado') and instance._old_estado != instance.estado:
            details = {"old": instance._old_estado, "new": instance.estado, "timestamp": now}
            process_events(instance, "STATUS_CHANGE", details, actor)
        
        if hasattr(instance, '_old_asignada') and instance._old_asignada != instance.asignada_a:
            details = {
                "old_user": instance._old_asignada.username if instance._old_asignada else None,
                "new_user": instance.asignada_a.username if instance.asignada_a else None,
                "timestamp": now
            }
            process_events(instance, "ASSIGNMENT", details, actor)

@receiver(post_save, sender=TaskComment)
def comment_post_save(sender, instance, created, **kwargs):
    if created:
        details = {
            "texto": instance.texto,
            "timestamp": instance.creada_en.isoformat()
        }
        process_events(instance.task, "NEW_COMMENT", details, instance.author)
