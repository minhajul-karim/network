# Generated by Django 3.1 on 2020-08-19 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_follow'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follow',
            old_name='follows',
            new_name='followed',
        ),
    ]