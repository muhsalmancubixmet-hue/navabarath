from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory
from django.contrib.auth.models import User

# REST Framework Imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from certificates.forms import CertificateIssueForm
from dashboard.models import HonorableCertificate

from django.contrib import messages

import uuid

# Local App Imports
from .forms import HeroEditForm, CampaignForm, FAQForm, StaffCreationForm, StudySubmissionForm
from .utils import log_activity
from .models import HeroSection, ActivityLog, Participant, Testimonial, Campaign, FAQ, StudySubmission, Category, CampaignImage
from .serializers import HeroSerializer, TestimonialSerializer, CampaignSerializer, CertificateSerializer

from django.urls import reverse
from functools import wraps

def get_default_allowed_url(user):
    if user.is_superuser:
        return 'hero_list'
    if hasattr(user, 'staff_permission'):
        perm = user.staff_permission
        if perm.has_content_info:
            return 'hero_list'
        if perm.has_campaigns:
            return 'campaign_list'
        if perm.has_honors_program:
            return 'certificate_list'
        if perm.has_system_security:
            return 'staff_list'
    return 'hero_list'

def staff_permission_required(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            has_perm = False
            if hasattr(request.user, 'staff_permission'):
                has_perm = getattr(request.user.staff_permission, permission_name, False)
            else:
                has_perm = True
                
            if has_perm:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You do not have permission to access that section.")
                return redirect(get_default_allowed_url(request.user))
        return _wrapped_view
    return decorator


# --- Model Forms Setup ---

TestimonialForm = modelform_factory(
    Testimonial, 
    fields=['client_name', 'feedback', 'client_designation', 'image']
)


# --- Authentication Views ---

class CustomLoginView(LoginView):
    template_name = 'dashboard/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, "Logged into the dashboard")
        return response

    def get_success_url(self):
        return reverse(get_default_allowed_url(self.request.user))

# --- Dashboard Feature Views ---

@login_required
@staff_permission_required('has_content_info')
def hero_list(request):
    heroes = HeroSection.objects.all().order_by('order')
    return render(request, 'dashboard/hero_list.html', {
        'heroes': heroes
    })

@login_required
@staff_permission_required('has_content_info')
def hero_create(request):
    if request.method == "POST":
        form = HeroEditForm(request.POST, request.FILES)
        if form.is_valid():
            hero = form.save()
            log_activity(request.user, f"Created new Hero Section: {hero.title}")
            messages.success(request, f"Hero Section '{hero.title}' was successfully created!")
            return redirect('hero_list')
    else:
        form = HeroEditForm()
    
    return render(request, 'dashboard/edit_hero.html', {
        'form': form,
        'title': 'Create New Hero Section',
        'subtitle': 'Add a new landing page banner header and background visuals.',
        'button_text': 'Create Hero Section'
    })

@login_required
@staff_permission_required('has_content_info')
def hero_edit(request, pk):
    hero = get_object_or_404(HeroSection, pk=pk)
    if request.method == "POST":
        form = HeroEditForm(request.POST, request.FILES, instance=hero)
        if form.is_valid():
            hero = form.save()
            log_activity(request.user, f"Updated Hero Section details: {hero.title}")
            messages.success(request, f"Hero Section '{hero.title}' was successfully updated!")
            return redirect('hero_list')
    else:
        form = HeroEditForm(instance=hero)
    
    return render(request, 'dashboard/edit_hero.html', {
        'form': form,
        'title': 'Edit Hero Section',
        'subtitle': 'Modify this landing page banner header and background visuals.',
        'button_text': 'Save Changes'
    })

@login_required
@staff_permission_required('has_content_info')
def hero_delete(request, pk):
    hero = get_object_or_404(HeroSection, pk=pk)
    title = hero.title
    hero.delete()
    log_activity(request.user, f"Deleted Hero Section: {title}")
    messages.warning(request, f"Hero Section '{title}' was successfully deleted.")
    return redirect('hero_list')

@login_required
@staff_permission_required('has_content_info')
def hero_reorder(request):
    import json
    from django.http import JsonResponse
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_list = data.get('order', [])
            for item in order_list:
                hero_id = item.get('id')
                new_order = item.get('order')
                HeroSection.objects.filter(id=hero_id).update(order=new_order)
            log_activity(request.user, "Reordered landing page Hero Sections")
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)


@login_required
@staff_permission_required('has_system_security')
def activity_logs(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')
    return render(request, 'dashboard/activity_logs.html', {'logs': logs})


@login_required
@staff_permission_required('has_content_info')
def testimonial_list(request):
    testimonials = Testimonial.objects.all().order_by('order')
    return render(request, 'dashboard/testimonials.html', {'testimonials': testimonials})


@login_required
@staff_permission_required('has_content_info')
def testimonial_add(request):
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            testimonial = form.save()
            log_activity(request.user, f"Added testimonial for client: {testimonial.client_name}")
            messages.success(request, f"Testimonial for '{testimonial.client_name}' was successfully created!")
            return redirect('testimonial_list')
    else:
        form = TestimonialForm()
    return render(request, 'dashboard/edit_hero.html', {
        'form': form, 
        'title': 'Add New Testimonial',
        'subtitle': 'Publish a new client testimonial or quote onto the public showcase section.',
        'button_text': 'Publish Testimonial'
    })


@login_required
@staff_permission_required('has_content_info')
def testimonial_detail(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    return render(request, 'dashboard/testimonial_detail.html', {'testimonial': testimonial})


@login_required
@staff_permission_required('has_content_info')
def testimonial_edit(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            testimonial = form.save()
            log_activity(request.user, f"Updated testimonial details for client: {testimonial.client_name}")
            messages.success(request, f"Testimonial for '{testimonial.client_name}' was successfully updated!")
            return redirect('testimonial_detail', pk=testimonial.pk)
    else:
        form = TestimonialForm(instance=testimonial)
    return render(request, 'dashboard/edit_hero.html', {
        'form': form, 
        'title': 'Edit Testimonial',
        'subtitle': 'Modify this client testimonial, quote, or profile image.',
        'button_text': 'Save Testimonial'
    })


@login_required
@staff_permission_required('has_content_info')
def testimonial_delete(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    name = testimonial.client_name
    testimonial.delete()
    log_activity(request.user, f"Deleted testimonial for client: {name}")
    messages.warning(request, f"Testimonial for '{name}' was successfully deleted.")
    return redirect('testimonial_list')


@login_required
@staff_permission_required('has_content_info')
def testimonial_reorder(request):
    import json
    from django.http import JsonResponse
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_list = data.get('order', [])
            for item in order_list:
                t_id = item.get('id')
                new_order = item.get('order')
                Testimonial.objects.filter(id=t_id).update(order=new_order)
            log_activity(request.user, "Reordered landing page Testimonials")
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)


@login_required
@staff_permission_required('has_campaigns')
def campaign_list(request):
    campaigns = Campaign.objects.all().order_by('-start_date')

    search_query = request.GET.get('search', '')
    if search_query:
        campaigns = campaigns.filter(name__icontains=search_query) | campaigns.filter(description__icontains=search_query)

    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        campaigns = campaigns.filter(is_active=True)
    elif status_filter == 'paused':
        campaigns = campaigns.filter(is_active=False)

    # Categories for filters
    campaign_categories = Category.objects.filter(category_type='CAMPAIGN')
    primary_categories = campaign_categories.filter(parent=None).order_by('name')
    secondary_categories = campaign_categories.exclude(parent=None).order_by('name')

    primary_filter = request.GET.get('primary_category', '')
    if primary_filter:
        campaigns = campaigns.filter(primary_category_id=primary_filter)

    secondary_filter = request.GET.get('secondary_category', '')
    if secondary_filter:
        campaigns = campaigns.filter(secondary_category_id=secondary_filter)

    return render(request, 'dashboard/campaigns.html', {
        'campaigns': campaigns,
        'search_query': search_query,
        'status_filter': status_filter,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
        'primary_filter': primary_filter,
        'secondary_filter': secondary_filter,
    })

@login_required
@staff_permission_required('has_campaigns')
def campaign_add(request):
    if request.method == "POST":
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            campaign = form.save()
            
            # Save multiple uploaded images
            images = request.FILES.getlist('images')
            for img in images:
                CampaignImage.objects.create(campaign=campaign, image=img)
                
            log_activity(request.user, f"Created new campaign: {campaign.name}")
            messages.success(request, f"Campaign '{campaign.name}' created successfully!")
            return redirect('campaign_list')
    else:
        form = CampaignForm()
        
    primary_categories = Category.objects.filter(category_type='CAMPAIGN', parent=None).prefetch_related('subcategories')
    
    return render(request, 'dashboard/edit_campaign.html', {
        'form': form, 
        'primary_categories': primary_categories,
        'title': 'Create New Campaign',
        'subtitle': 'Launch a new campaign, assign primary/secondary categories, and upload files.',
        'button_text': 'Create Campaign'
    })


@login_required
@staff_permission_required('has_campaigns')
def campaign_edit(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == "POST":
        form = CampaignForm(request.POST, request.FILES, instance=campaign)
        if form.is_valid():
            campaign = form.save()
            
            # Save newly uploaded multiple images
            images = request.FILES.getlist('images')
            for img in images:
                CampaignImage.objects.create(campaign=campaign, image=img)
                
            # Handle deletion of existing images
            delete_images = request.POST.getlist('delete_images')
            if delete_images:
                CampaignImage.objects.filter(id__in=delete_images, campaign=campaign).delete()
                
            log_activity(request.user, f"Updated campaign details: {campaign.name}")
            messages.success(request, f"Campaign '{campaign.name}' details updated successfully!")
            return redirect('campaign_detail', pk=campaign.pk)
    else:
        form = CampaignForm(instance=campaign)
        
    primary_categories = Category.objects.filter(category_type='CAMPAIGN', parent=None).prefetch_related('subcategories')
    
    return render(request, 'dashboard/edit_campaign.html', {
        'form': form,
        'campaign': campaign,
        'primary_categories': primary_categories,
        'title': 'Edit Campaign',
        'subtitle': 'Modify campaign information, category hierarchy, and gallery images.',
        'button_text': 'Save Campaign Details'
    })


@login_required
@staff_permission_required('has_campaigns')
def campaign_delete(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    name = campaign.name
    campaign.delete()
    log_activity(request.user, f"Deleted campaign: {name}")
    messages.warning(request, f"Campaign '{name}' was successfully deleted.")
    return redirect('campaign_list')


@login_required
@staff_permission_required('has_campaigns')
def category_list(request):
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add_primary':
            name = request.POST.get('name')
            if name:
                Category.objects.create(name=name, category_type='CAMPAIGN')
                log_activity(request.user, f"Created primary category: {name}")
                messages.success(request, f"Primary Category '{name}' created successfully!")
            else:
                messages.error(request, "Primary Category name cannot be empty.")
        elif action == 'add_secondary':
            name = request.POST.get('name')
            parent_id = request.POST.get('parent_id')
            if name and parent_id:
                parent = get_object_or_404(Category, id=parent_id)
                Category.objects.create(name=name, parent=parent, category_type='CAMPAIGN')
                log_activity(request.user, f"Created secondary category: {name} under {parent.name}")
                messages.success(request, f"Secondary Category '{name}' created under '{parent.name}'!")
            else:
                messages.error(request, "Name and Primary Category must be selected.")
        return redirect('category_list')

    # GET request
    primary_categories = Category.objects.filter(category_type='CAMPAIGN', parent=None).prefetch_related('subcategories').order_by('name')
    return render(request, 'dashboard/categories.html', {
        'primary_categories': primary_categories,
        'title': 'Manage Categories',
        'subtitle': 'Define and manage primary and secondary project categories.'
    })


@login_required
@staff_permission_required('has_honors_program')
def honors_category_list(request):
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add_primary':
            name = request.POST.get('name')
            if name:
                Category.objects.create(name=name, category_type='HONORS')
                log_activity(request.user, f"Created primary honors category: {name}")
                messages.success(request, f"Primary Honors Category '{name}' created successfully!")
            else:
                messages.error(request, "Primary Honors Category name cannot be empty.")
        elif action == 'add_secondary':
            name = request.POST.get('name')
            parent_id = request.POST.get('parent_id')
            if name and parent_id:
                parent = get_object_or_404(Category, id=parent_id, category_type='HONORS')
                Category.objects.create(name=name, parent=parent, category_type='HONORS')
                log_activity(request.user, f"Created secondary honors category: {name} under {parent.name}")
                messages.success(request, f"Secondary Honors Category '{name}' created under '{parent.name}'!")
            else:
                messages.error(request, "Name and Primary Honors Category must be selected.")
        return redirect('honors_category_list')

    # GET request
    primary_categories = Category.objects.filter(category_type='HONORS', parent=None).prefetch_related('subcategories').order_by('name')
    return render(request, 'dashboard/honors_categories.html', {
        'primary_categories': primary_categories,
        'title': 'Manage Honors Categories',
        'subtitle': 'Define and manage primary and secondary honors categories.'
    })


@login_required
@staff_permission_required('has_honors_program')
def certificate_list(request):
    # Certificates Query
    certs = HonorableCertificate.objects.all().order_by('-issue_date')
    search_query = request.GET.get('search', '')
    
    if search_query:
        certs = certs.filter(recipient_name__icontains=search_query) | \
                certs.filter(certificate_code__icontains=search_query) | \
                certs.filter(reason__icontains=search_query)
                
    start_date = request.GET.get('start_date', '')
    if start_date:
        certs = certs.filter(issue_date__gte=start_date)
        
    end_date = request.GET.get('end_date', '')
    if end_date:
        certs = certs.filter(issue_date__lte=end_date)

    # Categories for filters
    honors_categories = Category.objects.filter(category_type='HONORS')
    primary_categories = honors_categories.filter(parent=None).order_by('name')
    secondary_categories = honors_categories.exclude(parent=None).order_by('name')

    primary_filter = request.GET.get('primary_category', '')
    if primary_filter:
        certs = certs.filter(primary_category_id=primary_filter)

    secondary_filter = request.GET.get('secondary_category', '')
    if secondary_filter:
        certs = certs.filter(secondary_category_id=secondary_filter)
                          
    return render(request, 'dashboard/certificates.html', {
        'certs': certs,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
        'primary_filter': primary_filter,
        'secondary_filter': secondary_filter,
        'certs_count': HonorableCertificate.objects.count()
    })

@login_required
@staff_permission_required('has_honors_program')
def certificate_add(request):
    if request.method == "POST":
        form = CertificateIssueForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save()
            log_activity(request.user, f"Created new project/certificate for: {cert.recipient_name} (Code: {cert.certificate_code})")
            messages.success(request, f"Project for '{cert.recipient_name}' created successfully!")
            return redirect('certificate_list')
    else:
        form = CertificateIssueForm()
        
    primary_categories = Category.objects.filter(category_type='HONORS', parent=None).prefetch_related('subcategories')
    
    return render(request, 'dashboard/edit_project.html', {
        'form': form, 
        'primary_categories': primary_categories,
        'title': 'Create New Project',
        'subtitle': 'Enter the candidate details, project description, and upload the study file.',
        'button_text': 'Create Project'
    })


@login_required
@staff_permission_required('has_honors_program')
def certificate_detail(request, pk):
    cert = get_object_or_404(HonorableCertificate, pk=pk)
    is_pdf = False
    is_docx = False
    is_image = False
    if cert.study_file:
        name_lower = cert.study_file.name.lower()
        is_pdf = name_lower.endswith('.pdf')
        is_docx = name_lower.endswith('.docx')
        is_image = any(name_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif'])
        
    return render(request, 'dashboard/certificate_detail.html', {
        'cert': cert,
        'is_pdf': is_pdf,
        'is_docx': is_docx,
        'is_image': is_image
    })


@login_required
@staff_permission_required('has_honors_program')
def certificate_edit(request, pk):
    cert = get_object_or_404(HonorableCertificate, pk=pk)
    if request.method == "POST":
        form = CertificateIssueForm(request.POST, request.FILES, instance=cert)
        if form.is_valid():
            cert = form.save()
            log_activity(request.user, f"Updated project/certificate details for: {cert.recipient_name}")
            messages.success(request, f"Project details for '{cert.recipient_name}' updated successfully!")
            return redirect('certificate_detail', pk=cert.pk)
    else:
        form = CertificateIssueForm(instance=cert)
        
    primary_categories = Category.objects.filter(category_type='HONORS', parent=None).prefetch_related('subcategories')
    
    return render(request, 'dashboard/edit_project.html', {
        'form': form, 
        'cert': cert,
        'primary_categories': primary_categories,
        'title': 'Edit Project Details',
        'subtitle': 'Update candidate information, project details, or replace the study file.',
        'button_text': 'Save Changes'
    })


@login_required
@staff_permission_required('has_campaigns')
def campaign_detail(request, pk):
    from django.db.models import Q
    from django.core.paginator import Paginator

    campaign = get_object_or_404(Campaign, pk=pk)
    participants = campaign.participants.all().order_by('name')
    
    search_participants = request.GET.get('search_participants', '')
    if search_participants:
        participants = participants.filter(
            Q(name__icontains=search_participants) | 
            Q(email__icontains=search_participants)
        )
        
    paginator = Paginator(participants, 200)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/campaign_detail.html', {
        'campaign': campaign, 
        'participants': page_obj,
        'page_obj': page_obj,
        'search_participants': search_participants
    })


@login_required
@staff_permission_required('has_campaigns')
def campaign_export_participants(request, pk):
    import csv
    from django.http import HttpResponse
    from django.db.models import Q
    
    campaign = get_object_or_404(Campaign, pk=pk)
    participants = campaign.participants.all().order_by('name')
    
    search_participants = request.GET.get('search_participants', '')
    if search_participants:
        participants = participants.filter(
            Q(name__icontains=search_participants) | 
            Q(email__icontains=search_participants)
        )
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="participants_{campaign.name.replace(" ", "_")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Joined At', 'Payment Status', 'Amount Paid'])
    
    for participant in participants:
        writer.writerow([
            participant.name,
            participant.email,
            participant.phone,
            participant.joined_at.strftime('%Y-%m-%d %H:%M:%S') if participant.joined_at else '',
            participant.payment_status,
            participant.amount_paid
        ])
        
    return response

@login_required
@staff_permission_required('has_campaigns')
def participant_profile(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    past_campaigns = participant.campaigns.all()  # type: ignore
    return render(request, 'dashboard/participant_profile.html', {
        'participant': participant,
        'past_campaigns': past_campaigns
    })


@login_required
@staff_permission_required('has_content_info')
def faq_list(request):
    faqs = FAQ.objects.all().order_by('-created_at')
    search_query = request.GET.get('search', '')
    if search_query:
        faqs = faqs.filter(question__icontains=search_query) | faqs.filter(answer__icontains=search_query)
    return render(request, 'dashboard/faqs.html', {
        'faqs': faqs,
        'search_query': search_query
    })

@login_required
@staff_permission_required('has_content_info')
def faq_add(request):
    if request.method == "POST":
        form = FAQForm(request.POST)
        if form.is_valid():
            faq = form.save()
            log_activity(request.user, f"Created new FAQ: {faq.question}")
            return redirect('faq_list')
    else:
        form = FAQForm()
    return render(request, 'dashboard/edit_hero.html', {
        'form': form, 
        'title': 'Add New FAQ',
        'subtitle': 'Provide a new frequently asked question and answer for public reference.',
        'button_text': 'Add FAQ'
    })

@login_required
@staff_permission_required('has_content_info')
def faq_edit(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == "POST":
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            faq = form.save()
            log_activity(request.user, f"Updated FAQ: {faq.question}")
            return redirect('faq_list')
    else:
        form = FAQForm(instance=faq)
    return render(request, 'dashboard/edit_hero.html', {
        'form': form, 
        'title': 'Edit FAQ',
        'subtitle': 'Update the question or answer details of an existing FAQ.',
        'button_text': 'Save FAQ'
    })

@login_required
@staff_permission_required('has_content_info')
def faq_delete(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    question = faq.question
    faq.delete()
    log_activity(request.user, f"Deleted FAQ: {question}")
    return redirect('faq_list')

@login_required
@staff_permission_required('has_system_security')
def staff_list(request):
    staffs = User.objects.filter(is_staff=True).order_by('-date_joined')
    search_query = request.GET.get('search', '')
    if search_query:
        staffs = staffs.filter(username__icontains=search_query) | staffs.filter(first_name__icontains=search_query) | staffs.filter(last_name__icontains=search_query) | staffs.filter(email__icontains=search_query)
    return render(request, 'dashboard/staff_list.html', {
        'staffs': staffs,
        'search_query': search_query
    })

@login_required
@staff_permission_required('has_system_security')
def staff_create(request):
    if request.method == "POST":
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_activity(request.user, f"Created new staff user: {user.username}")
            messages.success(request, f"Staff account for {user.username} was successfully created!")
            return redirect('staff_list')
    else:
        form = StaffCreationForm()
    return render(request, 'dashboard/edit_hero.html', {
        'form': form, 
        'title': 'Create New Staff Member',
        'subtitle': 'Register a new administrative user with access to the Navabharath dashboard.',
        'button_text': 'Create Account'
    })


# --- Public Study Submission & Certificate Verification Views (No Login Required) ---

def public_submit_study(request):
    if request.method == "POST":
        form = StudySubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save()
            log_activity(None, f"Public study submission created by {submission.student_name}: {submission.title}")
            messages.success(request, "Your study has been successfully submitted for review! You will receive your certificate once approved.")
            return redirect('public_submit_study')
    else:
        form = StudySubmissionForm()
    return render(request, 'dashboard/public_submit_study.html', {
        'form': form
    })


def public_view_certificate(request, code):
    cert = get_object_or_404(HonorableCertificate, certificate_code=code.upper())
    submission = getattr(cert, 'study_submission', None)
    return render(request, 'dashboard/public_view_certificate.html', {
        'cert': cert,
        'submission': submission
    })


# --- Private Study Submissions Management (Dashboard Admins) ---


@login_required
@staff_permission_required('has_honors_program')
def study_submission_detail(request, pk):
    submission = get_object_or_404(StudySubmission, pk=pk)
    return render(request, 'dashboard/submission_detail.html', {
        'submission': submission
    })


@login_required
@staff_permission_required('has_honors_program')
def study_submission_approve(request, pk):
    submission = get_object_or_404(StudySubmission, pk=pk)
    if submission.status == 'PENDING':
        code = str(uuid.uuid4()).split('-')[0].upper()
        while HonorableCertificate.objects.filter(certificate_code=code).exists():
            code = str(uuid.uuid4()).split('-')[0].upper()
            
        cert = HonorableCertificate.objects.create(
            recipient_name=submission.student_name,
            certificate_code=code,
            reason=f"Honor awarded for the study: {submission.title}"
        )
        submission.certificate = cert
        submission.status = 'APPROVED'
        submission.save()
        log_activity(request.user, f"Approved study submission by {submission.student_name} and generated certificate {code}")
        messages.success(request, f"Successfully approved submission and generated Certificate code: {code}")
    else:
        messages.error(request, "This submission has already been processed.")
    return redirect('study_submission_detail', pk=pk)


@login_required
@staff_permission_required('has_honors_program')
def study_submission_reject(request, pk):
    submission = get_object_or_404(StudySubmission, pk=pk)
    if submission.status == 'PENDING':
        submission.status = 'REJECTED'
        submission.save()
        log_activity(request.user, f"Rejected study submission by {submission.student_name}")
        messages.warning(request, f"Successfully rejected study submission by {submission.student_name}.")
    else:
        messages.error(request, "This submission has already been processed.")
    return redirect('study_submission_detail', pk=pk)


# --- Public REST API Endpoints ---

@api_view(['GET'])
@permission_classes([AllowAny]) 
def public_landing_data(request):
    hero = HeroSection.objects.first()
    testimonials = Testimonial.objects.all()
    campaigns = Campaign.objects.filter(is_active=True)
    
    return Response({
        "hero": HeroSerializer(hero).data if hero else {},
        "testimonials": TestimonialSerializer(testimonials, many=True).data,
        "active_campaigns": CampaignSerializer(campaigns, many=True).data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_certificate_api(request, code):
    try:
        cert = HonorableCertificate.objects.get(certificate_code=code.upper())
        return Response({"valid": True, "data": CertificateSerializer(cert).data}, status=200)
    except HonorableCertificate.DoesNotExist:
        return Response({"valid": False, "message": "Invalid Certificate Verification Code"}, status=404)


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')