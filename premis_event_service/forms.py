from django import forms

import settings

OUTCOME_CHOICES = settings.EVENT_OUTCOME_CHOICES
EVENT_TYPE_CHOICES = settings.EVENT_TYPE_CHOICES


class EventSearchForm(forms.Form):
    outcome = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'id': 'prependedInput',
                'class': 'input-small',
            }
        ),
        choices=OUTCOME_CHOICES,

    )
    event_type = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'id': 'prependedInput',
                'class': 'input-medium',
            }
        ),
        choices=EVENT_TYPE_CHOICES,
    )
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'id': 'startdatepicker',
                'placeholder': 'Start Date',
                'class': 'input-small',
            }
        )
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'id': 'enddatepicker',
                'placeholder': 'End Date',
                'class': 'input-small',
            }
        )
    )
    linked_object_id = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Linked Object ID',
                'class': 'input-medium',
            }
        ),
        max_length=20,
    )
