import io
from datetime import datetime
import csv

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required

from .forms import UserRegistrationForm, LoginForm, ContactForm
from .forms import UserEditForm, ProfileEditForm
from django.contrib.auth.forms import PasswordChangeForm

from .models import Contact, Profile
from django.db.models import Count
from django.db.models import Q


def signup(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, 'You have been successfully registered and logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Fill the form correctly!')
    return render(request, 'ContactsApp/forms/register.html', {'form': form})


def user_login(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, 'You have been successfully logged in.')
            return redirect('home')
        else:
            form.add_error('password', 'Username or password is incorrect.')

    return render(request, 'ContactsApp/forms/login.html', context={'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')


@login_required(login_url='login')
def userprofile(request):
    profile = request.user.profile
    return render(request, 'ContactsApp/userprofile.html', {'profile': profile})

@login_required(login_url='login')
def change_password(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Fill the form correctly!')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'ContactsApp/forms/update.html', {'form': form, 'title': 'Change Password', 'profile': profile})


@login_required(login_url='login')
def update_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'ContactsApp/forms/profileUpdate.html', {'user_form': user_form, 'profile_form': profile_form, 'profile': profile})


@login_required(login_url='login')
def add_contact(request):
    profile = request.user.profile
    form = ContactForm(request.POST or None)
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.profile = request.user.profile
            contact.save()
            messages.success(request, 'Contact has been added successfully.')
            return redirect('home')
        else:
            form.add_error(None, 'Fill fields correctly!')
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'ContactsApp/create_contact.html', context)


@login_required(login_url='login')
def home(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    contacts = Contact.objects.filter(profile=profile)

    sort_by = request.GET.get('sort')
    category = request.GET.get('category')
    is_favourite = request.GET.get('favourite', False)
    show_birthdays = request.GET.get('birthday', False)

    today_date = datetime.now().strftime("%Y-%m-%d")
    today_month = datetime.now().strftime("%m")

    birthday_contacts = contacts.filter(birthday__day=today_date[-2:], birthday__month=today_month)

    if show_birthdays:
        contacts = birthday_contacts
        category = ''
    
    if sort_by == 'last_modified':
        contacts = contacts.order_by('-last_modified')
    elif sort_by == 'first_name':
        contacts = contacts.order_by('first_name')

    if is_favourite:
        contacts = contacts.filter(is_favourite=True)

    if category:
        contacts = contacts.filter(category=category)

    total_contacts = contacts.count()
    
    context = {
        'contacts': contacts,
        'total_contacts': total_contacts,
        'is_favourite': is_favourite,
        'category': category,
        'sort_by': sort_by,
        'profile': profile,
        'birthday_contacts': birthday_contacts,
    }

    return render(request, 'ContactsApp/index.html', context)

# @login_required(login_url='login')
def contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    try:
        profile = request.user.profile
    except:
        profile = None
    is_owner = contact.profile.user == request.user

    context = {
        'contact': contact,
        'is_owner': is_owner,
        'profile': profile,
    }

    return render(request, 'ContactsApp/contact.html', context)

@login_required(login_url='login')
def search_contact(request):
    search_query = request.GET.get('q', '')
    user = request.user
    profile = Profile.objects.get(user=user)

    contacts = Contact.objects.filter(profile=profile)

    if search_query:
        contacts = contacts.filter(
            first_name__startswith=search_query) | contacts.filter(
            last_name__startswith=search_query) | contacts.filter(
            phone_number__startswith=search_query) | contacts.filter(
            email__startswith=search_query)

    serialized_contacts = []
    for contact in contacts:
        serialized_contacts.append({
            'id': contact.id,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'phone_number': contact.phone_number,
            'email': contact.email,
            'address': contact.address if contact.address else '',
            'date_of_birth': contact.birthday if contact.birthday else '',
            'category': contact.category if contact.category else '',
        })

    return JsonResponse({'contacts': serialized_contacts})


@login_required(login_url='login')
def update_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    profile = request.user.profile

    if contact.profile != request.user.profile:
        messages.warning(request, 'You are not authorized to do this.')
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ContactForm(instance=contact)

    return render(request, 'ContactsApp/forms/update.html', {'form': form, 'title': 'Update Contact', 'profile': profile})


@login_required(login_url='login')
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    profile = request.user.profile

    if contact.profile != request.user.profile:
        messages.warning(request, 'You are not authorized to do this.')
        return HttpResponseForbidden()

    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contact deleted successfully.')
        return redirect('home')

    return render(request, 'ContactsApp/delete_contact.html', {'contact': contact, 'profile': profile})

@login_required(login_url='login')
def export_contacts(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contacts.csv"'

    user_profile = request.user.profile
    contacts = Contact.objects.filter(profile=user_profile)

    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Phone Number', 'Email',
                     'Address', 'Company Name', 'Birthday', 'Category', 'Favourite'])

    for contact in contacts:
        writer.writerow([contact.first_name, contact.last_name, contact.phone_number, contact.email, contact.address,
                         contact.company_name, contact.birthday, contact.get_category_display(), contact.is_favourite])

    messages.success(request, 'Successfully exported contacts.')
    return response


@login_required(login_url='login')
def import_contacts(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        
        # Check if the uploaded file is a CSV file
        if not file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('import_contacts')

        user_profile = request.user.profile
        expected_columns = ['First Name', 'Last Name', 'Phone Number', 'Email',
                            'Address', 'Company Name', 'Birthday', 'Category', 'Favourite']

        try:
            # Check if the CSV file is empty
            csvfile = io.TextIOWrapper(file, encoding='utf-8-sig')
            reader = csv.reader(csvfile)
            header = next(reader)
            if not header:
                messages.error(request, 'The CSV file is empty.')
                return redirect('import_contacts')

            # Check if the CSV file columns match the expected columns
            if header != expected_columns:
                messages.error(request, 'Invalid CSV file. Columns do not match.')
                return redirect('import_contacts')

            for row in reader:
                if not row:
                    # Skip empty rows in the CSV file
                    continue
                
                first_name, last_name, phone_number, email, address, company_name, birthday, category, is_favourite = row
                try:
                    year, month, day = map(int, birthday.split('-'))
                    birthday = datetime(year, month, day).date()
                except (ValueError, IndexError):
                    birthday = None
                contact = Contact.objects.create(
                    profile=user_profile,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    email=email,
                    address=address,
                    company_name=company_name,
                    birthday=birthday,
                    category=category,
                    is_favourite=is_favourite == 'True'
                )
        except:
            messages.error(request, 'Error while reading the CSV file.')
            return redirect('import_contacts')

        messages.success(request, 'Successfully imported contacts.')
        return redirect('home')

    return render(request, 'ContactsApp/import_contacts.html')

@login_required(login_url='login')
def delete_duplicate_contacts(request):
    profile = request.user.profile

    duplicates = (
        Contact.objects.filter(profile=profile)
        .values('first_name', 'email', 'phone_number')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )

    num_duplicates_deleted = 0

    for duplicate in duplicates:
        duplicate_contacts = Contact.objects.filter(
            Q(profile=profile) &
            Q(first_name=duplicate['first_name']) &
            Q(email=duplicate['email']) &
            Q(phone_number=duplicate['phone_number'])
        ).order_by('-id')

        for contact in duplicate_contacts[1:]:
            contact.delete()
            num_duplicates_deleted += 1

    if num_duplicates_deleted == 0:
        messages.success(request, 'No Duplicates Found!')
    else:
        messages.success(
            request, f'{num_duplicates_deleted} duplicate contacts have been deleted.')
    return redirect('home')
