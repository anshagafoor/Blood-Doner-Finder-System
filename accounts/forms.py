# Robust validation for blood group format and values
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from .constants import BLOOD_GROUPS, DISTRICTS, GENDER_CHOICES


class StyledFormMixin:
    """Adds a consistent CSS class + placeholders to all fields."""
    def _style(self):
        for name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-input").strip()
            if not field.widget.attrs.get("placeholder"):
                field.widget.attrs["placeholder"] = field.label or name.title()


class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class BaseRegisterForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class DonorRegisterForm(BaseRegisterForm):
    full_name = forms.CharField(max_length=120)
    blood_group = forms.ChoiceField(choices=BLOOD_GROUPS)
    district = forms.ChoiceField(choices=DISTRICTS)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False)

    field_order = ["username", "full_name", "email", "phone", "blood_group",
                   "district", "gender", "date_of_birth", "address",
                   "password1", "password2"]


class HospitalRegisterForm(BaseRegisterForm):
    hospital_name = forms.CharField(max_length=150)
    district = forms.ChoiceField(choices=DISTRICTS)
    license_number = forms.CharField(max_length=60)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}))

    field_order = ["username", "hospital_name", "email", "phone", "district",
                   "license_number", "address", "password1", "password2"]


class OrganizationRegisterForm(BaseRegisterForm):
    org_name = forms.CharField(max_length=150)
    district = forms.ChoiceField(choices=DISTRICTS)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}))
    website = forms.URLField(required=False)

    field_order = ["username", "org_name", "email", "phone", "district",
                   "website", "address", "password1", "password2"]
