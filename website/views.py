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

from chartjs.views.lines import BaseLineChartView, BasePieChartView


class HomeListView(TemplateView):
#Currently renders the home page and shows all records stored in the DB
    template_name = 'website/home.html'

    def record(self, *args, **kwargs):
        user = self.request.user.id
        recordOwnedList = Record.objects.filter(ownership__userID = user).values_list('ownership__recordID', flat = True)
        record = Record.objects.filter(pk__in = recordOwnedList)
        return record

class RecordInfoView(TemplateView):
    template_name = 'website/record_information.html'

    def record(self, *args, **kwargs):
        recordOwnedList = Record.objects.filter(ownership__userID = self.request.user.id, pk = self.kwargs['pk']).values_list('ownership__recordID', flat = True)
        record = Record.objects.filter(pk__in = recordOwnedList)
        return record
    
    def ownership(self, *args, **kwargs):
        ownership = Ownership.objects.filter(userID_id = self.request.user.id, recordID_id = self.kwargs['pk'])
        return ownership

class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    success_url= 'website/home.html'
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        return super().form_valid(form)

class UpdateInformationView(UpdateView):
    model = User
    template_name = 'registration/update_information.html'
    form_class = UpdateInformationForm
    success_url="/"

    def form_valid(self, form, user):
        if self.kwargs['pk'] != user.id:
            HttpResponseForbidden('You cannot view what is not yours')
        else:
            return super().form_valid(form)

class AddRecordView(CreateView):
    model = Record
    success_url= '/addowner'
    form_class = AddRecordForm
    template_name = 'website/add_record.html'
    ownership = Ownership()

    def form_valid(self, form):
        month_purchased = form.instance.month_purchased
        self.request.session['month_purchased'] = month_purchased
        form.instance.add_date = datetime.now()
        return super().form_valid(form)


class UpdateRecordView(UpdateView):
    model = Record
    template_name = 'website/update_record.html'
    form_class = AddRecordForm
    success_url="/"

    def form_valid(self, form, *args, **kwargs):
        recordID = self.object.id
        month_purchased = form.instance.month_purchased
        self.request.session['recordID'] = recordID
        self.request.session['month_purchased'] = month_purchased
        Q1 = Record.objects.filter(ownership__userID = self.request.user.id, ownership__recordID = self.object.id).values_list('ownership__recordID', flat = True)
        if len(Q1) == 1:
            form.instance.user = self.request.user
            form.instance.add_date = datetime.now()
            return super().form_valid(form)
        else:
            return redirect('add_new_owner')
            
class DeleteRecordView(DeleteView):
    model = Ownership
    template_name = 'website/delete_record.html'
    success_url="/"

    def get_object(self, queryset=None):
        obj = super(DeleteRecordView, self).get_object()
        if obj.userID_id != self.request.user.id:
            raise Http404
        else:
            return obj

class SearchResultsView(ListView):
    model = Record
    template_name = 'website/search_results.html'

    def get_queryset(self): #this function needs this name to run since it is extending the get_queryset logic 
        query = self.request.GET.get('q')
        object_list = Record.objects.filter(Q(recordName__icontains=query))
        return object_list


class LineChartNormView(TemplateView):
    template_name='website/stats.html'
    def stats(self, *args, **kwargs):
        priceList = Record.objects.filter(ownership__userID = self.request.user.id).values_list('price', flat = True)
        priceList = sorted(priceList)
        priceavg = sum(priceList)/len(priceList)
        pricemin = priceList[0]
        pricemax = priceList[(len(priceList)-1)]
        stats = Stats(userID = self.request.user, avg_price = priceavg, min_price = pricemin, max_price = pricemax)
        stats.save()
        statisticsQ = Stats.objects.filter(userID = self.request.user.id)
        return statisticsQ

class LineChartJSONView(BaseLineChartView):
    template_name = 'website/stats.html'
    model = Record

    def get_labels(self):
        #X-axis Labels
        return ["January", "February", "March", "April", "May", "June", "July", "August", "October", "September", "November", "December"]

    def get_providers(self):
        #Dataset names
        return ["Your average spend", "Average Users spend"]

    def get_data(self):
        #Data for datasets in form [[current user data], [average user data]]
        listData = [[], []]
        recordOwnedList = Ownership.objects.filter(userID_id = self.request.user.id).values_list('recordID_id', flat = True)
        for x in range(0, 12):
            userData = Record.objects.filter(pk__in = recordOwnedList, ownership__user_month_purchased = x).values_list('price', flat = True)
            avgData = Record.objects.filter(ownership__user_month_purchased = x).values_list('price', flat = True)
            userData = sum(userData)
            avgData = sum(avgData)
            listData[0].append(userData)
            listData[1].append(avgData)
        return listData

class PieChartJSONView(BasePieChartView):
    template_name = 'website/stats.html'
    model = Record

    def get_labels(self):
        #X-axis Labels
        return ["Vinyl", "CD", "Cassete"]

    def get_providers(self):
        #Dataset names
        return ["Ratio of Record Types", "Average Ration"]

    def get_data(self):
        #Data for datasets in form [current user data]
        listData = [[]]
        vinylOwnedList = Record.objects.filter(ownership__userID = self.request.user.id, record_format = "vinyl").values_list('record_format', flat = True)
        CDOwnedList = Record.objects.filter(ownership__userID = self.request.user.id, record_format = "cd").values_list('record_format', flat = True)
        casseteOwnedList = Record.objects.filter(ownership__userID = self.request.user.id, record_format = "cassete").values_list('record_format', flat = True)
        listData[0].append(len(vinylOwnedList))
        listData[0].append(len(CDOwnedList))
        listData[0].append(len(casseteOwnedList))
        return listData

def AddOwnerView(request):
    user_month_purchased = request.session['month_purchased']
    currentRecordID = Record.objects.order_by("id").last().id 
    recordID = Record.objects.get(id=currentRecordID) 
    currentUser = request.user
    ownership = Ownership(recordID = recordID, userID = currentUser, user_month_purchased = user_month_purchased)
    ownership.save()
    return redirect("home")

def AddNewOwnerView(request):
    user_month_purchased = int(request.session['month_purchased'])
    record_id = int(request.session['recordID'])
    userID = request.user.id
    ownership = Ownership(recordID_id = record_id, userID_id = userID, user_month_purchased = user_month_purchased)
    ownership.save()
    return redirect("home")


