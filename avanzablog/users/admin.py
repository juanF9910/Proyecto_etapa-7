
# Register your models here.
from django.contrib import admin
from .models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['role', 'bio']
    search_fields = ['role']

# Registrar el modelo y su configuración en el admin
admin.site.register(User, UserAdmin)