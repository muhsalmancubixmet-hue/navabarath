from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from dashboard.models import Category, Campaign, CampaignImage
import datetime

class CategoryAndCampaignTestCase(TestCase):
    def setUp(self):
        # Create a user and log in
        self.user = User.objects.create_user(username='testadmin', password='testpassword', is_staff=True)
        self.client = Client()
        self.client.login(username='testadmin', password='testpassword')

    def test_category_hierarchy(self):
        # Create primary category
        primary = Category.objects.create(name="Donation")
        self.assertNil = self.assertIsNone(primary.parent)
        
        # Create secondary category
        secondary = Category.objects.create(name="Blood Donation", parent=primary)
        self.assertEqual(secondary.parent, primary)
        subcategories = getattr(primary, 'subcategories')
        self.assertIn(secondary, subcategories.all())

    def test_campaign_category_linkage(self):
        primary = Category.objects.create(name="Donation")
        secondary = Category.objects.create(name="Blood Donation", parent=primary)
        
        campaign = Campaign.objects.create(
            name="Blood Drive 2026",
            description="Give blood save lives",
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=5),
            primary_category=primary,
            secondary_category=secondary
        )
        
        self.assertEqual(campaign.primary_category, primary)
        self.assertEqual(campaign.secondary_category, secondary)

    def test_category_list_post_primary(self):
        # Post to create primary category
        url = reverse('category_list')
        response = self.client.post(url, {'action': 'add_primary', 'name': 'Environment'})
        self.assertEqual(response.status_code, 302) # Redirects to self
        
        primary_exists = Category.objects.filter(name='Environment', parent=None).exists()
        self.assertTrue(primary_exists)

    def test_category_list_post_secondary(self):
        primary = Category.objects.create(name="Environment")
        url = reverse('category_list')
        response = self.client.post(url, {
            'action': 'add_secondary',
            'name': 'Tree Planting',
            'parent_id': primary.id
        })
        self.assertEqual(response.status_code, 302)
        
        secondary_exists = Category.objects.filter(name='Tree Planting', parent=primary).exists()
        self.assertTrue(secondary_exists)

    def test_honors_category_hierarchy(self):
        primary = Category.objects.create(name="Honors Research", category_type='HONORS')
        secondary = Category.objects.create(name="Deep Learning Research", parent=primary, category_type='HONORS')
        self.assertEqual(secondary.parent, primary)
        self.assertEqual(secondary.category_type, 'HONORS')

    def test_honors_category_list_post_primary(self):
        url = reverse('honors_category_list')
        response = self.client.post(url, {'action': 'add_primary', 'name': 'Distinction'})
        self.assertEqual(response.status_code, 302)
        primary_exists = Category.objects.filter(name='Distinction', parent=None, category_type='HONORS').exists()
        self.assertTrue(primary_exists)

    def test_honors_category_list_post_secondary(self):
        primary = Category.objects.create(name="Distinction", category_type='HONORS')
        url = reverse('honors_category_list')
        response = self.client.post(url, {
            'action': 'add_secondary',
            'name': 'Gold Medal',
            'parent_id': primary.id
        })
        self.assertEqual(response.status_code, 302)
        secondary_exists = Category.objects.filter(name='Gold Medal', parent=primary, category_type='HONORS').exists()
        self.assertTrue(secondary_exists)

    def test_campaign_detail_participants_search_and_pagination(self):
        from dashboard.models import Participant
        # Create campaign
        campaign = Campaign.objects.create(
            name="Pagination Test Campaign",
            description="Testing participants lists",
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=1)
        )
        # Add 210 participants
        for i in range(210):
            p = Participant.objects.create(name=f"Participant {i}", email=f"p{i}@test.com")
            campaign.participants.add(p)

        url = reverse('campaign_detail', args=[campaign.id])
        
        # Test default page 1 (should show 200 participants)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['participants']), 200)
        
        # Test page 2 (should show 10 participants)
        response = self.client.get(url, {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['participants']), 10)

        # Test search filtering (should filter down to matching participants)
        response = self.client.get(url, {'search_participants': 'Participant 100'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['participants']), 1)

    def test_campaign_export_participants_csv(self):
        from dashboard.models import Participant
        campaign = Campaign.objects.create(
            name="Export Test Campaign",
            description="Testing participant export",
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=1)
        )
        p1 = Participant.objects.create(name="Alice", email="alice@test.com", phone="+1234567")
        p2 = Participant.objects.create(name="Bob", email="bob@test.com", phone="+9876543")
        campaign.participants.add(p1, p2)

        url = reverse('campaign_export_participants', args=[campaign.id])
        
        # Test export without filter
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode('utf-8')
        self.assertIn("Alice", content)
        self.assertIn("Bob", content)

        # Test export with search filter
        response = self.client.get(url, {'search_participants': 'Alice'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Alice", content)
        self.assertNotIn("Bob", content)

    def test_participant_profile_receipt_rendering(self):
        from dashboard.models import Participant
        participant = Participant.objects.create(
            name="John Doe", 
            email="john@test.com", 
            phone="123456789", 
            payment_status="PAID",
            amount_paid=1500.00
        )
        url = reverse('participant_profile', args=[participant.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paid (View Receipt)")
        self.assertContains(response, "john@test.com")

    def test_hero_crud_and_ordering(self):
        from dashboard.models import HeroSection
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create a dummy image
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9'
            b'\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02\x4c\x01\x00\x3b'
        )
        img1 = SimpleUploadedFile('small1.gif', small_gif, content_type='image/gif')
        img2 = SimpleUploadedFile('small2.gif', small_gif, content_type='image/gif')

        # Test Hero creation auto ordering
        hero1 = HeroSection.objects.create(title="Hero One", subtitle="Subtitle One", image=img1)
        self.assertEqual(hero1.order, 1)

        hero2 = HeroSection.objects.create(title="Hero Two", subtitle="Subtitle Two", image=img2)
        self.assertEqual(hero2.order, 2)

        # Test Listing
        list_url = reverse('hero_list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['heroes']), [hero1, hero2])

        # Test JSON Reordering
        reorder_url = reverse('hero_reorder')
        import json
        payload = {
            "order": [
                {"id": hero1.id, "order": 2},
                {"id": hero2.id, "order": 1}
            ]
        }
        reorder_response = self.client.post(
            reorder_url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        self.assertEqual(reorder_response.status_code, 200)

        # Refresh from database and check orders
        hero1.refresh_from_db()
        hero2.refresh_from_db()
        self.assertEqual(hero1.order, 2)
        self.assertEqual(hero2.order, 1)

        # Test public landing API gets the first (highest priority) hero (which is now hero2)
        public_api_url = reverse('public_api_data')
        api_response = self.client.get(public_api_url)
        self.assertEqual(api_response.status_code, 200)
        self.assertEqual(api_response.json()['hero']['title'], "Hero Two")

    def test_certificate_project_flow_with_upload(self):
        from dashboard.models import HonorableCertificate
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create categories
        primary = Category.objects.create(name="Education", category_type='HONORS')
        secondary = Category.objects.create(name="Research", parent=primary, category_type='HONORS')

        # 1. Create a certificate/project with details & categories
        dummy_file = SimpleUploadedFile("study.pdf", b"pdf_content", content_type="application/pdf")
        cert = HonorableCertificate.objects.create(
            recipient_name="Alice Smith",
            recipient_email="alice@test.com",
            recipient_phone="5551234",
            project_title="AI Research",
            reason="Distinguished work",
            study_file=dummy_file,
            certificate_code="ALICE123",
            primary_category=primary,
            secondary_category=secondary
        )

        # 2. Test details page rendering
        detail_url = reverse('certificate_detail', args=[cert.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Smith")
        self.assertContains(response, "alice@test.com")
        self.assertContains(response, "AI Research")
        assert cert.study_file is not None
        self.assertContains(response, cert.study_file.url)
        self.assertContains(response, "Education")
        self.assertContains(response, "Research")
        self.assertTrue(response.context['is_pdf'])

        # 3. Test edit page rendering & post submission
        edit_url = reverse('certificate_edit', args=[cert.id])
        edit_response_get = self.client.get(edit_url)
        self.assertEqual(edit_response_get.status_code, 200)

        # Post edit update
        new_pdf = SimpleUploadedFile("new_study.pdf", b"updated_pdf_content", content_type="application/pdf")
        post_data = {
            'recipient_name': "Alice M. Smith",
            'recipient_email': "alice.m@test.com",
            'recipient_phone': "9999999",
            'project_title': "Advanced AI Research",
            'primary_category': primary.id,
            'secondary_category': secondary.id,
            'reason': "Highly distinguished work",
            'study_file': new_pdf
        }
        edit_response_post = self.client.post(edit_url, post_data)
        self.assertEqual(edit_response_post.status_code, 302) # Redirect to detail

        # Refresh from database and check values
        cert.refresh_from_db()
        self.assertEqual(cert.recipient_name, "Alice M. Smith")
        self.assertEqual(cert.project_title, "Advanced AI Research")
        self.assertEqual(cert.primary_category, primary)
        self.assertEqual(cert.secondary_category, secondary)
        assert cert.study_file is not None
        self.assertIn("new_study", cert.study_file.name)

        # Test Serialization in API
        verify_api_url = reverse('verify_cert_api', args=[cert.certificate_code])
        api_response = self.client.get(verify_api_url)
        self.assertEqual(api_response.status_code, 200)
        self.assertEqual(api_response.json()['data']['primary_category_details']['name'], "Education")
        self.assertEqual(api_response.json()['data']['secondary_category_details']['name'], "Research")

    def test_custom_logout_view(self):
        url = reverse('logout')
        response = self.client.get(url)
        # Should redirect to login page (302)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Verify the user is logged out
        protected_url = reverse('hero_list')
        response_protected = self.client.get(protected_url)
        self.assertEqual(response_protected.status_code, 302)
        self.assertIn('login', response_protected['Location'])

class StaffPermissionsTestCase(TestCase):
    def setUp(self):
        # Create users with different permission configurations
        self.superuser = User.objects.create_superuser(username='super', password='password')
        
        self.staff_all = User.objects.create_user(username='staffall', password='password', is_staff=True)
        # Note: data migration / signal automatically creates permission record with default True for all fields
        
        self.staff_restricted = User.objects.create_user(username='staffrestricted', password='password', is_staff=True)
        # Modify permissions for restricted user: only honors program
        perm = getattr(self.staff_restricted, 'staff_permission')
        perm.has_content_info = False
        perm.has_campaigns = False
        perm.has_honors_program = True
        perm.has_system_security = False
        perm.save()

        self.client = Client()

    def test_superuser_access_all(self):
        self.client.login(username='super', password='password')
        # Check hero list (Content & Info)
        response = self.client.get(reverse('hero_list'))
        self.assertEqual(response.status_code, 200)
        # Check campaign list (Campaigns)
        response = self.client.get(reverse('campaign_list'))
        self.assertEqual(response.status_code, 200)
        # Check certificates (Honors)
        response = self.client.get(reverse('certificate_list'))
        self.assertEqual(response.status_code, 200)
        # Check staff list (System & Security)
        response = self.client.get(reverse('staff_list'))
        self.assertEqual(response.status_code, 200)

    def test_restricted_user_access_honors_only(self):
        self.client.login(username='staffrestricted', password='password')
        
        # Access allowed: honors
        response = self.client.get(reverse('certificate_list'))
        self.assertEqual(response.status_code, 200)
        
        # Access denied: Campaigns -> Redirects to first allowed (certificates)
        response = self.client.get(reverse('campaign_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('certificate_list'))
        
        # Access denied: Hero -> Redirects to first allowed (certificates)
        response = self.client.get(reverse('hero_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('certificate_list'))

        # Access denied: Staff List -> Redirects to first allowed (certificates)
        response = self.client.get(reverse('staff_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('certificate_list'))

    def test_login_dynamic_redirection(self):
        # Log in restricted staff member
        response = self.client.post(reverse('login'), {
            'username': 'staffrestricted',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 302)
        # Restricted user has honors program as the first allowed section, so should redirect to certificate_list
        self.assertRedirects(response, reverse('certificate_list'))

        # Log in full access staff member
        self.client.logout()
        response = self.client.post(reverse('login'), {
            'username': 'staffall',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 302)
        # Full access redirects to hero_list (default first allowed)
        self.assertRedirects(response, reverse('hero_list'))

    def test_staff_creation_with_permissions(self):
        self.client.login(username='super', password='password')
        url = reverse('staff_create')
        post_data = {
            'username': 'newstaff',
            'email': 'new@staff.com',
            'first_name': 'New',
            'last_name': 'Staff',
            'password': 'newpassword',
            'confirm_password': 'newpassword',
            # Grant Content & Info and Campaigns, but not others
            'has_content_info': 'on',
            'has_campaigns': 'on',
            # honors and system security are not included (boolean field is False when absent in POST)
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify user and permissions created
        new_user = User.objects.get(username='newstaff')
        self.assertTrue(new_user.is_staff)
        perm = getattr(new_user, 'staff_permission')
        self.assertTrue(perm.has_content_info)
        self.assertTrue(perm.has_campaigns)
        self.assertFalse(perm.has_honors_program)
        self.assertFalse(perm.has_system_security)


class BrandingRenameTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='admin', password='password')

    def test_branding_on_login_and_public_pages(self):
        # 1. Login Page
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Navabharath")
        self.assertNotContains(response, "Promo CMS")

        # 2. Public Submit Study Page
        url = reverse('public_submit_study')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Navabharath")
        self.assertNotContains(response, "Promo CMS")

    def test_branding_on_admin_pages(self):
        self.client.login(username='admin', password='password')
        
        # 1. Dashboard base template via hero_list
        url = reverse('hero_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NAVABHARATH")
        self.assertNotContains(response, "PROMO CMS")

        # 2. Staff List Page
        url = reverse('staff_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Navabharath")
        self.assertNotContains(response, "Promo CMS")

        # 3. Participant Profile Page
        from dashboard.models import Participant
        participant = Participant.objects.create(
            name="Test Participant",
            email="test@participant.com",
            phone="1234567890",
            amount_paid=100
        )
        url = reverse('participant_profile', args=[participant.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Navabharath")
        self.assertNotContains(response, "Promo CMS")
