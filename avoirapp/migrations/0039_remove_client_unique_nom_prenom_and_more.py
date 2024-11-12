# Generated by Django 4.2.9 on 2024-10-11 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avoirapp', '0038_client_enfants_ids_alter_client_nom_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='client',
            name='unique_nom_prenom',
        ),
        migrations.AddConstraint(
            model_name='client',
            constraint=models.UniqueConstraint(fields=('nom', 'prenom', 'datenaissance'), name='unique_nom_prenom'),
        ),
    ]