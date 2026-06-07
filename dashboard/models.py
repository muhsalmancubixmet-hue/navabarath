from django.db import models
from django.conf import settings


class HeroSection(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.TextField()
    image = models.ImageField(upload_to='hero/')
    order = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id and not self.order:
            from django.db.models import Max
            max_order = HeroSection.objects.aggregate(Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)

class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    feedback = models.TextField()
    client_designation = models.CharField(max_length=100)
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.client_name

    def save(self, *args, **kwargs):
        if not self.id and not self.order:
            from django.db.models import Max
            max_order = Testimonial.objects.aggregate(Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)


class Participant(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('REFUNDED', 'Refunded'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, default="+91 9876543210")
    joined_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class Category(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ('CAMPAIGN', 'Campaign'),
        ('HONORS', 'Honors'),
    ]

    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES, default='CAMPAIGN')

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name


class Campaign(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    primary_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_campaigns')
    secondary_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='secondary_campaigns')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    participants = models.ManyToManyField(Participant, related_name='campaigns', blank=True)
    image = models.ImageField(upload_to='campaigns/', null=True, blank=True)

    def __str__(self):
        return self.name


class CampaignImage(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='campaigns/multiple/')

    def __str__(self):
        return f"Image for {self.campaign.name}"


class HonorableCertificate(models.Model):
    recipient_name = models.CharField(max_length=255)
    recipient_email = models.EmailField(null=True, blank=True)
    recipient_phone = models.CharField(max_length=15, null=True, blank=True)
    project_title = models.CharField(max_length=255, null=True, blank=True)
    primary_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_certificates')
    secondary_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='secondary_certificates')
    issue_date = models.DateField(auto_now_add=True)
    certificate_code = models.CharField(max_length=50, unique=True) # Unique ID for verification
    reason = models.TextField(help_text="Reason for the award")
    study_file = models.FileField(upload_to='certificates/studies/', null=True, blank=True)

    def __str__(self):
        return f"Certificate for {self.recipient_name}"
    

class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255) # e.g., "Updated Hero Section"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"{user_str} - {self.action} at {self.timestamp}"
    

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class StudySubmission(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    student_name = models.CharField(max_length=255)
    email = models.EmailField()
    title = models.CharField(max_length=255, verbose_name="Study Title")
    content = models.TextField(verbose_name="Study Details / Description")
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    certificate = models.OneToOneField(
        'HonorableCertificate', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='study_submission'
    )

    def __str__(self):
        return f"Submission by {self.student_name} - {self.title}"


class StaffPermission(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_permission')
    has_content_info = models.BooleanField(default=True, verbose_name="Content & Info")
    has_campaigns = models.BooleanField(default=True, verbose_name="Campaigns")
    has_honors_program = models.BooleanField(default=True, verbose_name="Honors Program")
    has_system_security = models.BooleanField(default=True, verbose_name="System & Security")

    def __str__(self):
        return f"Permissions for {self.user.username}"


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_staff_permission(sender, instance, created, **kwargs):
    if created:
        StaffPermission.objects.get_or_create(user=instance)
