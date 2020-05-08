import re
from datetime import datetime
from random import randint

from django.views import generic
from django.views.generic import ListView, FormView, DetailView, DeleteView, CreateView, UpdateView, TemplateView
from django.db import models
from django.db.models import When
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_protect, csrf_exempt, CsrfViewMiddleware
from django.template import Context
from website.models import Record, Ownership, Stats 
from website.forms import AddRecordForm, SignUpForm, DeleteRecordForm, UpdateInformationForm

from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404, HttpResponseRedirect

from chartjs.views.lines import BaseLineChartView


class HomeListView(TemplateView):
    template_name = 'website/home.html'

    def record(self, *args, **kwargs): # Querys the database for all the current users records
        user = self.request.user.id
        recordOwnedList = Record.objects.filter(ownership__userID = user).values_list('ownership__recordID', flat = True) # Creates a list of the recordID's the user owns
        record = Record.objects.filter(pk__in = recordOwnedList) # Finds the full records of the corrosponding recordID's
        return record

class LandingPageView(TemplateView): # Simply renders the landing page HTML
    template_name = 'website/landingPage.html'

class RecordInfoView(TemplateView):
    template_name = 'website/record_information.html'

    def record(self, *args, **kwargs): # Performs the same query as HomeListView
        recordOwnedList = Record.objects.filter(ownership__userID = self.request.user.id, pk = self.kwargs['pk']).values_list('ownership__recordID', flat = True)
        record = Record.objects.filter(pk__in = recordOwnedList)
        return record
    
    def ownership(self, *args, **kwargs): # So the delete button functions correctly
        ownership = Ownership.objects.filter(userID_id = self.request.user.id, recordID_id = self.kwargs['pk']) # Gets the ownership object of the record clicked on (via the URL)
        return ownership

class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url= '/'

    def form_valid(self, form): # Runs once validation has been performed on the form
        valid = super(SignUpView, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1') # Gets the username and password just used
        new_user = authenticate(username=username, password=password) # Authenticats the data just retrived
        login(self.request, new_user) # Logs the user into the account they just created 
        return valid

class UpdateInformationView(UpdateView):
    model = User
    template_name = 'registration/update_information.html'
    form_class = UpdateInformationForm
    success_url="/"

    def form_valid(self, form, user):
        if self.kwargs['pk'] != user.id: # If the primary key of the page (which is the userID) is not the same as the current user id return a error
            HttpResponseForbidden('You cannot view what is not yours')
        else:
            return super().form_valid(form) # Display the form to update info

class AddRecordView(CreateView):
    model = Record
    success_url= '/addowner'
    form_class = AddRecordForm
    template_name = 'website/add_record.html'
    ownership = Ownership()

    def form_valid(self, form):
        month_purchased = form.instance.month_purchased # Gets the currently entered month purchased when form is submitted
        self.request.session['month_purchased'] = month_purchased # Sets that month as a session (to be able to pass it to add owner function)
        form.instance.add_date = datetime.now() # Generates the current date and sets it as the add date
        return super().form_valid(form)


class UpdateRecordView(UpdateView):
    model = Record
    template_name = 'website/update_record.html'
    form_class = AddRecordForm
    success_url="/"

    def form_valid(self, form, *args, **kwargs):
        recordID = self.object.id 
        month_purchased = form.instance.month_purchased 
        self.request.session['recordID'] = recordID # Sets the recordID as a session (to be able to pass it to add NEW owner function)
        self.request.session['month_purchased'] = month_purchased # Sets the month_purchased as a session (to be able to pass it to add NEW owner function)
        Q1 = Record.objects.filter(ownership__userID = self.request.user.id, ownership__recordID = self.object.id).values_list('ownership__recordID', flat = True) # Generates a list of the current record being edited
        if len(Q1) == 1: # IF the list made above has length one they own the record
            form.instance.user = self.request.user
            form.instance.add_date = datetime.now()
            return super().form_valid(form) # Pushes the form as normal
        else: 
            return redirect('add_new_owner') # A new owner needs to be added since they don't already own the record
            
class DeleteRecordView(DeleteView):
    model = Ownership # Only deletes from the ownership table
    template_name = 'website/delete_record.html'
    success_url="/"

    def get_object(self, queryset=None): # Gets the object being deleted to pass to the delete view
        obj = super(DeleteRecordView, self).get_object()
        if obj.userID_id != self.request.user.id: # Checks if the user owns the record or not before deleting 
            raise Http404
        else:
            return obj

class SearchResultsView(ListView): # List view due to tabular design
    model = Record
    template_name = 'website/search_results.html'

    def get_queryset(self): # Extends the get_queryset logic  
        query = self.request.GET.get('q')
        object_list = Record.objects.filter(Q(recordName__icontains=query)) # Finds records with names LIKE the search term
        return object_list


class LineChartNormView(TemplateView): # THE MAIN stats page view
    template_name='website/stats.html'
    def stats(self, *args, **kwargs):
        priceList = Record.objects.filter(ownership__userID = self.request.user.id).values_list('price', flat = True) # Gets list of all users prices
        priceList = sorted(priceList) # Sorts the list into ascending order
        priceavg = sum(priceList)/len(priceList) # Finds the mean price
        pricemin = priceList[0] # Finds the min price (first index since sorted list)
        pricemax = priceList[(len(priceList)-1)] # Finds the max price (last index since sorted list)
        stats = Stats(userID = self.request.user, avg_price = priceavg, min_price = pricemin, max_price = pricemax) 
        stats.save() # Saves the data to the dB 
        statisticsQ = Stats.objects.filter(userID = self.request.user.id) # Enables this data to be outputted
        return statisticsQ

class LineChartJSONView(BaseLineChartView):
    template_name = 'website/stats.html'
    model = Record

    def get_labels(self):
        # X-axis Labels
        return ["January", "February", "March", "April", "May", "June", "July", "August", "October", "September", "November", "December"]

    def get_providers(self):
        # Dataset names
        return ["Your average spend", "Average Users spend"]

    def get_data(self):
        # Creates the data for datasets in form [[current user data], [average user data]]
        listData = [[], []]
        recordOwnedList = Ownership.objects.filter(userID_id = self.request.user.id).values_list('recordID_id', flat = True) # Gets a list of all the records the current user owns
        for x in range(0, 12): # Loops through all the months (Jan-Dec)
            userData = Record.objects.filter(pk__in = recordOwnedList, ownership__user_month_purchased = x).values_list('price', flat = True) # Gets a list of the price of records THE CURRENT user owns for a specific month
            avgData = Record.objects.filter(ownership__user_month_purchased = x).values_list('price', flat = True) # Gets a list of the price of records EVERY user owns for a specific month
            if len(userData) > 0: # Prevents dividing by zero errors
                userData = round((sum(userData))/(len(userData)), 2) # Calculates average price of records for the current user for that month
            else:
                userData = 0
            if len(avgData) > 0:
                avgData = round((sum(avgData))/(len(avgData)), 2) # The same as first IF statement but for every users data
            else:
                avgData = 0
            listData[0].append(userData) # Adds the data to the corrosponding list inside the 2D array
            listData[1].append(avgData)
        return listData

class PieChartJSONView(BaseLineChartView):
    template_name = 'website/stats.html'
    model = Record

    def get_labels(self):
        # X-axis Labels
        return ["Vinyl", "CD", "Cassete"]

    def get_providers(self):
        # Dataset names
        return ["Ratio of Record Types", "Average Ration"]

    def get_data(self):
        # Data for datasets in form [current user data]
        listData = [[]]
        vinylOwnedList = Record.objects.filter(ownership__userID = self.request.user.id, record_format = "vinyl").values_list('record_format', flat = True) # The next 3 lines get a list of "record format" for each record they have of a specific format
        CDOwnedList = Record.objects.filter(ownership__userID = self.request.user.id, record_format = "cd").values_list('record_format', flat = True) # CD list
        casseteOwnedList = Record.objects.filter(ownership__userID = self.request.user.id, record_format = "cassete").values_list('record_format', flat = True) # cassete list
        listData[0].append(len(vinylOwnedList)) # Then the length of the lists are appended to the dataset since that is how many there are
        listData[0].append(len(CDOwnedList))
        listData[0].append(len(casseteOwnedList))
        return listData

def AddOwnerView(request):
    user_month_purchased = request.session['month_purchased'] # Grabs the 'month_purchased' variable from add record view
    currentRecordID = Record.objects.order_by("id").last().id # Gets the id of the record being added
    recordID = Record.objects.get(id=currentRecordID) # From the recordd ID the whole object is retrived
    currentUser = request.user
    ownership = Ownership(recordID = recordID, userID = currentUser, user_month_purchased = user_month_purchased) 
    ownership.save()
    return redirect("home")

def AddNewOwnerView(request):
    user_month_purchased = int(request.session['month_purchased']) 
    record_id = int(request.session['recordID']) # Grabs the 'recordID' variable from update record view
    userID = request.user.id
    ownership = Ownership(recordID_id = record_id, userID_id = userID, user_month_purchased = user_month_purchased)
    ownership.save()
    return redirect("home")


