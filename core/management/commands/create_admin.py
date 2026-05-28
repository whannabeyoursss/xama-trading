from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create an admin superuser from environment variables'

    def handle(self, *args, **options):
        import os
        User = get_user_model()

        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@xamatrading.com')
        password = os.environ.get('ADMIN_PASSWORD', '')
        phone = os.environ.get('ADMIN_PHONE', '09000000000')

        if not password:
            self.stdout.write(self.style.WARNING(
                'ADMIN_PASSWORD not set. Skipping admin creation.'
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'Admin user "{username}" already exists. Skipping.'
            ))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            phone_number=phone,
            role='admin',
        )
        self.stdout.write(self.style.SUCCESS(
            f'✅ Admin user "{user.username}" created successfully!'
        ))
