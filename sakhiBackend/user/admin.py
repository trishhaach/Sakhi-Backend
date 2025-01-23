from django.contrib import admin
from .models import User
from .models import NonClinicalDetection, AdvancedDetection

admin.site.register(User)

admin.site.register(NonClinicalDetection)
admin.site.register(AdvancedDetection)