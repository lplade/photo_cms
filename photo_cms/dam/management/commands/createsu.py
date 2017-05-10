from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            # Make sure to change the password promptly!
            User.objects.create_superuser('admin', 'larry.p.lade+photo_cms@gmail.com', 'admin')
