# Generated by Django 4.2.9 on 2024-04-01 08:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avoirapp', '0031_journeevente_ca_mois_journeevente_ca_mois_1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vente',
            old_name='date_vente',
            new_name='date',
        ),
    ]