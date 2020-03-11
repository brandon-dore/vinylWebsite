from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import string, random
from django.utils.encoding import force_text
from stdimage import StdImageField, JPEGField

FORMATS = (
    ('vinyl','Vinyl'),
    ('cd', 'CD'),
    ('cassete','Cassete'),
)

MONTHS = (
    ('0','January'),
    ('1', 'Febuary'),
    ('2','March'),
    ('3','April'),
    ('4', 'May'),
    ('5','June'),
    ('6','July'),
    ('7','August'),
    ('8', 'September'),
    ('9','October'),
    ('10','November'),
    ('11', 'December'),
)

class Record(models.Model): 
    recordName = models.CharField(max_length=865)
    record_cover = StdImageField(upload_to='images/', variations={'thumbnail': {'width': 550, 'height': 550}} )
    record_format = models.CharField(max_length=7, choices=FORMATS, default='vinyl')
    artist = models.CharField(max_length=150)
    price = models.DecimalField(decimal_places=2, max_digits=5)
    label = models.CharField(max_length=50, blank=True)
    add_date = models.DateTimeField("record added")
    month_purchased = models.CharField(max_length=9, choices=MONTHS, default='')

    def __str__(self):
        date = timezone.localtime(self.add_date)
        return f"'{self.recordName}' record added {date.strftime('%A, %d %B, %Y at %X')}"

class Ownership(models.Model):
    class Meta:
        unique_together = (('userID', 'recordID'))
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    recordID = models.ForeignKey(Record, on_delete=models.CASCADE)
    user_month_purchased = models.CharField(max_length=1, choices=MONTHS, default='', null = True, blank = True)

class Stats(models.Model):
    userID = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True)
    avg_price = models.DecimalField(decimal_places=2, max_digits=5)
    min_price = models.DecimalField(decimal_places=2, max_digits=5)
    max_price = models.DecimalField(decimal_places=2, max_digits=5)






