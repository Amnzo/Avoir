# Generated by Django 4.2.9 on 2024-10-08 17:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('avoirapp', '0036_alter_avoir_facture'),
    ]

    operations = [
        migrations.AddField(
            model_name='retour',
            name='date_renvoi',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
