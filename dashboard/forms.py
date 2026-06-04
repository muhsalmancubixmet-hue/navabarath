from django import forms
from django.contrib.auth.models import User
from .models import HeroSection, Testimonial, Campaign, FAQ, StudySubmission, Category

class HeroEditForm(forms.ModelForm):
    class Meta:
        model = HeroSection
        fields = ['title', 'subtitle', 'image']

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class CampaignForm(forms.ModelForm):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True}),
        required=False,
        label="Project Gallery Images"
    )

    class Meta:
        model = Campaign
        fields = ['name', 'description', 'primary_category', 'secondary_category', 'start_date', 'end_date', 'is_active', 'image']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['primary_category'].queryset = Category.objects.filter(category_type='CAMPAIGN', parent=None)
        self.fields['secondary_category'].queryset = Category.objects.filter(category_type='CAMPAIGN').exclude(parent=None)
        self.fields['primary_category'].empty_label = "Select Primary Category"
        self.fields['secondary_category'].empty_label = "Select Secondary Category"

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer']

class StaffCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))

    has_content_info = forms.BooleanField(required=False, initial=True, label="Access Content & Info")
    has_campaigns = forms.BooleanField(required=False, initial=True, label="Access Campaigns")
    has_honors_program = forms.BooleanField(required=False, initial=True, label="Access Honors Program")
    has_system_security = forms.BooleanField(required=False, initial=True, label="Access System & Security")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = True
        if commit:
            user.save()
            from .models import StaffPermission
            StaffPermission.objects.update_or_create(
                user=user,
                defaults={
                    'has_content_info': self.cleaned_data.get('has_content_info', False),
                    'has_campaigns': self.cleaned_data.get('has_campaigns', False),
                    'has_honors_program': self.cleaned_data.get('has_honors_program', False),
                    'has_system_security': self.cleaned_data.get('has_system_security', False),
                }
            )
        return user


class StudySubmissionForm(forms.ModelForm):
    class Meta:
        model = StudySubmission
        fields = ['student_name', 'email', 'title', 'content']