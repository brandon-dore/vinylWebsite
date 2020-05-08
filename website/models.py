from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import string, random
from django.utils.encoding import force_text
from stdimage import StdImageField, JPEGField

# Defines the options for record formats
FORMATS = (
    ('vinyl','Vinyl'),
    ('cd', 'CD'),
    ('cassete','Cassete'),
)

# Defines the options for months with corrosponding number 0-11
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

class Record(models.Model): # Creates the Record table
    recordName = models.CharField(max_length=865) # Standard character field (with maximum length of 865)
    record_cover = StdImageField(upload_to='images/', variations={'thumbnail': {'width': 550, 'height': 550}} ) # Image field process' the image so a thumbnail of 550x550px is created
    record_format = models.CharField(max_length=7, choices=FORMATS, default='vinyl') # Choices as defined above
    artist = models.CharField(max_length=150)
    price = models.DecimalField(decimal_places=2, max_digits=5) # Creates the price field with max of 999.99
    label = models.CharField(max_length=50, blank=True)
    add_date = models.DateTimeField("record added") # Date time field
    month_purchased = models.CharField(max_length=9, choices=MONTHS, default='')

    def __str__(self): # Formats the record added time
        date = timezone.localtime(self.add_date)
        return f"'{self.recordName}' record added {date.strftime('%A, %d %B, %Y at %X')}"

class Ownership(models.Model): # Creates the Ownership table
    class Meta:
        unique_together = (('userID', 'recordID')) # Composite primary key definition
    userID = models.ForeignKey(User, on_delete=models.CASCADE) # A foreign key relationship of UserID from the Django users table
    recordID = models.ForeignKey(Record, on_delete=models.CASCADE)
    user_month_purchased = models.CharField(max_length=1, choices=MONTHS, default='', null = True, blank = True) # Adds the user specific month purchased for stats query logic

class Stats(models.Model): # Creates the Stats table
    userID = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True) # A one-to-one relationship so each userID will have one stats row
    avg_price = models.DecimalField(decimal_places=2, max_digits=5)
    min_price = models.DecimalField(decimal_places=2, max_digits=5)
    max_price = models.DecimalField(decimal_places=2, max_digits=5)






