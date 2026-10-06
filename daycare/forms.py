from django import forms

from .models import Child, FeeRecord, Inquiry


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["parent_name", "child_name", "phone", "email", "child_age", "message"]
        widgets = {
            "parent_name": forms.TextInput(attrs={"placeholder": "Your full name", "autocomplete": "name"}),
            "child_name": forms.TextInput(attrs={"placeholder": "Child's name"}),
            "phone": forms.TextInput(attrs={"placeholder": "+255 ...", "autocomplete": "tel"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
            "child_age": forms.TextInput(attrs={"placeholder": "e.g. 3 years"}),
            "message": forms.Textarea(attrs={"placeholder": "Tell us what you would like to know", "rows": 4}),
        }


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = [
            "first_name", "last_name", "birth_date", "gender", "program", "parent_name",
            "parent_phone", "parent_email", "allergies", "enrolled_on", "status", "photo",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "enrolled_on": forms.DateInput(attrs={"type": "date"}),
            "allergies": forms.Textarea(attrs={"rows": 3}),
        }


class FeeRecordForm(forms.ModelForm):
    class Meta:
        model = FeeRecord
        fields = ["child", "billing_period", "due_date", "amount_due", "amount_paid"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}
