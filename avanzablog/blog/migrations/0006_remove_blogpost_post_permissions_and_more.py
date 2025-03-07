# Generated by Django 5.1.4 on 2025-02-13 21:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_alter_blogpost_author_alter_comment_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='post_permissions',
        ),
        migrations.AddField(
            model_name='blogpost',
            name='authenticated',
            field=models.CharField(choices=[('none', 'None'), ('read only', 'Read Only'), ('read and edit', 'Read and Edit')], default='read only', max_length=20),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='owner',
            field=models.CharField(choices=[('none', 'None'), ('read only', 'Read Only'), ('read and edit', 'Read and Edit')], default='read and edit', max_length=20),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='public',
            field=models.CharField(choices=[('none', 'None'), ('read only', 'Read Only'), ('read and edit', 'Read and Edit')], default='read only', max_length=20),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='team',
            field=models.CharField(choices=[('none', 'None'), ('read only', 'Read Only'), ('read and edit', 'Read and Edit')], default='read and edit', max_length=20),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]
