from django.db import models, connection
from django.db.models.base import ModelBase
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps


class PLC(models.Model):
    ip_address = models.CharField(max_length=50)
    port = models.IntegerField()
    serial_no = models.CharField(max_length=100)

    def __str__(self):
        return f"PLC {self.serial_no}"

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    plc = models.ForeignKey(PLC, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class EquipmentTag(models.Model):
    ZONE_CHOICES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('log', 'Log'),
    ]
    DATA_TYPE = [
        ('INT', 'int'),
        ('BOOL', 'bool'),
        ('DINT', 'dint'),
        ('WORD','word'),
        ('FLOAT', 'float')]

    name = models.CharField(max_length=100)
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES)
    data_type = models.CharField(max_length=15, choices=DATA_TYPE)
    is_alarm = models.BooleanField(default=False)
    is_fault = models.BooleanField(default=False)
    is_data_tag = models.BooleanField(default=False)
    trigger_tag = models.BooleanField(default=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
def create_log_model(equipment_instance):
        
    fields = {
            'timestamp': models.DateTimeField(auto_now_add=True),
            'modified_date': models.DateTimeField(auto_now=True),
        }

    if equipment_instance.is_alarm or equipment_instance.is_fault:
        fields[f'old_value'] = models.BooleanField()
        fields[f'new_value'] = models.BooleanField()
    else:
        fields[f'value'] = models.CharField()

        class LogModel(models.Model):
            class Meta:
                managed = False
                db_table = f"tagmanager_{equipment_instance.name.lower()}_log"

        # Add dynamically created fields to the LogModel
        for field_name, field in fields.items():
            setattr(LogModel, field_name, field)

        return LogModel

class DynamicModelCreator:
    @staticmethod
    def create_log_model_on_equipment_tag_save(sender, instance, created, **kwargs):
        if created:
            equipment_tag_name = instance.name
            log_model_name = f'tagmanager_{equipment_tag_name.lower()}_log'

            if not log_model_name in apps.all_models['tagmanager']:
                log_model = create_log_model(instance)
                apps.all_models['tagmanager'][log_model_name] = log_model

                # Register the model with the app registry
                apps.get_app_config('tagmanager').models_module = True

                print(f"Log model created for equipment tag: {equipment_tag_name}")

                # Create the corresponding table in the database
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(log_model)

# Connect the signal handler to the post_save signal of EquipmentTag
post_save.connect(DynamicModelCreator.create_log_model_on_equipment_tag_save, sender=EquipmentTag)