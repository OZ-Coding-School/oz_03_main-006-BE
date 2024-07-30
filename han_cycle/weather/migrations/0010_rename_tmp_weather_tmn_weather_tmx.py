# Generated by Django 4.2.14 on 2024-07-30 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("weather", "0009_rename_t1h_weather_tmp"),
    ]

    operations = [
        migrations.RenameField(
            model_name="weather",
            old_name="TMP",
            new_name="TMN",
        ),
        migrations.AddField(
            model_name="weather",
            name="TMX",
            field=models.FloatField(null=True),
        ),
    ]
