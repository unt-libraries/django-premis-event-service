# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('premis_event_service', '0001_initial'),
    ]

    operations = [
        # Add ordinal column.
        migrations.RunSQL(
            'alter table premis_event_service_event add column ordinal int not null',
            'alter table premis_event_service_event drop column ordinal',
            state_operations = [
                migrations.AddField(
                    model_name='event',
                    name='ordinal',
                    field=models.IntegerField(
                        default=None,
                        help_text=b'Read-only field used for paging.',
                        editable=False,
                        null=True
                    ),
                    preserve_default=False                
                )
            ]
        ),
        # Create variable and ordinal for set existing rows, ordered by date added.
        migrations.RunSQL(
            'set @ord = 0; update premis_event_service_event set ordinal = (@ord:=@ord+1) '
            'order by event_added asc, event_identifier desc;'
        ),
        # Add index to ordinal column.
        migrations.RunSQL(
            'alter table premis_event_service_event add index '
            'premis_event_service_event_ordinal_idx (ordinal);',
            'alter table premis_event_service_event drop index '
            'premis_event_service_event_ordinal_idx;'
        ),
        # Make ordinal column auto_increment.
        migrations.RunSQL(
            'alter table premis_event_service_event change ordinal ordinal int not '
            'null auto_increment;',
            'alter table premis_event_service_event change ordinal ordinal int not '
            'null;'
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_identifier',
            field=models.CharField(
                help_text=b'Short identifier for agent to be used in url.',
                unique=True,
                max_length=255,
                db_index=True
            ),
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_name',
            field=models.CharField(
                help_text=b'Name of agent.',
                max_length=255
            ),
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_note',
            field=models.TextField(
                help_text=b'Optional note about agent.',
                blank=True
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_added',
            field=models.DateTimeField(
                help_text=b'Date/Time event was added to system.',
                auto_now=True,
                db_index=True
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_date_time',
            field=models.DateTimeField(
                help_text=b'Date/Time event was completed.',
                db_index=True
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_identifier_type',
            field=models.CharField(
                help_text=b'The categorization of the nature of the identifier used.',
                max_length=255
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.CharField(
                help_text=b'A categorization of the nature of the event use controlled vocabulary.',
                max_length=255,
                db_index=True),
        ),
        migrations.AlterField(
            model_name='linkobject',
            name='object_identifier',
            field=models.CharField(
                help_text=b'Unique identifier for this object.',
                max_length=255,
                serialize=False,
                primary_key=True
            ),
        ),
        migrations.AlterField(
            model_name='linkobject',
            name='object_role',
            field=models.CharField(
                help_text=b'A high-level characterization of the role of the object.',
                max_length=255,
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='linkobject',
            name='object_type',
            field=models.CharField(
                help_text=b'High-level characterization of the type of object identifier.',
                max_length=255
            ),
        ),
    ]
