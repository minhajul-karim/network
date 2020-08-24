# Generated by Django 3.1 on 2020-08-24 05:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_auto_20200823_0642'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reactions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.posts')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='reactions',
            constraint=models.UniqueConstraint(fields=('user', 'liked'), name='unq_user_liked'),
        ),
    ]