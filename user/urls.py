from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import JoinView, LoginView, ChangePasswordView, EncryptedUserView, UserListView, UserDetailView

urlpatterns = [
    path('join/', JoinView.as_view(), name='join'),
    path('', LoginView.as_view(), name='login'),
    path('google/', include('allauth.socialaccount.providers.google.urls')),
    path('kakao/', include('allauth.socialaccount.providers.kakao.urls')),
    path('account/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('account/', EncryptedUserView.as_view(), name='account'),
    path('all/', UserListView.as_view(), name='user-list'),  # 전체 사용자 목록 조회
    path('current/', UserDetailView.as_view(), name='user-detail'),  # 현재 사용자 정보 조회
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
]
