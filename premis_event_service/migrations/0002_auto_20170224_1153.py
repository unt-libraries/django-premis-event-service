# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('premis_event_service', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='agent_identifier',
            field=models.CharField(help_text=b'Short identifier for agent to be used in url.', unique=True, max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_name',
            field=models.CharField(help_text=b'Name of agent.', max_length=255),
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_note',
            field=models.TextField(help_text=b'Optional note about agent.', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_added',
            field=models.DateTimeField(help_text=b'Date/Time event was added to system.', auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_date_time',
            field=models.DateTimeField(help_text=b'Date/Time event was completed.', db_index=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_identifier_type',
            field=models.CharField(help_text=b'The categorization of the nature of the identifier used.', max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.CharField(help_text=b'A categorization of the nature of the event use controlled vocabulary.', max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='linkobject',
            name='object_identifier',
            field=models.CharField(help_text=b'Unique identifier for this object.', max_length=255, serialize=False, primary_key=True),
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
        migrations.AlterIndexTogether(
            name='event',
            index_together=set([('event_added', 'event_identifier')]),
        ),
    ]
