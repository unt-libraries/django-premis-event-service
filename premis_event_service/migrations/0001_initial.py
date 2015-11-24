# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('agent_identifier', models.CharField(help_text=b'Short identifier for agent to be used in url', unique=True, max_length=255, db_index=True)),
                ('agent_name', models.CharField(help_text=b'Name of agent', max_length=255)),
                ('agent_type', models.CharField(help_text=b'A high-level characterization of the type of agent.', max_length=13, choices=[(b'Personal', b'Personal'), (b'Organization', b'Organization'), (b'Event', b'Event'), (b'Software', b'Software')])),
                ('agent_note', models.TextField(help_text=b'Optional note about agent', blank=True)),
            ],
            options={
                'ordering': ['agent_name'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('event_identifier', models.CharField(help_text=b'Unique identifier for an event. example: urn:uuid:12345678-1234-5678-1234-567812345678', max_length=64, serialize=False, editable=False, primary_key=True)),
                ('event_identifier_type', models.CharField(help_text=b'The categorization of the nature of the identifier used', max_length=255)),
                ('event_type', models.CharField(help_text=b'A categorization of the nature of the event use controlled vocabulary', max_length=255, db_index=True)),
                ('event_date_time', models.DateTimeField(help_text=b'Date/Time event was completed', db_index=True)),
                ('event_added', models.DateTimeField(help_text=b'Date/Time event was added to system', auto_now=True, db_index=True)),
                ('event_detail', models.TextField(help_text=b'Additional information about the event.', blank=True)),
                ('event_outcome', models.CharField(help_text=b'A categorization of the overall result of the event in terms of success, partial success, or failure.', max_length=255, db_index=True)),
                ('event_outcome_detail', models.TextField(help_text=b'A non-coded detailed description of the result of the event.', blank=True)),
                ('linking_agent_identifier_type', models.CharField(help_text=b'A designation of the domain in which the linking agent identifier is unique.', max_length=255)),
                ('linking_agent_identifier_value', models.CharField(help_text=b'The value of the linking agent identifier.', max_length=255, db_index=True)),
                ('linking_agent_role', models.CharField(help_text=b'The role of the agent in relation to this event.', max_length=255)),
            ],
            options={
                'ordering': ['event_added'],
            },
        ),
        migrations.CreateModel(
            name='LinkObject',
            fields=[
                ('object_identifier', models.CharField(help_text=b'Unique identifier for this object', max_length=255, serialize=False, primary_key=True)),
                ('object_type', models.CharField(help_text=b'High-level characterization of the type of object             identifier', max_length=255)),
                ('object_role', models.CharField(help_text=b'A high-level characterization of the role of the object', max_length=255, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='linking_objects',
            field=models.ManyToManyField(to='premis_event_service.LinkObject'),
        ),
    ]
