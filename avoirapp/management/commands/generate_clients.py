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
            # Generate a random date of birth between 18 and 70 years ago
            date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=70)
            Client.objects.create(
                nom=fake.last_name(),
                prenom=fake.first_name(),
                datenaissance=date_of_birth,
                #email=fake.email(),
                #telephone=fake.phone_number(),
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated 30 clients with realistic names and dates of birth'))
