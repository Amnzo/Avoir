# Generated by Django 4.2.9 on 2024-05-21 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparateur', '0017_rename_hsc_seiko_sunisc_remove_seiko_sunscc'),
    ]

    operations = [
        migrations.AddField(
            model_name='starvision',
            name='actif',
            field=models.BooleanField(default=True),
        ),
    ]