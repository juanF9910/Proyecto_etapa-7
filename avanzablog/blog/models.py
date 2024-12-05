from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class BlogPost(models.Model):

    ACCESS_CHOICES = [
        ('public', 'Public'), #solo lectura
        ('authenticated', 'Authenticated'), #solo lectura
        ('team', 'Team'), #leer y editar
        ('author', 'Author'), #leer y editar
    ]
    
    author= models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    post_permissions= models.CharField(max_length=20, choices=ACCESS_CHOICES, default='author', null=False)
 
class Like(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)