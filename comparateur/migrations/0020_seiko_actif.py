# Generated by Django 4.2.9 on 2024-05-23 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparateur', '0019_seiko_date_debut_remise_seiko_date_fin_remise_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='seiko',
            name='actif',
            field=models.BooleanField(default=True),
        ),
    ]
