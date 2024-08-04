from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import ChangePasswordSerializer
from .models import CustomUser
from .serializers import EncryptedUserSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

# 회원가입 로직
class JoinView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# 로그인 로직
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # 사용자가 인증되었는지 확인
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # 사용자 인증 성공 시 토큰 생성 및 반환
            token, created = Token.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data  # 사용자 데이터를 직렬화
            return Response({'token': token.key, 'user': user_data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
# 비밀번호 변경 로직
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = get_user_model()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.validated_data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # Set new password
            self.object.set_password(serializer.validated_data.get("new_password"))
            self.object.save()
            update_session_auth_hash(request, self.object)  # Important for keeping the user logged in
            return Response({"status": "password set"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# 사용자 정보
class EncryptedUserView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = EncryptedUserSerializer
    permission_classes = [permissions.IsAuthenticated]  # 인증된 사용자만 접근 허용

    def get_queryset(self):
        # 선택적으로 특정 사용자의 정보만 제공할 수 있음
        return self.queryset.filter(username=self.request.user.username)
    
class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # 관리자 권한이 있는 사용자만 접근 가능

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # 현재 인증된 사용자 정보 반환