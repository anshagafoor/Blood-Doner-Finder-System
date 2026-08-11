from django import forms
from .models import DonorProfile
from accounts.constants import BLOOD_GROUPS, DISTRICTS


class DonorProfileForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = ["full_name", "blood_group", "district", "gender",
                  "date_of_birth", "address", "is_available"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != "is_available":
                field.widget.attrs["class"] = "form-input"


class DonorSearchForm(forms.Form):
    blood_group = forms.ChoiceField(
        choices=[("", "Any blood group")] + BLOOD_GROUPS, required=False)
    district = forms.ChoiceField(
        choices=[("", "Any district")] + DISTRICTS, required=False)
    only_available = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["blood_group"].widget.attrs["class"] = "form-input"
        self.fields["district"].widget.attrs["class"] = "form-input"
