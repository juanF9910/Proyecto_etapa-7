from django.contrib import admin
from .models import BlogPost

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'title', 'created_at', 'updated_at']
    search_fields = ['author', 'post_permissions']

# Registrar el modelo y su configuración en el admin
admin.site.register(BlogPost, PostAdmin)