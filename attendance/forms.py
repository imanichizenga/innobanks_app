from django import forms
from django.utils import timezone


class ManualAttendanceFilterForm(forms.Form):
    VIEW_CHOICES = (
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    )
    STATUS_CHOICES = (
        ("", "All statuses"),
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    )

    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    view = forms.ChoiceField(
        choices=VIEW_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by name or identifier"}
        ),
    )
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    from_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
    )
    to_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
    )
    arrived_after = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
    )
    late_only = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))

    def clean_date(self):
        return self.cleaned_data.get("date") or timezone.localdate()

    def clean_view(self):
        return self.cleaned_data.get("view") or "daily"

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            self.add_error("date_to", "Date To must be after Date From.")

        from_time = cleaned_data.get("from_time")
        to_time = cleaned_data.get("to_time")
        if from_time and to_time and from_time > to_time:
            self.add_error("to_time", "To Time must be later than From Time.")

        return cleaned_data
