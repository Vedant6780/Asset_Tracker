from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter(trailing_slash=False)
router.register(r'assets', AssetViewSet)

urlpatterns = [
    path('auth/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
