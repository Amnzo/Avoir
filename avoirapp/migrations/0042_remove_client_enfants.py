# Generated by Django 4.2.9 on 2024-10-14 14:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avoirapp', '0041_client_enfants_alter_avoir_facture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='enfants',
        ),
    ]