# Generated by Django 2.2.4 on 2024-08-07 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HenaaApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='first_name',
            new_name='username',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_name',
        ),
    ]
