# Generated by Django 4.2.9 on 2024-05-15 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparateur', '0011_alter_exceldata_hc_alter_exceldata_hsc_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exceldata',
            name='HC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='HSC',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='ISC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='POLA_ISC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='POLA_UC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='RCC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='SCC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='SRB',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='SRBUV',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='SRC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='SRCUV',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='SUNHC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='SUNSCC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='SUNUC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='UC',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='prix',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='exceldata',
            name='remise',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]