from django.core.management.base import BaseCommand
from api.models import CustomUser, Asset, AuditLog

class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **kwargs):
        if CustomUser.objects.exists():
            self.stdout.write(self.style.SUCCESS('Database already seeded.'))
            return

        # Users
        admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        operator = CustomUser.objects.create_user(
            username='operator',
            email='operator@example.com',
            password='operator123',
            role='operator'
        )
        self.stdout.write(self.style.SUCCESS('Created users: admin, operator'))

        # Assets
        assets_data = [
            {"name": "Medical Scanner",        "serial_number": "SN-9982", "location": "Warehouse A",   "status": "Registered"},
            {"name": "Portable Defibrillator", "serial_number": "SN-4410", "location": "Warehouse B",   "status": "In Warehouse"},
            {"name": "Surgical Kit Alpha",     "serial_number": "SN-7721", "location": "Truck 2",       "status": "In Transit"},
            {"name": "Lab Centrifuge",         "serial_number": "SN-3305", "location": "Lab C",         "status": "Delivered"},
            {"name": "X-Ray Machine",          "serial_number": "SN-6618", "location": "Warehouse A",   "status": "Under Maintenance"},
        ]

        for data in assets_data:
            asset = Asset.objects.create(**data)
            AuditLog.objects.create(
                asset=asset,
                action="CREATED",
                new_status=data["status"],
                new_location=data["location"],
                changed_by="system"
            )

        self.stdout.write(self.style.SUCCESS('Created dummy assets with audit logs.'))
