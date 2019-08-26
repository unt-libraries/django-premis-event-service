# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-08-20 17:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('premis_event_service', '0002_add_event_ordinal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='agent_identifier',
            field=models.CharField(db_index=True, help_text=b'Short identifier for agent to be used in url.', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_name',
            field=models.CharField(help_text=b'Name of agent.', max_length=255),
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_note',
            field=models.TextField(blank=True, help_text=b'Optional note about agent.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_added',
            field=models.DateTimeField(auto_now=True, db_index=True, help_text=b'Date/Time event was added to system.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_date_time',
            field=models.DateTimeField(db_index=True, help_text=b'Date/Time event was completed.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_identifier_type',
            field=models.CharField(help_text=b'The categorization of the nature of the identifier used.', max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.CharField(db_index=True, help_text=b'A categorization of the nature of the event use controlled vocabulary.', max_length=255),
        ),
        migrations.AlterField(
            model_name='linkobject',
            name='object_identifier',
            field=models.CharField(help_text=b'Unique identifier for this object.', max_length=255, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='linkobject',
            name='object_role',
            field=models.CharField(help_text=b'A high-level characterization of the role of the object.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='linkobject',
            name='object_type',
            field=models.CharField(help_text=b'High-level characterization of the type of object             identifier.', max_length=255),
        ),
    ]