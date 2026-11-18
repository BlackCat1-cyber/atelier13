from django.contrib import admin
from .models import Category, Theme, Costume, CostumeTheme, SizeParams

admin.site.register(Category)
admin.site.register(Theme)
admin.site.register(Costume)
admin.site.register(CostumeTheme)
admin.site.register(SizeParams)