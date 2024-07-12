import random
import requests
import json
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ContactsApp.models import Contact, Profile
from django.core.files import File
import string
from datetime import date
from io import BytesIO

class Command(BaseCommand):
    help = 'Generates sample data for testing purposes'

    def handle(self, *args, **options):
        data = self.generate_contacts(numUsers=5, maxContacts=10)
        self.operationCompleted()

    def generate_contacts(self, numUsers, maxContacts):
        fake = Faker()
        data = []

        users = []
        
        for i in range(1, numUsers):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f'{first_name}{last_name}'
            password = username
            email = fake.email()

            user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)

            # Create a profile for the user
            profile = Profile(user=user)
            profile.save()

            users.append(user)
            
            # Set the profile picture URL
            profile_photo_url = self.get_random_photo_url()
            response = requests.get(profile_photo_url)
            image_temp_file = BytesIO(response.content)
            profile.photo.save(f'{username}.jpg', File(image_temp_file))

            # Create multiple contacts for each user
            num = random.randint(2, maxContacts)
            for j in range(num):
                contact_data = {
                    'profile': profile,
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'phone_number': '9' + ''.join(random.choices(string.digits, k=9)),
                    'email': fake.email(),
                    'address': fake.address(),
                    'company_name': fake.company(),
                    'birthday': fake.date_of_birth(minimum_age=18, maximum_age=65),
                    'category': random.choice(Contact.CATEGORY_CHOICES)[0],
                    'is_favourite': random.choice([True, False]),
                }

                # Set the contact's photo
                contact_photo_url = self.get_random_photo_url()
                response = requests.get(contact_photo_url)
                image_temp_file = BytesIO(response.content)
                contact = Contact(**contact_data)
                contact.photo.save(f'{username}_contact_{j}.jpg', File(image_temp_file))
                contact.save()
                
                data.append(contact_data)

        return data

    def get_random_photo_url(self):
        width = random.randint(400, 800)
        height = random.randint(400, 800)
        photo_url = f'https://picsum.photos/{width}/{height}'
        return photo_url

    def operationCompleted(self):
        print(f'Generated Data Successfully!')
