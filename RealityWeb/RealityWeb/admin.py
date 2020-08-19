from django.contrib import admin
from .models import Post, GetPriceModel

# Register your models here.

admin.site.register(Post)
admin.site.register(GetPriceModel)

