from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Workspace

User = get_user_model()


class Command(BaseCommand):
    help = 'Create initial data for the application'

    def handle(self, *args, **options):
        # Create default workspace
        if not Workspace.objects.filter(name="Default Workspace").exists():
            workspace = Workspace.objects.create(
                name="Default Workspace",
                description="Default workspace for admin users"
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created workspace: {workspace.name}')
            )
        else:
            workspace = Workspace.objects.get(name="Default Workspace")

        # Create superuser if it doesn't exist
        if not User.objects.filter(email="admin@almo.com").exists():
            admin_user = User.objects.create_superuser(
                email="admin@almo.com",
                username="admin",
                password="admin123",
                workspace=workspace,
                role="admin"
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser: {admin_user.email}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser already exists')
            )