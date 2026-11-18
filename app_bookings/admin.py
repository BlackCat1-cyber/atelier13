from django.contrib import admin
from .models import FittingSlot, FittingCostume, Booking

admin.site.register(FittingSlot)
admin.site.register(FittingCostume)
admin.site.register(Booking)