from django import forms
from django.contrib.auth.models import User
from .models import Profile, Contact
from django.core.validators import EmailValidator
import datetime


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', 'Passwords do not match.')

        if len(password) < 4:
            self.add_error(
                'password', 'Password should be at least 4 characters long.')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.save()

        return user


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ContactForm(forms.ModelForm):
    email_validator = EmailValidator()

    class Meta:
        model = Contact
        fields = [
            'photo',
            'first_name',
            'last_name',
            'phone_number',
            'is_favourite',
            'email',
            'birthday',
            'category',
            'address',
            'company_name',
        ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if phone_number:
            if len(str(phone_number)) != 10:
                self.add_error('phone_number', 'Invalid phone number.')
        return phone_number

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        if birthday and birthday > datetime.date.today():
            self.add_error(
                'birthday', 'Invalid birthday. Future dates are not allowed.')
        return birthday

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            try:
                self.email_validator(email)
            except forms.ValidationError:
                self.add_error('email', 'Invalid email.')
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birthday'].widget = forms.DateInput(
            attrs={'type': 'date'})


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']
