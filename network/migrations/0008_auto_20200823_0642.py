# Generated by Django 3.1 on 2020-08-23 06:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0007_auto_20200820_1152'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='posts',
            options={'ordering': ['-time_posted']},
        ),
    ]
