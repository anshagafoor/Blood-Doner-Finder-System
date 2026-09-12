import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from donors.models import DonorProfile, DonationHistory
from hospitals.models import HospitalProfile, BloodRequest
from organizations.models import OrganizationProfile, DonationCamp, AwarenessProgram
from rewards.models import Badge
from rewards.services import check_and_award_badges

BADGES = [
    ("First Drop", "Complete your first donation", "fa-droplet", "#e63946", 100, 1),
    ("Life Saver", "Donate blood 3 times", "fa-heart", "#d62828", 300, 3),
    ("Guardian", "Reach 500 reward points", "fa-shield-heart", "#b11116", 500, 0),
    ("Hero", "Donate blood 5 times", "fa-star", "#c98600", 500, 5),
    ("Legend", "Reach 1000 reward points", "fa-crown", "#7a0d12", 1000, 0),
]

FIRST = ["Arjun", "Meera", "Rahul", "Anjali", "Vishnu", "Priya", "Kiran", "Deepa",
         "Sanjay", "Nithya", "Rohit", "Lakshmi", "Aravind", "Sneha", "Manu", "Divya"]
DISTRICTS = ["Ernakulam", "Thrissur", "Kozhikode", "Thiruvananthapuram", "Malappuram", "Kollam"]
GROUPS = ["A+", "B+", "O+", "AB+", "A-", "O-", "B-", "AB-"]


class Command(BaseCommand):
    help = "Seed the database with demo data"

    def handle(self, *args, **opts):
        # Badges
        for name, desc, icon, color, pts, don in BADGES:
            Badge.objects.get_or_create(name=name, defaults=dict(
                description=desc, icon=icon, color=color,
                points_required=pts, donations_required=don))
        self.stdout.write("Badges created.")

        # Admin
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser("admin", "admin@bloodlink.com", "admin12345")
            admin.role = User.Role.ADMIN
            admin.save()
            self.stdout.write("Admin created -> admin / admin12345")

        # Donors
        for i in range(16):
            uname = f"donor{i+1}"
            if User.objects.filter(username=uname).exists():
                continue
            u = User.objects.create_user(uname, f"{uname}@mail.com", "donor12345",
                                         role=User.Role.DONOR, phone=f"98470{10000+i}")
            donations = random.randint(0, 6)
            p = DonorProfile.objects.create(
                user=u, full_name=f"{random.choice(FIRST)} {random.choice(['Nair','Menon','Kumar','Das','Pillai'])}",
                blood_group=random.choice(GROUPS), district=random.choice(DISTRICTS),
                gender=random.choice(["M", "F"]),
                date_of_birth=timezone.now().date() - timedelta(days=365*random.randint(20, 45)),
                is_available=random.random() > 0.25,
                total_donations=donations, total_points=donations*100,
                last_donation_date=timezone.now().date() - timedelta(days=random.randint(10, 200)) if donations else None,
            )
            for d in range(donations):
                DonationHistory.objects.create(
                    donor=p, date=timezone.now().date() - timedelta(days=random.randint(30, 400)*(d+1)),
                    location=f"{random.choice(DISTRICTS)} General Hospital", units=1,
                    points_awarded=100, note="Voluntary donation")
            check_and_award_badges(p)
        self.stdout.write("16 donors created -> donor1..donor16 / donor12345")

        # Hospital
        if not User.objects.filter(username="hospital1").exists():
            hu = User.objects.create_user("hospital1", "hosp@mail.com", "hospital12345",
                                          role=User.Role.HOSPITAL, phone="04842200000")
            hp = HospitalProfile.objects.create(
                user=hu, hospital_name="City Care Hospital", district="Ernakulam",
                license_number="KL-HOSP-2291", address="MG Road, Kochi", verified=True)
            BloodRequest.objects.create(
                hospital=hp, patient_name="Emergency Patient", blood_group="O+",
                units_needed=2, district="Ernakulam", urgency=BloodRequest.Urgency.CRITICAL,
                contact_number="04842200000", notes="Urgent surgery case.")
            BloodRequest.objects.create(
                hospital=hp, patient_name="Ward 4 Patient", blood_group="B+",
                units_needed=1, district="Ernakulam", urgency=BloodRequest.Urgency.HIGH,
                contact_number="04842200000")
            self.stdout.write("Hospital created -> hospital1 / hospital12345")

        # Organization + camp
        if not User.objects.filter(username="org1").exists():
            ou = User.objects.create_user("org1", "org@mail.com", "org12345",
                                          role=User.Role.ORGANIZATION, phone="9846000000")
            op = OrganizationProfile.objects.create(
                user=ou, org_name="LifeShare Foundation", district="Ernakulam",
                address="Kaloor, Kochi", verified=True)
            DonationCamp.objects.create(
                organization=op, title="Mega Blood Donation Camp",
                description="A community-wide blood donation drive open to all eligible donors.",
                district="Ernakulam", location="Town Hall, Kochi",
                date=timezone.now().date() + timedelta(days=12))
            DonationCamp.objects.create(
                organization=op, title="Campus Blood Drive",
                description="Blood donation camp at the local college campus.",
                district="Thrissur", location="Govt College, Thrissur",
                date=timezone.now().date() + timedelta(days=25))
            AwarenessProgram.objects.create(
                organization=op, title="Why Your Blood Type Matters",
                description="An awareness session on blood compatibility and safe donation.",
                date=timezone.now().date() + timedelta(days=5), location="Community Center, Kochi")
            self.stdout.write("Organization created -> org1 / org12345")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
