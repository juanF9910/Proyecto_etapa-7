from django.contrib.auth.models import User
from django.db import models

# Profile model to store additional information like team
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.CharField(max_length=100, default="Default Team")  # Team field

    def __str__(self):
        return self.user.username
