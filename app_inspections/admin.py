from django.contrib import admin
from .models import Deposit, DamagePrice, Inspection, Damage

admin.site.register(Deposit)
admin.site.register(DamagePrice)
admin.site.register(Inspection)
admin.site.register(Damage)