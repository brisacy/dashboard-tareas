from rest_framework import serializers
from .models import Task, TaskComment, ActivityLog, Notification


class TaskCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    author_rol = serializers.CharField(source="author.rol", read_only=True)  
    class Meta:
        model = TaskComment
        fields = ["id", "task", "author", "author_username", "author_rol", "texto", "archivo", "creada_en"]
        read_only_fields = ["id", "task", "author", "author_username", "author_rol", "creada_en"]

class TaskSerializer(serializers.ModelSerializer):
    asignada_a_username = serializers.CharField(source="asignada_a.username", read_only=True)
    creada_por_username = serializers.CharField(source="creada_por.username", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "titulo",
            "descripcion",
            "estado",
            "asignada_a",
            "asignada_a_username",
            "creada_por",
            "creada_por_username",
            "creada_en",
            "actualizada_en",
        ]
        read_only_fields = ["creada_por", "creada_en", "actualizada_en"]

class ActivityLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True, default="Sistema")
    task_title = serializers.CharField(source="task.titulo", read_only=True)

    class Meta:
        model = ActivityLog
        fields = ["id", "actor_username", "task", "task_title", "action", "details", "timestamp"]

class NotificationSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source="task.titulo", read_only=True)
    
    class Meta:
        model = Notification
        fields = ["id", "task", "task_title", "message", "action", "is_read", "timestamp"]

from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    sender_rol = serializers.CharField(source="sender.rol", read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ["id", "sender", "sender_username", "sender_rol", "texto", "archivo", "timestamp"]
        read_only_fields = ["id", "sender", "sender_username", "sender_rol", "timestamp"]
