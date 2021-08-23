from django.core.management.base import BaseCommand, CommandError
from loaddb.models import PinchingData


# Run this file using "python manage.py loaddb" command 

class Command(BaseCommand):

    def handle(self, *args, **options):

        def get_val(value):
            if value == "":
                return 999
            else:
                return value
        pinching_param = {1 : [0.6, 0.6, 0.1, 0.0631507],
                    2 : [0.6, 0.6, 0.1, 0.0631507],
                    3 : [1, 1, 0, 0.0433675],
                    4 : [0.5, 0.5, 0.0, 0.0433675],
                    5 : [0.5, 0.5, 0.0, 0.0433675],
                    6 : [0.45, 0.45, 0.0, 0.0433675],
                    7 : [0.4, 0.4, 0.0, 0.0433675],
                    8 : [0.5, 0.5, 0.4, 0.0607146],
                    9 : [0.4, 0.4, 0.4, 0.0607146],
                    10 : [0.3, 0.3, 0.4, 0.0607146],
                    11 : [0.35, 0.35, 0.4, 0.05],
                    12 : [0.3, 0.3, 0.4, 0.05],
                    13 : [0.4, 0.4, 0.1, 0.0867351],
                    14 : [0.4, 0.4, 0.1, 0.0867351],
                    15 : [0.3, 0.3, 0.1, 0.0867351],}
        for key, value in pinching_param.items():
            save_data = PinchingData.objects.create(
            building_type = key,
            pinch_x = value[0],
            pinch_y = value[1],
            betta = value[2],
            damp = value[3],
            )
            save_data.save()
        self.stdout.write(self.style.SUCCESS('Successfully loaded'))