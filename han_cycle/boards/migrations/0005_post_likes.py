# Generated by Django 5.0.7 on 2024-07-24 12:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boards", "0004_alter_post_region"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="likes",
            field=models.ManyToManyField(
                default=0, related_name="liked_posts", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
