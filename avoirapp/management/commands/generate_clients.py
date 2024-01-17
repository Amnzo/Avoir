# myapp/management/commands/generate_clients.py
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from avoirapp.models import Client

class Command(BaseCommand):
    help = 'Generate 30 clients with realistic names for testing purposes'

    def handle(self, *args, **options):
        fake = Faker()

        for _ in range(50):
            Client.objects.create(
                nom=fake.last_name(),
                prenom=fake.first_name(),
                datenaissance=timezone.now(),
                email=fake.email(),
                telephone=fake.phone_number(),
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated 30 clients with realistic names'))
