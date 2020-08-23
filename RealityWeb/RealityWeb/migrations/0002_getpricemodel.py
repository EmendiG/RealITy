# Generated by Django 3.1 on 2020-08-22 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RealityWeb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GetPriceModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.DecimalField(decimal_places=4, max_digits=7)),
                ('lon', models.DecimalField(decimal_places=4, max_digits=7)),
                ('area', models.DecimalField(decimal_places=2, max_digits=5)),
                ('typ_zabudowy', models.CharField(choices=[('apartamentowiec', 'apartamentowiec'), ('blok', 'blok'), ('kamienica', 'kamienica'), ('szeregowiec', 'szeregowiec'), ('NaN', 'inny')], max_length=30)),
                ('rok_zabudowy', models.IntegerField()),
                ('liczba_pokoi', models.IntegerField()),
                ('pietro', models.IntegerField()),
                ('max_liczba_pieter', models.IntegerField()),
                ('parking', models.CharField(choices=[('brak miejsca parkingowego', 'brak miejsca parkingowego'), ('garaz', 'garaz'), ('parking strzezony', 'parking strzezony'), ('przynalezne na ulicy', 'przynalezny na ulicy'), ('NaN', 'inny')], max_length=40)),
                ('kuchnia', models.CharField(choices=[('oddzielna', 'oddzielna'), ('w aneksie', 'w aneksie'), ('NaN', 'inna')], max_length=20)),
                ('wlasnosc', models.CharField(choices=[('wlasnosc', 'wlasnosc'), ('spoldzielcze wlasnosciowe', 'spoldzielcze wlasnosciowe'), ('spoldzielcze wlasnosciowe z KW', 'spoldzielcze wlasnosciowe z KW'), ('NaN', 'inna')], max_length=30)),
                ('stan', models.CharField(choices=[('stan deweloperski', 'stan deweloperski'), ('do zamieszkania', 'do zamieszkania'), ('swiezo po remoncie', 'swiezo po remoncie'), ('do wykonczenia', 'do wykonczenia'), ('do odswiezenia', 'do odswiezenia'), ('do remontu', 'do remontu'), ('NaN', 'inny')], max_length=30)),
                ('material', models.CharField(choices=[('zelbet', 'zelbet'), ('cegla', 'cegla'), ('plyta', 'plyta'), ('pustak', 'pustak'), ('rama H', 'rama H'), ('silikat', 'silikat'), ('inne', 'inny')], max_length=15)),
                ('okna', models.CharField(choices=[('aluminiowe', 'aluminiowe'), ('drewniane', 'drewniane'), ('plastikowe/PCV', 'plastikowe/PCV'), ('NaN', 'inne')], max_length=30)),
                ('rynek', models.CharField(choices=[('pierwotny', 'pierwotny'), ('wtorny', 'wtorny')], max_length=10)),
                ('tagi', models.TextField(max_length=200)),
            ],
        ),
    ]
