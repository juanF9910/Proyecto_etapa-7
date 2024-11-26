from django.contrib import admin
from .models import BlogPost

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at']
    search_fields = ['title', 'author__username']

# Registrar el modelo y su configuración en el admin
admin.site.register(BlogPost, PostAdmin)