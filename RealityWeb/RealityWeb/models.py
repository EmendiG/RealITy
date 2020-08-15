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
            # for python < 3.0 super(pick, self).save(*args, **kwargs)
            self.ident = self.id
            super().save(*args, **kwargs)
            # for python < 3.0 super(pick, self).save(*args, **kwargs)
