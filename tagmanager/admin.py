from django.contrib import admin
from .models import *  # Replace YourModel with the name of your model

# Register your models here.
admin.site.register(PLC)
admin.site.register(Equipment)
admin.site.register(EquipmentTag)

# Get the app registry
app_name = 'tagmanager' 
app_config = apps.get_app_config(app_name)
print(app_config)
# Register dynamically created log models
for model_name, model in app_config.models.items():
    print(model_name, model)
    if model_name.endswith('_log'):
        admin.site.register(model)

