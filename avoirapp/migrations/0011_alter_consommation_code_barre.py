# Generated by Django 4.2.9 on 2024-03-02 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avoirapp', '0010_avoir_user_consommation_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consommation',
            name='code_barre',
            field=models.CharField(max_length=25, null=True, verbose_name='EAN-13 Barcode'),
        ),
    ]
