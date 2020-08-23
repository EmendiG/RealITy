from django.db import models
from django.db import transaction

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

    lat = models.DecimalField( max_digits=7, decimal_places=4)
    lon = models.DecimalField( max_digits=7, decimal_places=4)
    #csrftoken = models.CharField(max_length=200)

    area = models.DecimalField(max_digits=5, decimal_places=2)

    typ_zabudowy = models.CharField(max_length=30,
                                    choices=[
                                            ('apartamentowiec', 'apartamentowiec'),
                                            ('blok', 'blok'),
                                            ('kamienica', 'kamienica'),
                                            ('szeregowiec', 'szeregowiec'),
                                            ('NaN', 'inny')
                                    ]
    )

    rok_zabudowy = models.IntegerField()
    liczba_pokoi = models.IntegerField()
    pietro = models.IntegerField()
    max_liczba_pieter = models.IntegerField()

    parking = models.CharField(max_length=40,
                               choices=[
                                        ('brak miejsca parkingowego', 'brak miejsca parkingowego'),
                                        ('garaz', 'garaz'),
                                        ('parking strzezony', 'parking strzezony'),
                                        ('przynalezne na ulicy', 'przynalezny na ulicy'),
                                        ('NaN', 'inny')
                               ]
    )
    kuchnia = models.CharField(max_length=20,
                               choices=[
                                        ('oddzielna', 'oddzielna'),
                                        ('w aneksie', 'w aneksie'),
                                        ('NaN', 'inna')
                               ]
    )
    wlasnosc = models.CharField(max_length=30,
                                choices=[
                                         ('wlasnosc', 'wlasnosc'),
                                         ('spoldzielcze wlasnosciowe', 'spoldzielcze wlasnosciowe'),
                                         ('spoldzielcze wlasnosciowe z KW', 'spoldzielcze wlasnosciowe z KW'),
                                         ('NaN', 'inna')
                                ]
    )
    stan = models.CharField(max_length=30,
                            choices=[
                                     ('stan deweloperski', 'stan deweloperski'),
                                     ('do zamieszkania', 'do zamieszkania'),
                                     ('swiezo po remoncie', 'swiezo po remoncie'),
                                     ('do wykonczenia', 'do wykonczenia'),
                                     ('do odswiezenia', 'do odswiezenia'),
                                     ('do remontu', 'do remontu'),
                                     ('NaN', 'inny')
                            ]
    )
    material = models.CharField(max_length=15,
                                choices=[
                                         ('zelbet', 'zelbet'),
                                         ('cegla', 'cegla'),
                                         ('plyta', 'plyta'),
                                         ('pustak', 'pustak'),
                                         ('rama H', 'rama H'),
                                         ('silikat', 'silikat'),
                                         ('inne', 'inny')
                                ]
    )
    okna = models.CharField(max_length=30,
                            choices=[
                                     ('aluminiowe', 'aluminiowe'),
                                     ('drewniane', 'drewniane'),
                                     ('plastikowe/PCV', 'plastikowe/PCV'),
                                     ('NaN', 'inne')
                            ]
    )
    rynek = models.CharField(max_length=10,
                             choices=[
                                      ('pierwotny', 'pierwotny'),
                                      ('wtorny', 'wtorny')
                             ]
    )
    tagi =  models.CharField(max_length=200)
