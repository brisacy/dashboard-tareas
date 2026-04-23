from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .serializers import RegisterSerializer, UserMiniSerializer, UserSerializer, AdminCreateUserSerializer, ChangePasswordSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Endpoint de registro de usuarios.
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ExecutorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "rol", "") != "ADMIN":
            raise PermissionDenied("Solo ADMIN puede ver ejecutores.")

        qs = User.objects.all().order_by("username")
        return Response(UserMiniSerializer(qs, many=True).data)

class AdminCreateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if getattr(request.user, "rol", "") != "ADMIN":
            raise PermissionDenied("Solo ADMIN puede crear usuarios.")
            
        serializer = AdminCreateUserSerializer(data=request.data)
        if serializer.is_valid():
            # Generate random password and username
            email = serializer.validated_data['email']
            username = email.split('@')[0]
            
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            temp_password = get_random_string(length=12, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            
            user = User(
                username=username,
                email=email,
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                rol=serializer.validated_data.get('rol', 'EJECUTOR'),
                force_password_change=True
            )
            user.set_password(temp_password)
            user.save()
            
            # Send welcome email
            send_mail(
                subject='Bienvenido a WorkSpace - Tu cuenta ha sido creada',
                message=f'Hola {user.first_name},\n\nTu cuenta ha sido creada exitosamente. '
                        f'Tu contraseña temporal es: {temp_password}\n\n'
                        f'Por favor, inicia sesión para cambiar tu contraseña obligatoriamente.',
                from_email='no-reply@dashboard.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.force_password_change = False
            user.save()
            return Response({"detail": "Contraseña actualizada exitosamente."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
