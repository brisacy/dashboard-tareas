from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, AuditLogView, NotificationViewSet, ChatViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"notifications", NotificationViewSet, basename="notifications")
router.register(r"chat", ChatViewSet, basename="chat")
urlpatterns = [
    path("audit/", AuditLogView.as_view(), name="audit-log"),
    path("", include(router.urls)),
]
