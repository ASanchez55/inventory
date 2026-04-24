from django.contrib import admin
from .models import Inventory, StockMovement

# Register your models here.
admin.site.register(Inventory)
admin.site.register(StockMovement)
