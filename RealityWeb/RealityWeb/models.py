from django.db import models
from django.db import transaction
from django import forms

# Create your models here.
class Post(models.Model):
    miasto = models.CharField(max_length=20)
    longitude = models.FloatField()
    latitude = models.FloatField()
    content = models.CharField(max_length=80)
    ident = models.IntegerField(default=999)
    def __str__(self):
        return f'{self.miasto}.{self.content}.{self.ident}'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.ident = self.id
            super().save(*args, **kwargs)

class GetPriceModel(models.Model):
    lat = models.DecimalField( max_digits=7, decimal_places=4, null=True, blank=True )
    lon = models.DecimalField( max_digits=7, decimal_places=4, null=True, blank=True  )
    category = models.CharField(max_length=20, choices=[('domek', 'domek'), ('mieszkanie', 'mieszkanie')])
    subject = models.CharField(max_length=120)
