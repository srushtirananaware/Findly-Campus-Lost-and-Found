
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Report, Message, Claim, ReportFlag

class SignupForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=50, label="First name")
    invite_code = forms.CharField(max_length=80, required=False, label="Campus invite code")

    class Meta:
        model = User
        fields = ("first_name", "username", "email", "password1", "password2", "invite_code")

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        domain = getattr(settings, "COLLEGE_EMAIL_DOMAIN", "college.edu").lower().strip()
        if not domain or not email.endswith("@" + domain):
            raise forms.ValidationError(f"Use your college email address ending in @{domain}.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_invite_code(self):
        entered = self.cleaned_data.get("invite_code", "").strip()
        required = getattr(settings, "COLLEGE_INVITE_CODE", "")
        if required and entered != required:
            raise forms.ValidationError("That campus invite code is not valid.")
        return entered

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        if commit:
            user.save()
        return user


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["kind", "title", "description", "category", "location", "item_date", "photo"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Distinctive details help verify a match. Avoid posting ID numbers or private information."}),
            "item_date": forms.DateInput(attrs={"type": "date"}),
            "location": forms.TextInput(attrs={"placeholder": "e.g. Main library, canteen, Block B"}),
            "title": forms.TextInput(attrs={"placeholder": "e.g. Blue water bottle"}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo:
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image must be 5 MB or smaller.")
            if photo.content_type not in ["image/jpeg", "image/png", "image/webp"]:
                raise forms.ValidationError("Upload a JPG, PNG or WEBP image.")
        return photo


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["body"]
        labels = {"body": "Your message"}
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Share a detail that helps verify the item. Keep personal information private."})}


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ["note"]
        labels = {"note": "How can you verify this item is yours?"}
        widgets = {"note": forms.Textarea(attrs={"rows": 3, "placeholder": "Mention a distinctive detail that isn't visible in the public listing."})}


class FlagForm(forms.ModelForm):
    class Meta:
        model = ReportFlag
        fields = ["reason"]
        labels = {"reason": "Why should staff review this report?"}
