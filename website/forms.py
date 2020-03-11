from django import forms
from website.models import Record, Ownership
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime

class AddRecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ["recordName", "artist", "record_cover", "record_format", "price", "label", "month_purchased"]

class DeleteRecordForm(forms.Form):
    btn = forms.CharField()

class SignUpForm(UserCreationForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email',)

class UpdateInformationForm(UserCreationForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
