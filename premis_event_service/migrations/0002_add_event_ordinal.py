# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forward_sqlite(apps, schema_editor):
    cur = schema_editor.connection.cursor()
    cur.execute(
        """create table pesetmp (
            "ordinal" integer primary key,
            "event_identifier" varchar(64) NOT NULL UNIQUE,
            "event_identifier_type" varchar(255) NOT NULL, 
            "event_type" varchar(255) NOT NULL, 
            "event_date_time" datetime NOT NULL, 
            "event_added" datetime NOT NULL, "event_detail" text NOT NULL, 
            "event_outcome" varchar(255) NOT NULL, 
            "event_outcome_detail" text NOT NULL, 
            "linking_agent_identifier_type" varchar(255) NOT NULL, 
            "linking_agent_identifier_value" varchar(255) NOT NULL, 
            "linking_agent_role" varchar(255) NOT NULL
        );"""
    )
    cur.execute(
        """insert into pesetmp
            (ordinal, event_identifier, event_identifier_type, event_type, event_date_time,
            event_added, event_outcome, event_outcome_detail, linking_agent_identifier_type,
            linking_agent_identifier_value, linking_agent_role)
            select null, event_identifier, event_identifier_type, event_type, event_date_time,
            event_added, event_outcome, event_outcome_detail, linking_agent_identifier_type,
            linking_agent_identifier_value, linking_agent_role 
            from premis_event_service_event;"""
    )
    cur.execute(
        """drop table premis_event_service_event;"""
    )
    cur.execute(
        """create index "premis_event_service_event_1cd03614" 
        on "pesetmp" ("event_type");"""
    )
    cur.execute(
        """create index "premis_event_service_event_afe44630" 
        on "pesetmp" ("event_date_time");"""
    )
    cur.execute(
        """create index "premis_event_service_event_eefc032c" 
        on "pesetmp" ("event_added");"""
    )
    cur.execute(
        """create index "premis_event_service_event_d8893bd6" 
        on "pesetmp" ("event_outcome");"""
    )
    cur.execute(
        """create index "premis_event_service_event_854a1fa6" 
        on "pesetmp" ("linking_agent_identifier_value");"""
    )
    cur.execute(
        """alter table pesetmp rename to premis_event_service_event;"""
    )


def forward_mysql(apps, schema_editor):
    cur = schema_editor.connection.cursor()
    cur.execute(
        """lock tables 
        premis_event_service_event write,
        premis_event_service_event_linking_objects write,
        premis_event_service_linkobject write"""
    )
    cur.execute(
        """alter table premis_event_service_event drop primary key;"""
    )
    cur.execute(
        """alter table premis_event_service_event add unique(event_identifier);"""
    )
    cur.execute(
        """alter table premis_event_service_event add column 
        ordinal int not null primary key auto_increment first;
    """
    )
    cur.execute(
        """unlock tables"""
    )


def forward(apps, schema_editor):
    backend = schema_editor.connection.vendor
    if backend == 'sqlite':
        forward_sqlite(apps, schema_editor)
    else:
        forward_mysql(apps, schema_editor)


class Migration(migrations.Migration):

    dependencies = [
        ('premis_event_service', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward),
        migrations.RunSQL('select 1;', state_operations=[

            migrations.AddField(
                model_name='event',
                name='ordinal',
                field=models.AutoField(
                    primary_key=True
                ),
            ),
            migrations.AlterField(
                model_name='event',
                name='event_identifier',
                field=models.CharField(
                    help_text=(
                        b'Unique identifier for an event. '
                        'example: urn:uuid:12345678-1234-5678-1234-567812345678'
                    ),
                    unique=True,
                    max_length=64,
                    editable=False,
                    db_index=True
                ),
            ),
        ])
    ]
