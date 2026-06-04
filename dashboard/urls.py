from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


from django.views.generic import RedirectView

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('hero/edit/', RedirectView.as_view(pattern_name='hero_list', permanent=False)),
    path('hero/', views.hero_list, name='hero_list'),
    path('hero/add/', views.hero_create, name='hero_create'),
    path('hero/<int:pk>/edit/', views.hero_edit, name='hero_edit'),
    path('hero/<int:pk>/delete/', views.hero_delete, name='hero_delete'),
    path('hero/reorder/', views.hero_reorder, name='hero_reorder'),
    path('logs/', views.activity_logs, name='activity_logs'), 
    path('testimonials/', views.testimonial_list, name='testimonial_list'),
    path('testimonials/add/', views.testimonial_add, name='testimonial_add'),
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/add/', views.campaign_add, name='campaign_add'),
    path('campaigns/<int:pk>/edit/', views.campaign_edit, name='campaign_edit'),
    path('campaigns/<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/honors/', views.honors_category_list, name='honors_category_list'),
    path('api/v1/public-data/', views.public_landing_data, name='public_api_data'),
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('certificates/add/', views.certificate_add, name='certificate_add'),
    path('certificates/<int:pk>/', views.certificate_detail, name='certificate_detail'),
    path('certificates/<int:pk>/edit/', views.certificate_edit, name='certificate_edit'),
    path('api/v1/verify-certificate/<str:code>/', views.verify_certificate_api, name='verify_cert_api'),
    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:pk>/export/', views.campaign_export_participants, name='campaign_export_participants'),
    path('participant/<int:pk>/', views.participant_profile, name='participant_profile'),
    
    # FAQs
    path('faqs/', views.faq_list, name='faq_list'),
    path('faqs/add/', views.faq_add, name='faq_add'),
    path('faqs/<int:pk>/edit/', views.faq_edit, name='faq_edit'),
    path('faqs/<int:pk>/delete/', views.faq_delete, name='faq_delete'),
    
    # Staff management
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/create/', views.staff_create, name='staff_create'),
    
    # Public Study Submission & Certificate Verification (No Auth)
    path('public/submit-study/', views.public_submit_study, name='public_submit_study'),
    path('public/certificate/<str:code>/', views.public_view_certificate, name='public_view_certificate'),
    
    # Backend Submissions
    path('submissions/<int:pk>/', views.study_submission_detail, name='study_submission_detail'),
    path('submissions/<int:pk>/approve/', views.study_submission_approve, name='study_submission_approve'),
    path('submissions/<int:pk>/reject/', views.study_submission_reject, name='study_submission_reject'),
]