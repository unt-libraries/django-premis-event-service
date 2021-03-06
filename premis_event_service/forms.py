from django import forms

from premis_event_service import settings

OUTCOME_CHOICES = settings.EVENT_OUTCOME_CHOICES
EVENT_TYPE_CHOICES = settings.EVENT_TYPE_CHOICES


class EventSearchForm(forms.Form):
    event_outcome = forms.ChoiceField(
        widget=forms.Select(attrs={'id': 'prependedInput', 'class': 'input-small'}),
        choices=OUTCOME_CHOICES,
        required=False)

    event_type = forms.ChoiceField(
        widget=forms.Select(attrs={'id': 'prependedInput', 'class': 'input-medium'}),
        choices=EVENT_TYPE_CHOICES,
        required=False)

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'id': 'startdatepicker', 'placeholder': 'Start Date', 'class': 'input-small'}),  # noqa
        required=False)

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'id': 'enddatepicker', 'placeholder': 'End Date', 'class': 'input-small'}),  # noqa
        required=False)

    linked_object_id = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Linked Object ID', 'class': 'input-medium'}),
        max_length=64,
        required=False)
