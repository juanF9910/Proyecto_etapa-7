# Generated by Django 5.1.3 on 2024-11-26 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="edit_access",
            field=models.CharField(
                choices=[
                    ("public", "Public"),
                    ("authenticated", "Authenticated"),
                    ("team", "Team"),
                    ("author", "Author"),
                ],
                default="author",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="read_access",
            field=models.CharField(
                choices=[
                    ("public", "Public"),
                    ("authenticated", "Authenticated"),
                    ("team", "Team"),
                    ("author", "Author"),
                ],
                default="public",
                max_length=20,
            ),
        ),
    ]
