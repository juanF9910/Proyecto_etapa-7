# Generated by Django 5.1.3 on 2024-11-27 21:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_blogpost_edit_access_blogpost_read_access"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="blogpost",
            name="read_access",
        ),
    ]