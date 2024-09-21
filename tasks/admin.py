from django.contrib import admin
from .models import Tarea

class TareaAdministrador(admin.ModelAdmin):
    readonly_fields = ("fecha_creacion", )
    
# Register your models here.
admin.site.register(Tarea, TareaAdministrador)