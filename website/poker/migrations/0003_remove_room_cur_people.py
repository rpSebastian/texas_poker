# Generated by Django 2.2.5 on 2019-09-24 02:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('poker', '0002_room_person'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='cur_people',
        ),
    ]