# seed_data.py (Updated snippet)
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from dashboard.models import Campaign, Participant, Category

def seed():
    Campaign.objects.all().delete()
    Participant.objects.all().delete()
    Category.objects.all().delete()

    # Seed Categories
    cat_edu = Category.objects.create(name="Education")
    cat_django = Category.objects.create(name="Django Bootcamp", parent=cat_edu)
    cat_scholar = Category.objects.create(name="Scholarships", parent=cat_edu)

    cat_don = Category.objects.create(name="Donation")
    cat_blood = Category.objects.create(name="Blood Donation", parent=cat_don)
    cat_fund = Category.objects.create(name="Financial Funding", parent=cat_don)

    p1 = Participant.objects.create(name="Rahul Das", email="rahul@gmail.com", phone="+91 9946012345", payment_status="PAID", amount_paid=2500.00)
    p2 = Participant.objects.create(name="Anjali Nair", email="anjali@yahoo.com", phone="+91 9847054321", payment_status="PENDING", amount_paid=0.00)
    p3 = Participant.objects.create(name="Fadi Muhammed", email="fadi@dev.com", phone="+91 9744112233", payment_status="PAID", amount_paid=5000.00)
    p4 = Participant.objects.create(name="Sneha Johnston", email="sneha@outlook.com", phone="+91 9562001122", payment_status="REFUNDED", amount_paid=1500.00)
    p5 = Participant.objects.create(name="Rinshad KC", email="rinshad@talrop.com", phone="+91 8594056789", payment_status="PAID", amount_paid=2500.00)
    p6 = Participant.objects.create(name="Deepak Kumar", email="deepak@gmail.com", phone="+91 9998887771", payment_status="PAID", amount_paid=0.00)
    p7 = Participant.objects.create(name="Divya Lakshmi", email="divya@gmail.com", phone="+91 9998887772", payment_status="PAID", amount_paid=0.00)
    p8 = Participant.objects.create(name="Arjun Varma", email="arjun@gmail.com", phone="+91 9998887773", payment_status="PAID", amount_paid=0.00)
    p9 = Participant.objects.create(name="Meera Nair", email="meera@gmail.com", phone="+91 9998887774", payment_status="PAID", amount_paid=0.00)
    p10 = Participant.objects.create(name="Sandeep Krishna", email="sandeep@gmail.com", phone="+91 9998887775", payment_status="PAID", amount_paid=0.00)

    today = datetime.now().date()
    c1 = Campaign.objects.create(
        name="Summer Tech BootCamp 2026", 
        description="Intensive Django scalable architecture drive.", 
        start_date=today-timedelta(days=5), 
        end_date=today+timedelta(days=5), 
        is_active=True,
        primary_category=cat_edu,
        secondary_category=cat_django
    )
    c1.participants.add(p1, p3, p5)

    c2 = Campaign.objects.create(
        name="Kerala Startup Promotion Drive", 
        description="Early stage developer incubator push.", 
        start_date=today-timedelta(days=20), 
        end_date=today-timedelta(days=5), 
        is_active=False,
        primary_category=cat_don,
        secondary_category=cat_fund
    )
    c2.participants.add(p2, p3, p4)

    c3 = Campaign.objects.create(
        name="Annual Blood Donation Drive 2026",
        description="A community blood donation drive organized in partnership with local hospitals to support emergency wards. Open to healthy donors with full checkups provided.",
        start_date=today-timedelta(days=2),
        end_date=today+timedelta(days=10),
        is_active=True,
        primary_category=cat_don,
        secondary_category=cat_blood
    )
    
    # Seed 1000 participants for pagination testing
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
    
    # Retrieve and link all 1000 participants
    new_participants = Participant.objects.filter(email__endswith="@clinical.com")
    c3.participants.add(*new_participants)

    print("New Fake Data with Categories and Payment Records Seeded!")

if __name__ == "__main__":
    seed()