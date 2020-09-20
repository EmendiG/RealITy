from django.db import models
from django.db import transaction
from multiselectfield import MultiSelectField

# Create your models here.
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

class FindFeaturesModel(models.Model):

    lat = models.DecimalField( max_digits=7, decimal_places=4)
    lon = models.DecimalField( max_digits=7, decimal_places=4)

    mapka_radius = models.IntegerField()
    city = models.CharField(max_length=40)

    feature_shop = MultiSelectField(max_length=800,
                                    default=('all_shop', 'WSZYSTKIE'),
                                    choices=[
                                            ('all_shop', 'WSZYSTKIE'),
                                            ('mall', 'centrum handlowe'),
                                            ('pastry', 'cukiernia'),
                                            ('department_store', 'dom towarowy'),
                                            ('chemist', 'drogeria'),
                                            ('hairdresser', 'fryzjer'),
                                            ('deli', 'garmażeria'),
                                            ('kiosk', 'kiosk'),
                                            ('florist', 'kwiaciarnia'),
                                            ('ice_cream', 'lodziarnia'),
                                            ('bakery', 'piekarnia'),
                                            ('butcher', 'rzeźnik'),
                                            ('beauty', 'salon piękności'),
                                            ('jewelry', 'sklep jubilerski'),
                                            ('alcohol', 'sklep monopolowy'),
                                            ('convenience', 'sklep wielobranzowy'),
                                            ('coffee', 'sklep z kawa'),
                                            ('beverages', 'sklep z napojami'),
                                            ('seafood', 'sklep z owocami morza'),
                                            ('wine', 'sklep z winami'),
                                            ('confectionery', 'sklep cukierniczy'),
                                            ('art', 'sklep ze sztuka'),
                                            ('supermarket', 'supermarket'),
                                            ('greengrocer', 'warzywniak'),
                                            ('none_shop', 'ZADNE')
                                    ]
    )

    feature_amenity_fun = MultiSelectField(max_length=800,
                                    default=('all_fun', 'WSZYSTKIE'),
                                    choices=[
                                            ('all_fun', 'WSZYSTKIE'),
                                            ('vending_machine', 'automat vendingowy'),
                                            ('bank', 'bank'),
                                            ('atm', 'bankomat'),
                                            ('bar', 'bar'),
                                            ('fast_food', 'fast food'),
                                            ('arts_centre', 'galeria sztuki'),
                                            ('cafe', 'kawiarnia'),
                                            ('cinema', 'kino'),
                                            ('nightclub', 'klub nocny'),
                                            ('post_office', 'poczta'),
                                            ('police', 'policja'),
                                            ('pub', 'pub'),
                                            ('restaurant', 'restauracja'),
                                            ('theatre', 'teatr'),
                                            ('bicycle_rental', 'wypozyczalnia rowerow'),
                                            ('none_fun', 'ZADNE')
                                    ]
    )

    feature_amenity_healthcare = MultiSelectField(max_length=800,
                                    default=('all_helthcare', 'WSZYSTKIE'),
                                    choices=[
                                            ('all_helthcare', 'WSZYSTKIE'),
                                            ('pharmacy', 'apteka'),
                                            ('dentist', 'dentysta'),
                                            ('doctors', 'gabinet lekarski'),
                                            ('clinic', 'klinika'),
                                            ('hospital', 'szpital'),
                                            ('none_helthcare', 'ZADNE')
                                    ]
    )

    feature_amenity_schooling = MultiSelectField(max_length=800,
                                    default=('all_schooling', 'WSZYSTKIE'),
                                    choices=[
                                            ('all_schooling', 'WSZYSTKIE'),
                                            ('library', 'biblioteka'),
                                            ('kindergarten', 'przedszkole'),
                                            ('school', 'szkola'),
                                            ('college', 'uczelnia'),
                                            ('university', 'uniwersytet'),
                                            ('none_schooling', 'ZADNE')
                                    ]
    )

    feature_leisure = MultiSelectField(max_length=800,
                                    default=('all_leisure', 'WSZYSTKIE'),
                                    choices=[
                                            ('all_leisure', 'WSZYSTKIE'),
                                            ('fitness_centre', 'centrum fitness'),
                                            ('sports_centre', 'ośrodek sportowy'),
                                            ('park', 'park'),
                                            ('playground', 'plac zabaw'),
                                            ('nature_reserve', 'rezerwat przyrody'),
                                            ('none_leisure', 'ZADNE')
                                    ]
    )

    feature_transport = MultiSelectField(max_length=800,
                                    default=('all_transport', 'WSZYSTKIE'),
                                    choices=[
                                            ('all_transport', 'WSZYSTKIE'),
                                            ('bus', 'przystanek autobusowy'),
                                            ('subway', 'metro'),
                                            ('train', 'przystanek kolejowy'),
                                            ('stop_position', 'przystanek'),
                                            ('tram', 'przystanek tramwajowy'),
                                            ('none_transport', 'ZADNE')
                                    ]
    )

    feature_tourism = MultiSelectField(max_length=800,
                                    default=('all_tourism', 'WSZYSTKIE'),
                                    choices=[
                                            ('all_tourism', 'WSZYSTKIE'),
                                            ('attraction', 'atrakcje'),
                                            ('artwork', 'dzieła sztuki'),
                                            ('hotel', 'hotel'),
                                            ('museum', 'muzeum'),
                                            ('viewpoint', 'punkt widokowy'),
                                            ('none_tourism', 'ZADNE')
                                    ]
    )

    
