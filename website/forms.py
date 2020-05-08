from django import forms
from website.models import Record, Ownership
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime

class AddRecordForm(forms.ModelForm): # Creates the add record form (used in update record as well)
    class Meta:
        model = Record # Gives the model being used
        # Defines all fields (no other logic needed since validion done in models)
        fields = ["recordName", "artist", "record_cover", "record_format", "price", "label", "month_purchased"] 

class DeleteRecordForm(forms.Form): # Fix (adds button) for deleting records in ownership table
    btn = forms.CharField()

class SignUpForm(UserCreationForm): # Creates signup form
    username = forms.CharField(required=True) # Forces the fields to be not null
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email',) # Defines the fields specifically

class UpdateInformationForm(UserCreationForm): # Creates update info form
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False) # Adds more fields than sign up form for more personalisation
    last_name = forms.CharField(required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
