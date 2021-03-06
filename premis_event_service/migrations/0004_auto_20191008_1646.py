# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-10-08 16:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('premis_event_service', '0003_auto_20190820_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='agent_identifier',
            field=models.CharField(db_index=True, help_text='Short identifier for agent to be used in url.', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_name',
            field=models.CharField(help_text='Name of agent.', max_length=255),
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_note',
            field=models.TextField(blank=True, help_text='Optional note about agent.'),
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_type',
            field=models.CharField(choices=[('Personal', 'Personal'), ('Organization', 'Organization'), ('Event', 'Event'), ('Software', 'Software')], help_text='A high-level characterization of the type of agent.', max_length=13),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_added',
            field=models.DateTimeField(auto_now=True, db_index=True, help_text='Date/Time event was added to system.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_date_time',
            field=models.DateTimeField(db_index=True, help_text='Date/Time event was completed.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_detail',
            field=models.TextField(blank=True, help_text='Additional information about the event.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_identifier_type',
            field=models.CharField(help_text='The categorization of the nature of the identifier used.', max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_outcome',
            field=models.CharField(db_index=True, help_text='A categorization of the overall result of the event in terms of success, partial success, or failure.', max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_outcome_detail',
            field=models.TextField(blank=True, help_text='A non-coded detailed description of the result of the event.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.CharField(db_index=True, help_text='A categorization of the nature of the event use controlled vocabulary.', max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='linking_agent_identifier_type',
            field=models.CharField(help_text='A designation of the domain in which the linking agent identifier is unique.', max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='linking_agent_identifier_value',
            field=models.CharField(db_index=True, help_text='The value of the linking agent identifier.', max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='linking_agent_role',
            field=models.CharField(help_text='The role of the agent in relation to this event.', max_length=255),
        ),
        migrations.AlterField(
            model_name='linkobject',
            name='object_identifier',
            field=models.CharField(help_text='Unique identifier for this object.', max_length=255, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='linkobject',
            name='object_role',
            field=models.CharField(help_text='A high-level characterization of the role of the object.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='linkobject',
            name='object_type',
            field=models.CharField(help_text='High-level characterization of the type of object             identifier.', max_length=255),
        ),
    ]
