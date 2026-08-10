from django.core.management.base import BaseCommand
from website.models import RegistrationCategory  # Replace 'your_app' with your Django app name

CATEGORIES = [
    # Registration Links (1-18)
    ('TSC26-REG-01', 'Student Registration', 'REGISTRATION', 500, 'KES', False, False),
    ('TSC26-REG-02', 'Teachers & Educators', 'REGISTRATION', 1000, 'KES', False, False),
    ('TSC26-REG-03', 'Youth Innovators & Startups', 'REGISTRATION', 1500, 'KES', False, False),
    ('TSC26-REG-04', 'Women Entrepreneurs & MSMEs', 'REGISTRATION', 2000, 'KES', False, False),
    ('TSC26-REG-05', 'Community-Based Organizations (CBOs)', 'REGISTRATION', 2000, 'KES', False, False),
    ('TSC26-REG-06', 'Civil Society Organizations (CSOs)', 'REGISTRATION', 3000, 'KES', False, False),
    ('TSC26-REG-07', 'Non-Governmental Organizations (NGOs)', 'REGISTRATION', 3000, 'KES', False, False),
    ('TSC26-REG-08', 'Corporate Professionals', 'REGISTRATION', 3000, 'KES', False, False),
    ('TSC26-REG-09', 'Private Sector Companies', 'REGISTRATION', 5000, 'KES', False, False),
    ('TSC26-REG-10', 'Government MDAs', 'REGISTRATION', 5000, 'KES', False, False),
    ('TSC26-REG-11', 'County Government Officials', 'REGISTRATION', 5000, 'KES', False, False),
    ('TSC26-REG-12', 'Development Partners & Donor Agencies', 'REGISTRATION', 7500, 'KES', False, False),
    
    # VIP Intake (13-18)
    ('TSC26-VIP-13', 'Member of County Assembly (MCA) — VIP Intake', 'REGISTRATION', 3000, 'KES', True, False),
    ('TSC26-VIP-14', 'Member of Parliament (MP) — VIP Intake', 'REGISTRATION', 5000, 'KES', True, False),
    ('TSC26-VIP-15', 'Senators & Governors — VIP Intake', 'REGISTRATION', 7500, 'KES', True, False),
    ('TSC26-VIP-16', 'Diplomats & Embassy Representatives — VIP Intake', 'REGISTRATION', 10000, 'KES', True, False),
    ('TSC26-VIP-17', 'International Delegates — VIP Intake', 'REGISTRATION', 200, 'USD', True, False),
    ('TSC26-VIP-18', 'VIP Delegate Pass — VIP Intake', 'REGISTRATION', 10000, 'KES', True, False),

    # Exhibition & Business (19-23)
    ('TSC26-EXH-19', 'Exhibition Booth', 'EXHIBITION', 5000, 'KES', False, False),
    ('TSC26-EXH-20', 'Premium Exhibition Space', 'EXHIBITION', 15000, 'KES', False, False),
    ('TSC26-EXH-21', 'Product Demonstration Slot', 'EXHIBITION', 20000, 'KES', False, False),
    ('TSC26-EXH-22', 'Innovation Showcase', 'EXHIBITION', 30000, 'KES', False, False),
    ('TSC26-EXH-23', 'Startup Pitch Session', 'EXHIBITION', 15000, 'KES', False, False),

    # Corporate Packages (24-25)
    ('TSC26-CORP-24', 'Corporate Table (8 Delegates)', 'CORPORATE', 40000, 'KES', False, False),
    ('TSC26-CORP-25', 'Corporate Table (10 Delegates)', 'CORPORATE', 50000, 'KES', False, False),

    # Programme Advertising (26-31)
    ('TSC26-ADV-26', 'Back Cover Advertisement', 'ADVERTISING', 100000, 'KES', False, False),
    ('TSC26-ADV-27', 'Inside Front Cover', 'ADVERTISING', 75000, 'KES', False, False),
    ('TSC26-ADV-28', 'Inside Back Cover', 'ADVERTISING', 75000, 'KES', False, False),
    ('TSC26-ADV-29', 'Full Page Advertisement', 'ADVERTISING', 50000, 'KES', False, False),
    ('TSC26-ADV-30', 'Half Page Advertisement', 'ADVERTISING', 30000, 'KES', False, False),
    ('TSC26-ADV-31', 'Quarter Page Advertisement', 'ADVERTISING', 20000, 'KES', False, False),

    # Branding Opportunities (32-40)
    ('TSC26-BRD-32', 'Stage Branding Sponsor', 'BRANDING', 500000, 'KES', False, False),
    ('TSC26-BRD-33', 'Event Backdrop Sponsor', 'BRANDING', 300000, 'KES', False, False),
    ('TSC26-BRD-34', 'Lanyard Sponsor', 'BRANDING', 250000, 'KES', False, False),
    ('TSC26-BRD-35', 'Delegate Badge Sponsor', 'BRANDING', 150000, 'KES', False, False),
    ('TSC26-BRD-36', 'Delegate Bag Sponsor', 'BRANDING', 350000, 'KES', False, False),
    ('TSC26-BRD-37', 'Branded Water Sponsor', 'BRANDING', 150000, 'KES', False, False),
    ('TSC26-BRD-38', 'Registration Desk Branding', 'BRANDING', 100000, 'KES', False, False),
    ('TSC26-BRD-39', 'Directional Signage Sponsor', 'BRANDING', 100000, 'KES', False, False),
    ('TSC26-BRD-40', 'Notebooks & Pens Sponsor', 'BRANDING', 250000, 'KES', False, False),

    # Sponsorship Packages (41-45)
    ('TSC26-SPON-41', 'Title Sponsor', 'SPONSORSHIP', 2500000, 'KES', False, False),
    ('TSC26-SPON-42', 'Platinum Sponsor', 'SPONSORSHIP', 1500000, 'KES', False, False),
    ('TSC26-SPON-43', 'Gold Sponsor', 'SPONSORSHIP', 1000000, 'KES', False, False),
    ('TSC26-SPON-44', 'Silver Sponsor', 'SPONSORSHIP', 500000, 'KES', False, False),
    ('TSC26-SPON-45', 'Bronze Sponsor', 'SPONSORSHIP', 250000, 'KES', False, False),

    # General Support / Donations (46-50)
    ('TSC26-DON-46', 'Donate to the Movement', 'DONATION', 1000, 'KES', False, True),
    ('TSC26-DON-47', 'Sponsor a Student', 'DONATION', 500, 'KES', False, True),
    ('TSC26-DON-48', 'Sponsor a Woman Entrepreneur', 'DONATION', 2000, 'KES', False, True),
    ('TSC26-DON-49', 'Sponsor a Community Delegate', 'DONATION', 1500, 'KES', False, True),
    ('TSC26-DON-50', 'General Partner Contribution', 'DONATION', 1000, 'KES', False, True),
]

class Command(BaseCommand):
    help = "Seeds all 50 registration and support categories into the database."

    def handle(self, *args, **options):
        for link_id, name, group, price, currency, is_vip, is_custom in CATEGORIES:
            RegistrationCategory.objects.update_or_create(
                link_id=link_id,
                defaults={
                    'name': name,
                    'group': group,
                    'base_price': price,
                    'currency': currency,
                    'is_vip': is_vip,
                    'is_custom_amount': is_custom,
                    'is_active': True,
                }
            )
        self.stdout.write(self.style.SUCCESS("Successfully seeded all 50 Summit tracking categories!"))