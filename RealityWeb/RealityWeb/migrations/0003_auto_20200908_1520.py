# Generated by Django 3.1.1 on 2020-09-08 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RealityWeb', '0002_getpricemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='getpricemodel',
            name='tagi',
            field=models.CharField(max_length=200),
        ),
    ]