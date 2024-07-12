from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # User Authentication
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.userprofile, name='userprofile'),

    # User Profile Updatation
    path('changepassword/', views.change_password, name='change_password'),
    path('updateprofile/', views.update_profile, name='update_profile'),

    # Contacts
    path('add_contact', views.add_contact, name='add_contact'),
    path('contact/<uuid:contact_id>/', views.contact, name='contact'),
    path('update/<uuid:contact_id>/', views.update_contact, name='update_contact'),
    path('delete/<uuid:contact_id>/', views.delete_contact, name='delete_contact'),
    path('search/', views.search_contact, name='search'),

    # Import, Export, Duplicate Deletion of Contacts
    path('export/', views.export_contacts, name='export_contacts'),
    path('import/', views.import_contacts, name='import_contacts'),
    path('delduplicates/', views.delete_duplicate_contacts, name='delduplicates'),
]
