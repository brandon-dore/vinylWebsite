# Generated by Django 2.2.5 on 2020-03-10 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_record_artist'),
    ]

    operations = [
        migrations.AddField(
            model_name='ownership',
            name='user_month_purchased',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
    ]
