from django.contrib import admin

from .models import Record, Ownership, Stats

admin.site.register(Record)
admin.site.register(Ownership)
admin.site.register(Stats)