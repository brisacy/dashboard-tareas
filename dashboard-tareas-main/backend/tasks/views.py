from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from .models import Task, TaskComment
from .serializers import TaskSerializer, TaskCommentSerializer
from .permissions import IsAdminOrOwner

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().select_related("asignada_a", "creada_por")
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "rol", "") == "ADMIN":
            return Task.objects.all().order_by("-creada_en")
        return Task.objects.filter(asignada_a=user).order_by("-creada_en")

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "rol", "") != "ADMIN":
            raise PermissionDenied("Solo ADMIN puede crear tareas.")
        serializer.save(creada_por=user)

    def perform_update(self, serializer):
        user = self.request.user
        task = self.get_object()

        estado_antes = task.estado
        asignada_antes = task.asignada_a_id

        # Guardado con restricciones
        if getattr(user, "rol", "") != "ADMIN":
            # EJECUTOR: no puede reasignar ni tocar creada_por
            instance = serializer.save(
                asignada_a=task.asignada_a,
                creada_por=task.creada_por
            )
        else:
            instance = serializer.save()

        # --- Comentario automático si cambió el estado ---
        if estado_antes != instance.estado:
            TaskComment.objects.create(
                task=instance,
                author=user,
                texto=f"Estado: {estado_antes} → {instance.estado}"
            )

        # (Opcional) Comentario automático si ADMIN reasignó
        if getattr(user, "rol", "") == "ADMIN" and asignada_antes != instance.asignada_a_id:
            asignado_a = instance.asignada_a.username if instance.asignada_a else "—"
            TaskComment.objects.create(
                task=instance,
                author=user,
                texto=f"Reasignada a: {asignado_a}"
            )


    @action(detail=False, methods=["get"], url_path="mine")
    def mine(self, request):
        # devuelve mis tareas (útil en frontend)
        qs = Task.objects.filter(asignada_a=request.user).order_by("-creada_en")
        return Response(TaskSerializer(qs, many=True).data)
    
    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        task = self.get_object()  # respeta get_queryset + IsAdminOrOwner

        if request.method == "GET":
            qs = task.comentarios.select_related("author").all().order_by("creada_en")
            return Response(TaskCommentSerializer(qs, many=True).data)

        # POST
        texto = (request.data.get("texto") or "").strip()
        archivo = request.FILES.get("archivo")
        
        if not texto and not archivo:
            return Response(
                {"detail": "Debe enviar texto o un archivo adjunto."},
                status=status.HTTP_400_BAD_REQUEST
            )

        TaskComment.objects.create(
            task=task,
            author=request.user,
            texto=texto,
            archivo=archivo
        )

        qs = task.comentarios.select_related("author").all().order_by("creada_en")
        return Response(TaskCommentSerializer(qs, many=True).data, status=status.HTTP_201_CREATED)


from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import ActivityLog, Notification, ChatMessage
from .serializers import ActivityLogSerializer, NotificationSerializer, ChatMessageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class ChatViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().select_related("sender").order_by("timestamp")
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        # Retorna los últimos 50 mensajes
        return super().get_queryset()
        
    def perform_create(self, serializer):
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        
        instance = serializer.save(sender=self.request.user)
        
        # Enviar al WebSocket global_chat
        channel_layer = get_channel_layer()
        payload = {
            "type": "chat_message",
            "message": ChatMessageSerializer(instance).data
        }
        async_to_sync(channel_layer.group_send)("global_chat", payload)

class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, "rol", "") != "ADMIN":
            raise PermissionDenied("Solo el administrador tiene acceso a la auditoría.")
            
        logs = ActivityLog.objects.all().select_related("actor", "task").order_by("-timestamp")[:100]
        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by("-timestamp")
        
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({"status": "ok"})
