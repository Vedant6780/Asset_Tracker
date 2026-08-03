from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('operator', 'Operator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator')

class Asset(models.Model):
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=50, default="Registered")
    location = models.CharField(max_length=100, default="Unknown")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

class AuditLog(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50)
    old_status = models.CharField(max_length=50, null=True, blank=True)
    new_status = models.CharField(max_length=50)
    old_location = models.CharField(max_length=100, null=True, blank=True)
    new_location = models.CharField(max_length=100, null=True, blank=True)
    changed_by = models.CharField(max_length=50)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} on {self.asset.name} at {self.changed_at}"
