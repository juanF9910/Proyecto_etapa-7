from django.db import models

class Permission(models.Model):
    
    role = models.CharField(max_length=20, unique=True)
    can_create = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_manage_all = models.BooleanField(default=False)

