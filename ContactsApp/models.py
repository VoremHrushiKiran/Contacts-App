from django.db import models
from django.conf import settings
import uuid

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True, default='default.jpg')
    
    def __str__(self):
        return str(self.user)


class Contact(models.Model):
    CATEGORY_CHOICES = [
        ('friends', 'Friends'),
        ('family', 'Family'),
        ('work', 'Work'),
        ('home', 'Home'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='contacts/%Y/%m/%d', blank=True, default='default.jpg')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=10, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    birthday = models.DateField(blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        blank=True,
    )
    is_favourite = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
