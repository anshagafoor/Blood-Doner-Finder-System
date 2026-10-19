from django import forms
from .models import DonorProfile, DonationCertificate
from accounts.constants import BLOOD_GROUPS, DISTRICTS


class DonationCertificateForm(forms.ModelForm):
    class Meta:
        model = DonationCertificate
        fields = ["certificate_file", "donation_date", "location", "units", "note"]
        widgets = {
            "donation_date": forms.DateInput(attrs={"type": "date"}),
            "note": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = (field.widget.attrs.get("class", "") + " form-input").strip()

    def clean_certificate_file(self):
        f = self.cleaned_data.get("certificate_file")
        if f:
            allowed = (".pdf", ".png", ".jpg", ".jpeg", ".webp")
            if not f.name.lower().endswith(allowed):
                raise forms.ValidationError("Upload a PDF or an image (png, jpg, jpeg, webp).")
            if f.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File too large (max 5 MB).")
        return f


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
