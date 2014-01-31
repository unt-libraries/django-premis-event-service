from django.contrib import admin

from .models import Event, Agent, LinkObject


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "event_identifier",
        "event_date_time",
        "event_type",
        "link_objects_string",
        "linking_agent_identifier_value",
        "is_good",
    )
    search_fields = [
        "event_identifier",
    ]
    raw_id_fields = (
        "linking_objects",
    )


class AgentAdmin(admin.ModelAdmin):
    list_display = (
        "agent_identifier",
        "agent_name",
    )


class LinkObjectAdmin(admin.ModelAdmin):
    pass


admin.site.register(Event, EventAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(LinkObject, LinkObjectAdmin)
