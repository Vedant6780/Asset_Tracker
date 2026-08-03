from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from .models import Asset, AuditLog, CustomUser
from .serializers import AssetSerializer, AuditLogSerializer, CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data = {
                'access_token': response.data['access'],
                'role': response.data['role'],
                'username': response.data['username']
            }
        return response

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all().prefetch_related('audit_logs')
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path=r'lookup/(?P<serial_number>[^/.]+)')
    def lookup(self, request, serial_number=None):
        asset = get_object_or_404(Asset, serial_number=serial_number)
        serializer = self.get_serializer(asset)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='status')
    def status_update(self, request, pk=None):
        asset = self.get_object()
        old_status = asset.status
        old_location = asset.location

        new_status = request.data.get('new_status')
        new_location = request.data.get('location', old_location)

        if not new_status:
            return Response({'detail': 'new_status is required'}, status=status.HTTP_400_BAD_REQUEST)

        asset.status = new_status
        asset.location = new_location
        asset.save()

        # Log if changed
        if old_status != new_status or old_location != new_location:
            AuditLog.objects.create(
                asset=asset,
                action="UPDATED",
                old_status=old_status,
                new_status=new_status,
                old_location=old_location,
                new_location=new_location,
                changed_by=request.user.username
            )

        serializer = self.get_serializer(asset)
        return Response(serializer.data)

    def perform_create(self, serializer):
        asset = serializer.save()
        AuditLog.objects.create(
            asset=asset,
            action="CREATED",
            new_status=asset.status,
            new_location=asset.location,
            changed_by=self.request.user.username
        )

    def perform_update(self, serializer):
        asset = self.get_object()
        old_status = asset.status
        old_location = asset.location

        updated_asset = serializer.save()

        # Log if changed
        if old_status != updated_asset.status or old_location != updated_asset.location:
            AuditLog.objects.create(
                asset=updated_asset,
                action="UPDATED",
                old_status=old_status,
                new_status=updated_asset.status,
                old_location=old_location,
                new_location=updated_asset.location,
                changed_by=self.request.user.username
            )
