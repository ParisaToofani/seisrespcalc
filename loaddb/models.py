from django.db import models
from .model_choice import *

class PinchingData(models.Model):
    building_type = models.PositiveSmallIntegerField("Building Type", null=True, blank=True, choices = buildingclass.BUILDINGCLASS)
    pinch_x = models.FloatField("Pinch X", null=True, blank=True)
    pinch_y = models.FloatField("Pinch Y", null=True, blank=True)
    betta = models.FloatField("Betta", null=True, blank=True)
    damp = models.FloatField("Damping", null=True, blank=True)

    class Meta:
        verbose_name = u'Pinching Data'
        verbose_name_plural = u'Pinching Data'

# Create your models here.
