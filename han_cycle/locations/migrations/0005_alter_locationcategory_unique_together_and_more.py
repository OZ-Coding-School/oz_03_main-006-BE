# Generated by Django 4.2.14 on 2024-07-29 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0004_delete_categories_l_category_name_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="locationcategory",
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name="locationcategory",
            name="L_category",
        ),
        migrations.RemoveField(
            model_name="locationcategory",
            name="location",
        ),
        migrations.AddField(
            model_name="location",
            name="L_category",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name="L_Category",
        ),
        migrations.DeleteModel(
            name="LocationCategory",
        ),
    ]
