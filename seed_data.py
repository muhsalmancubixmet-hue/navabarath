import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from dashboard.models import (
    HeroSection, Testimonial, FAQ, Campaign, Category, Participant,
    HonorableCertificate, StudySubmission, ActivityLog
)

User = get_user_model()

def seed():
    print("Clearing existing data...")
    HeroSection.objects.all().delete()
    Testimonial.objects.all().delete()
    FAQ.objects.all().delete()
    Campaign.objects.all().delete()
    Category.objects.all().delete()
    Participant.objects.all().delete()
    HonorableCertificate.objects.all().delete()
    StudySubmission.objects.all().delete()
    ActivityLog.objects.all().delete()
    
    # Delete non-superuser staff members to allow clean creation
    User.objects.filter(is_superuser=False).delete()

    # Define a 1-pixel GIF representation for model images
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9'
        b'\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
        b'\x00\x02\x02\x4c\x01\x00\x3b'
    )

    # 1. Seed Campaign Categories (Need 15 entries)
    print("Seeding Campaign Categories...")
    campaign_primaries = []
    campaign_primary_names = ["Technology", "Healthcare", "Education", "Arts & Culture", "Social Welfare"]
    for name in campaign_primary_names:
        cat = Category.objects.create(name=name, category_type='CAMPAIGN')
        campaign_primaries.append(cat)
    
    campaign_secondaries = []
    campaign_secondary_names = [
        ("Web Development", campaign_primaries[0]),
        ("Mobile App Development", campaign_primaries[0]),
        ("AI & Machine Learning", campaign_primaries[0]),
        ("Heart Health Drive", campaign_primaries[1]),
        ("Mental Health Awareness", campaign_primaries[1]),
        ("Undergrad Scholarships", campaign_primaries[2]),
        ("High School Grants", campaign_primaries[2]),
        ("Literary Festivals", campaign_primaries[3]),
        ("Community Cleanup", campaign_primaries[4]),
        ("Disaster Relief Funds", campaign_primaries[4]),
    ]
    for name, parent in campaign_secondary_names:
        cat = Category.objects.create(name=name, parent=parent, category_type='CAMPAIGN')
        campaign_secondaries.append(cat)

    # 2. Seed Honors Categories (Need 15 entries)
    print("Seeding Honors Categories...")
    honors_primaries = []
    honors_primary_names = ["Academic Honors", "Scientific Research", "Social Contribution", "Artistic Merit", "Young Innovator"]
    for name in honors_primary_names:
        cat = Category.objects.create(name=name, category_type='HONORS')
        honors_primaries.append(cat)
        
    honors_secondaries = []
    honors_secondary_names = [
        ("Computer Science Excellence", honors_primaries[0]),
        ("Mathematics Distinction", honors_primaries[0]),
        ("BioTech Discoveries", honors_primaries[1]),
        ("Renewable Energy Research", honors_primaries[1]),
        ("Youth Leadership Award", honors_primaries[2]),
        ("Environmental Advocacy", honors_primaries[2]),
        ("Outstanding Poetry", honors_primaries[3]),
        ("Classical Music Honors", honors_primaries[3]),
        ("Robotics Prototype", honors_primaries[4]),
        ("FinTech Innovation", honors_primaries[4]),
    ]
    for name, parent in honors_secondary_names:
        cat = Category.objects.create(name=name, parent=parent, category_type='HONORS')
        honors_secondaries.append(cat)

    # 3. Seed Participants (Need 15+ entries)
    print("Seeding Custom Participants...")
    participants = []
    participant_data = [
        ("Rahul Das", "rahul@gmail.com", "+91 9946012345", "PAID", 2500.00),
        ("Anjali Nair", "anjali@yahoo.com", "+91 9847054321", "PENDING", 0.00),
        ("Fadi Muhammed", "fadi@dev.com", "+91 9744112233", "PAID", 5000.00),
        ("Sneha Johnston", "sneha@outlook.com", "+91 9562001122", "REFUNDED", 1500.00),
        ("Rinshad KC", "rinshad@talrop.com", "+91 8594056789", "PAID", 2500.00),
        ("Deepak Kumar", "deepak@gmail.com", "+91 9998887771", "PAID", 1000.00),
        ("Divya Lakshmi", "divya@gmail.com", "+91 9998887772", "PAID", 1200.00),
        ("Arjun Varma", "arjun@gmail.com", "+91 9998887773", "PAID", 2500.00),
        ("Meera Nair", "meera@gmail.com", "+91 9998887774", "PAID", 3000.00),
        ("Sandeep Krishna", "sandeep@gmail.com", "+91 9998887775", "PAID", 1500.00),
        ("Sarah Connor", "sarah@skynet.com", "+91 9112233445", "PENDING", 0.00),
        ("John Connor", "john@resistance.org", "+91 9112233446", "PAID", 4500.00),
        ("Bruce Wayne", "bruce@waynecorp.com", "+91 9112233447", "PAID", 10000.00),
        ("Clark Kent", "clark@dailyplanet.com", "+91 9112233448", "REFUNDED", 500.00),
        ("Diana Prince", "diana@themyscira.gov", "+91 9112233449", "PAID", 7500.00),
        ("Peter Parker", "peter@bugle.com", "+91 9112233450", "PENDING", 0.00),
    ]
    for name, email, phone, status, amount in participant_data:
        p = Participant.objects.create(
            name=name,
            email=email,
            phone=phone,
            payment_status=status,
            amount_paid=amount
        )
        participants.append(p)

    # 4. Seed Hero Sections (Need 15 entries)
    print("Seeding Hero Sections...")
    for i in range(1, 16):
        HeroSection.objects.create(
            title=f"Empowering Navabharath Innovators - Phase {i}",
            subtitle=f"This is the subtitle/description for banner phase {i} of the Navabharath national promotion program.",
            order=i,
            image=ContentFile(small_gif, name=f"hero_{i}.gif")
        )

    # 5. Seed Testimonials (Need 15 entries)
    print("Seeding Testimonials...")
    for i in range(1, 16):
        Testimonial.objects.create(
            client_name=f"Partner Client {i}",
            feedback=f"The campaigns and honors provided in phase {i} were extremely beneficial for our growth and community outreach.",
            client_designation=f"Director of Operations, Enterprise {i}",
            image=ContentFile(small_gif, name=f"testimonial_{i}.gif")
        )

    # 6. Seed FAQs (Need 15 entries)
    print("Seeding FAQs...")
    faq_questions = [
        "How can I register for the Navabharath Campaign?",
        "What are the payment methods supported for registration?",
        "How do I submit my study or project for the Honors Program?",
        "Who is eligible to participate in the blood donation drives?",
        "Can I edit my campaign details after launching?",
        "How long does the certificate approval process take?",
        "Is there a refund policy for paid campaigns?",
        "How can I contact support if I have login issues?",
        "Can a secondary category belong to multiple primary categories?",
        "What file formats are supported for study file uploads?",
        "How do I verify the authenticity of a certificate code?",
        "Can I register multiple participants in bulk?",
        "Who manages the staff directory permissions?",
        "Are the activity logs visible to all staff members?",
        "What is the next phase of the startup promotion drive?",
    ]
    for i, question in enumerate(faq_questions, 1):
        FAQ.objects.create(
            question=question,
            answer=f"This is the detailed answer for FAQ question {i}. It explains the guidelines, rules, and expectations of the platform."
        )

    # 7. Seed Campaigns (Need 15 entries)
    print("Seeding Campaigns...")
    today = datetime.now().date()
    campaigns = []
    for i in range(1, 16):
        p_cat = campaign_primaries[i % len(campaign_primaries)]
        s_cat = campaign_secondaries[i % len(campaign_secondaries)]
        c = Campaign.objects.create(
            name=f"National Promotion Campaign {i}",
            description=f"This is a description for national promotion campaign number {i}. It focuses on accelerating growth in {p_cat.name} -> {s_cat.name}.",
            start_date=today - timedelta(days=5 * i),
            end_date=today + timedelta(days=5 * (16 - i)),
            is_active=(i % 2 == 1),
            primary_category=p_cat,
            secondary_category=s_cat,
            image=ContentFile(small_gif, name=f"campaign_{i}.gif")
        )
        # Link 3 participants to each campaign dynamically
        c.participants.add(
            participants[(i - 1) % len(participants)],
            participants[i % len(participants)],
            participants[(i + 1) % len(participants)]
        )
        campaigns.append(c)

    # 8. Seed Honorable Certificates & Study Submissions (Need 15 entries)
    print("Seeding Honors Certificates & Submissions...")
    for i in range(1, 16):
        p_cat = honors_primaries[i % len(honors_primaries)]
        s_cat = honors_secondaries[i % len(honors_secondaries)]
        
        cert = HonorableCertificate.objects.create(
            recipient_name=f"Award Recipient {i}",
            recipient_email=f"recipient{i}@scholarly.org",
            recipient_phone=f"+91 9991112{i:03d}",
            project_title=f"Pioneering Research Initiative {i}",
            primary_category=p_cat,
            secondary_category=s_cat,
            certificate_code=f"HONORS{i:03d}CODE",
            reason=f"Awarded for outstanding contribution to research and development in {s_cat.name}.",
            study_file=ContentFile(b"PDF document content simulation for research project.", name=f"study_doc_{i}.pdf")
        )
        
        # Link to StudySubmissions with alternating statuses: APPROVED, PENDING, REJECTED
        status = 'APPROVED' if i <= 10 else ('PENDING' if i <= 13 else 'REJECTED')
        
        StudySubmission.objects.create(
            student_name=cert.recipient_name,
            email=cert.recipient_email,
            title=cert.project_title,
            content=f"Detailed study and prototype submission explaining the findings of initiative {i}.",
            status=status,
            certificate=cert if status == 'APPROVED' else None
        )

    # 9. Seed Staff Directory & Permissions (Need 15 entries)
    print("Seeding Staff Directory...")
    staff_users = []
    for i in range(1, 16):
        username = f"staff_member_{i}"
        email = f"staff{i}@navabharath.gov"
        user = User.objects.create_user(
            username=username,
            email=email,
            password="StaffPassword123!",
            is_staff=True,
            first_name=f"StaffName{i}",
            last_name=f"LastName{i}"
        )
        # StaffPermission is automatically created by the post_save signal.
        # We fetch and customize permissions to represent a diverse staff setup:
        perm = getattr(user, 'staff_permission')
        perm.has_content_info = (i % 4 != 0)
        perm.has_campaigns = (i % 4 != 1)
        perm.has_honors_program = (i % 4 != 2)
        perm.has_system_security = (i % 4 != 3)
        perm.save()
        staff_users.append(user)

    # 10. Seed Activity Logs (Need 15 entries)
    print("Seeding Activity Logs...")
    activity_actions = [
        "Logged into the dashboard",
        "Created new Hero Section: Banner 1",
        "Updated Campaign Details: Summer Bootcamp",
        "Approved study submission from Recipient 1",
        "Updated FAQ: Contact information",
        "Created primary category: Science",
        "Created secondary category: Robotics under Science",
        "Rejected incomplete study submission",
        "Exported campaign participant CSV file",
        "Created new staff account for staff_member_5",
        "Updated Testimonial for Client 2",
        "Reordered landing page Hero Sections",
        "Modified staff permission settings",
        "Deleted obsolete FAQ item",
        "Generated certificate HONORS005CODE",
    ]
    for i, action in enumerate(activity_actions, 1):
        user = staff_users[i % len(staff_users)]
        ActivityLog.objects.create(
            user=user,
            action=action
        )

    # 11. Seed 1,000 participants for pagination testing
    print("Seeding 1000 bulk clinical donor participants for pagination...")
    bulk_list = []
    for i in range(1, 1001):
        bulk_list.append(Participant(
            name=f"Donor Participant {i}",
            email=f"donor{i}@clinical.com",
            phone=f"+91 95000{i:05d}",
            payment_status="PAID",
            amount_paid=100.00
        ))
    Participant.objects.bulk_create(bulk_list)
    
    # Associate all 1,000 bulk participants to the last campaign (Campaign 15)
    last_campaign = campaigns[-1]
    new_participants = Participant.objects.filter(email__endswith="@clinical.com")
    last_campaign.participants.add(*new_participants)

    print("Success: 15+ entries for every model, plus 1,000 bulk participants generated!")

if __name__ == "__main__":
    seed()