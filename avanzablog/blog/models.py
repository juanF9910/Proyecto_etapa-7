from django.db import models

from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User
from jsonschema import ValidationError

class BlogPost(models.Model):
    
    ACCESS_CHOICES = [
        ('none', 'None'),
        ('read only', 'Read Only'),
        ('read and edit', 'Read and Edit'),
    ]

    PUBLIC_CHOICES = [
        ('none', 'None'),
        ('read only', 'Read Only'),
    ]

    OWNER_CHOICES = [
        ('read and edit', 'Read and Edit'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_public = models.CharField(max_length=20, choices=PUBLIC_CHOICES, default='read only')
    authenticated = models.CharField(max_length=20, choices=ACCESS_CHOICES, default='read only')
    team = models.CharField(max_length=20, choices=ACCESS_CHOICES, default='read and edit')
    owner = models.CharField(max_length=20, choices=OWNER_CHOICES, default='read and edit')

    def __str__(self):
        return self.title

    def clean(self):
        """Custom validation for permission consistency."""
        if self.authenticated == 'read and edit' and self.team == 'read only':
            raise ValidationError("Authenticated users cannot have 'read and edit' if the team has 'read only'.")
        if self.team == 'read and edit' and self.owner == 'read only':
            raise ValidationError("Team members cannot have 'read and edit' if the owner has 'read only'.")

    def save(self, *args, **kwargs):
        """Override save to run full_clean for validation."""
        self.full_clean()
        super().save(*args, **kwargs)


class Like(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)