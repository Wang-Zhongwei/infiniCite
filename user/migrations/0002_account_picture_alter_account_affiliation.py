# Generated by Django 4.2.2 on 2023-07-21 05:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="picture",
            field=models.ImageField(blank=True, null=True, upload_to="media"),
        ),
        migrations.AlterField(
            model_name="account",
            name="affiliation",
            field=models.CharField(blank=True, default="", max_length=255, null=True),
        ),
    ]
