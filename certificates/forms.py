from django import forms
from dashboard.models import HonorableCertificate
import uuid

class CertificateIssueForm(forms.ModelForm):
    class Meta:
        model = HonorableCertificate
        fields = ['recipient_name', 'recipient_email', 'recipient_phone', 'project_title', 'primary_category', 'secondary_category', 'reason', 'study_file']
        labels = {
            'recipient_name': 'Candidate Name',
            'recipient_email': 'Email Address',
            'recipient_phone': 'Phone Number',
            'project_title': 'Project Title',
            'primary_category': 'Primary Category',
            'secondary_category': 'Secondary Category',
            'reason': 'Project Description / Reason',
            'study_file': 'Upload Study File (PDF / Document)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from dashboard.models import Category
        primary_field = self.fields.get('primary_category')
        if isinstance(primary_field, forms.ModelChoiceField):
            primary_field.queryset = Category.objects.filter(category_type='HONORS', parent=None)
            primary_field.empty_label = "Select Primary Category"
        secondary_field = self.fields.get('secondary_category')
        if isinstance(secondary_field, forms.ModelChoiceField):
            secondary_field.queryset = Category.objects.filter(category_type='HONORS').exclude(parent=None)
            secondary_field.empty_label = "Select Secondary Category"
    
    # Auto-generate a unique short code for the certificate verification if blank
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.certificate_code:
            import uuid
            instance.certificate_code = str(uuid.uuid4()).split('-')[0].upper() # Short unique token (e.g., A1B2C3D4)
        if commit:
            instance.save()
        return instance