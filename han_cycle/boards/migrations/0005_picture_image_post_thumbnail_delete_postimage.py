# Generated by Django 5.0.7 on 2024-07-18 06:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boards", "0004_postimage"),
    ]

    operations = [
        migrations.CreateModel(
            name="Picture",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("img", models.ImageField(blank=True, upload_to="")),
            ],
        ),
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="images/")),
                ("is_representative", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "board",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="boards.post",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="post",
            name="thumbnail",
            field=models.ManyToManyField(to="boards.image"),
        ),
        migrations.DeleteModel(
            name="PostImage",
        ),
    ]
