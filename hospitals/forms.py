from django import forms
from .models import BloodRequest, HospitalProfile


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ["patient_name", "blood_group", "units_needed", "district",
                  "urgency", "contact_number", "needed_by", "notes"]
        widgets = {
            "needed_by": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"


class HospitalProfileForm(forms.ModelForm):
    class Meta:
        model = HospitalProfile
        fields = ["hospital_name", "district", "license_number", "address"]
        widgets = {"address": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"
