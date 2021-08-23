# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import *

@admin.register(PinchingData)
class PinchingDataAdmin(admin.ModelAdmin):
    list_display = ('building_type', 'pinch_x', 'pinch_y', 'betta', 'damp')
