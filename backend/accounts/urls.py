from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    # Auth endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.user_profile, name='user_profile'),
    
    # Admin endpoints (requires is_staff=True or is_superuser=True)
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<uuid:user_id>/block/', views.AdminBlockUserView.as_view(), name='admin_block_user'),
    path('admin/ai-usage/', views.AdminAIUsageView.as_view(), name='admin_ai_usage'),
]