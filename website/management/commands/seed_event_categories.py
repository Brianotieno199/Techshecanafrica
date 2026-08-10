from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from website.models import (
    ContributionTier,
    Event,
    RegistrationCategory,
)


class Command(BaseCommand):
    help = (
        "Creates or updates the 50 TechShe Can Africa Summit "
        "registration, sponsorship, booking, and contribution categories."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--event-id",
            type=int,
            help=(
                "Optional event ID. If omitted, the most recently created "
                "active event will be used."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        event_id = options.get("event_id")

        if event_id:
            try:
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist as exc:
                raise CommandError(
                    f"No event exists with ID {event_id}."
                ) from exc
        else:
            event = (
                Event.objects.filter(is_active=True)
                .order_by("-created_at")
                .first()
            )

            if event is None:
                raise CommandError(
                    "No active event was found. Create an event in "
                    "Django Admin before running this command."
                )

        self.stdout.write(
            self.style.WARNING(
                f"Using event: {event.title} (ID: {event.id})"
            )
        )

        categories = [
            # ==========================================
            # REGISTRATION LINKS: ITEMS 1–18
            # ==========================================
            {
                "link_id": "TSC26-REG-01",
                "name": "Student Registration",
                "group": "REGISTRATION",
                "base_price": Decimal("500.00"),
                "currency": "KES",
                "description": "Registration for students attending the Summit.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 1,
            },
            {
                "link_id": "TSC26-REG-02",
                "name": "Teachers & Educators",
                "group": "REGISTRATION",
                "base_price": Decimal("1000.00"),
                "currency": "KES",
                "description": "Registration for teachers, trainers, and educators.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 2,
            },
            {
                "link_id": "TSC26-REG-03",
                "name": "Youth Innovators & Startups",
                "group": "REGISTRATION",
                "base_price": Decimal("1500.00"),
                "currency": "KES",
                "description": "Registration for youth innovators and startup founders.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 3,
            },
            {
                "link_id": "TSC26-REG-04",
                "name": "Women Entrepreneurs & MSMEs",
                "group": "REGISTRATION",
                "base_price": Decimal("2000.00"),
                "currency": "KES",
                "description": "Registration for women entrepreneurs and MSME representatives.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 4,
            },
            {
                "link_id": "TSC26-REG-05",
                "name": "Community-Based Organizations (CBOs)",
                "group": "REGISTRATION",
                "base_price": Decimal("2000.00"),
                "currency": "KES",
                "description": "Registration for Community-Based Organization representatives.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 5,
            },
            {
                "link_id": "TSC26-REG-06",
                "name": "Civil Society Organizations (CSOs)",
                "group": "REGISTRATION",
                "base_price": Decimal("3000.00"),
                "currency": "KES",
                "description": "Registration for Civil Society Organization representatives.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 6,
            },
            {
                "link_id": "TSC26-REG-07",
                "name": "Non-Governmental Organizations (NGOs)",
                "group": "REGISTRATION",
                "base_price": Decimal("3000.00"),
                "currency": "KES",
                "description": "Registration for NGO representatives.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 7,
            },
            {
                "link_id": "TSC26-REG-08",
                "name": "Corporate Professionals",
                "group": "REGISTRATION",
                "base_price": Decimal("3000.00"),
                "currency": "KES",
                "description": "Registration for corporate professionals.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 8,
            },
            {
                "link_id": "TSC26-REG-09",
                "name": "Private Sector Companies",
                "group": "REGISTRATION",
                "base_price": Decimal("5000.00"),
                "currency": "KES",
                "description": "Registration for private-sector company representatives.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 9,
            },
            {
                "link_id": "TSC26-REG-10",
                "name": "Government MDAs",
                "group": "REGISTRATION",
                "base_price": Decimal("5000.00"),
                "currency": "KES",
                "description": "Registration for government ministries, departments, and agencies.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 10,
            },
            {
                "link_id": "TSC26-REG-11",
                "name": "County Government Officials",
                "group": "REGISTRATION",
                "base_price": Decimal("5000.00"),
                "currency": "KES",
                "description": "Registration for county government officials.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 11,
            },
            {
                "link_id": "TSC26-REG-12",
                "name": "Development Partners & Donor Agencies",
                "group": "REGISTRATION",
                "base_price": Decimal("7500.00"),
                "currency": "KES",
                "description": "Registration for development partners and donor agencies.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 12,
            },
            {
                "link_id": "TSC26-REG-13",
                "name": "Members of County Assembly (MCAs)",
                "group": "REGISTRATION",
                "base_price": Decimal("3000.00"),
                "currency": "KES",
                "description": "VIP registration for Members of County Assembly.",
                "is_vip": True,
                "is_custom_amount": False,
                "display_order": 13,
            },
            {
                "link_id": "TSC26-REG-14",
                "name": "Members of Parliament (MPs)",
                "group": "REGISTRATION",
                "base_price": Decimal("5000.00"),
                "currency": "KES",
                "description": "VIP registration for Members of Parliament.",
                "is_vip": True,
                "is_custom_amount": False,
                "display_order": 14,
            },
            {
                "link_id": "TSC26-REG-15",
                "name": "Senators & Governors",
                "group": "REGISTRATION",
                "base_price": Decimal("7500.00"),
                "currency": "KES",
                "description": "VIP registration for Senators and Governors.",
                "is_vip": True,
                "is_custom_amount": False,
                "display_order": 15,
            },
            {
                "link_id": "TSC26-REG-16",
                "name": "Diplomats & Embassy Representatives",
                "group": "REGISTRATION",
                "base_price": Decimal("10000.00"),
                "currency": "KES",
                "description": "VIP registration for diplomats and embassy representatives.",
                "is_vip": True,
                "is_custom_amount": False,
                "display_order": 16,
            },
            {
                "link_id": "TSC26-REG-17",
                "name": "International Delegates",
                "group": "REGISTRATION",
                "base_price": Decimal("200.00"),
                "currency": "USD",
                "description": "VIP registration for international delegates.",
                "is_vip": True,
                "is_custom_amount": False,
                "display_order": 17,
            },
            {
                "link_id": "TSC26-REG-18",
                "name": "VIP Delegate Pass",
                "group": "REGISTRATION",
                "base_price": Decimal("10000.00"),
                "currency": "KES",
                "description": "VIP Delegate Pass with reserved front-row seating.",
                "is_vip": True,
                "is_custom_amount": False,
                "display_order": 18,
            },

            # ==========================================
            # EXHIBITION & BUSINESS: ITEMS 19–23
            # ==========================================
            {
                "link_id": "TSC26-EXH-01",
                "name": "Exhibition Booth",
                "group": "EXHIBITION",
                "base_price": Decimal("5000.00"),
                "currency": "KES",
                "description": "Standard exhibition booth booking.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 19,
            },
            {
                "link_id": "TSC26-EXH-02",
                "name": "Premium Exhibition Space",
                "group": "EXHIBITION",
                "base_price": Decimal("15000.00"),
                "currency": "KES",
                "description": "Premium exhibition space booking.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 20,
            },
            {
                "link_id": "TSC26-EXH-03",
                "name": "Product Demonstration Slot",
                "group": "EXHIBITION",
                "base_price": Decimal("20000.00"),
                "currency": "KES",
                "description": "Reserved product demonstration slot.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 21,
            },
            {
                "link_id": "TSC26-EXH-04",
                "name": "Innovation Showcase",
                "group": "EXHIBITION",
                "base_price": Decimal("30000.00"),
                "currency": "KES",
                "description": "Innovation showcase presentation opportunity.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 22,
            },
            {
                "link_id": "TSC26-EXH-05",
                "name": "Startup Pitch Session",
                "group": "EXHIBITION",
                "base_price": Decimal("15000.00"),
                "currency": "KES",
                "description": "Reserved startup pitch session.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 23,
            },

            # ==========================================
            # CORPORATE PACKAGES: ITEMS 24–25
            # ==========================================
            {
                "link_id": "TSC26-COR-01",
                "name": "Corporate Table (8 Delegates)",
                "group": "CORPORATE",
                "base_price": Decimal("40000.00"),
                "currency": "KES",
                "description": "Corporate table package for eight delegates.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 24,
            },
            {
                "link_id": "TSC26-COR-02",
                "name": "Corporate Table (10 Delegates)",
                "group": "CORPORATE",
                "base_price": Decimal("50000.00"),
                "currency": "KES",
                "description": "Corporate table package for ten delegates.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 25,
            },

            # ==========================================
            # PROGRAMME ADVERTISING: ITEMS 26–31
            # ==========================================
            {
                "link_id": "TSC26-ADV-01",
                "name": "Back Cover Advertisement",
                "group": "ADVERTISING",
                "base_price": Decimal("100000.00"),
                "currency": "KES",
                "description": "Back cover advertisement in the Summit programme.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 26,
            },
            {
                "link_id": "TSC26-ADV-02",
                "name": "Inside Front Cover",
                "group": "ADVERTISING",
                "base_price": Decimal("75000.00"),
                "currency": "KES",
                "description": "Inside front cover advertisement.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 27,
            },
            {
                "link_id": "TSC26-ADV-03",
                "name": "Inside Back Cover",
                "group": "ADVERTISING",
                "base_price": Decimal("75000.00"),
                "currency": "KES",
                "description": "Inside back cover advertisement.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 28,
            },
            {
                "link_id": "TSC26-ADV-04",
                "name": "Full Page Advertisement",
                "group": "ADVERTISING",
                "base_price": Decimal("50000.00"),
                "currency": "KES",
                "description": "Full-page programme advertisement.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 29,
            },
            {
                "link_id": "TSC26-ADV-05",
                "name": "Half Page Advertisement",
                "group": "ADVERTISING",
                "base_price": Decimal("30000.00"),
                "currency": "KES",
                "description": "Half-page programme advertisement.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 30,
            },
            {
                "link_id": "TSC26-ADV-06",
                "name": "Quarter Page Advertisement",
                "group": "ADVERTISING",
                "base_price": Decimal("20000.00"),
                "currency": "KES",
                "description": "Quarter-page programme advertisement.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 31,
            },

            # ==========================================
            # BRANDING OPPORTUNITIES: ITEMS 32–40
            # ==========================================
            {
                "link_id": "TSC26-BRD-01",
                "name": "Stage Branding Sponsor",
                "group": "BRANDING",
                "base_price": Decimal("500000.00"),
                "currency": "KES",
                "description": "Exclusive stage branding opportunity.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 32,
            },
            {
                "link_id": "TSC26-BRD-02",
                "name": "Event Backdrop Sponsor",
                "group": "BRANDING",
                "base_price": Decimal("300000.00"),
                "currency": "KES",
                "description": "Event backdrop branding opportunity.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 33,
            },
            {
                "link_id": "TSC26-BRD-03",
                "name": "Lanyard Sponsor",
                "group": "BRANDING",
                "base_price": Decimal("250000.00"),
                "currency": "KES",
                "description": "Delegate lanyard branding opportunity.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 34,
            },
            {
                "link_id": "TSC26-BRD-04",
                "name": "Delegate Badge Sponsor",
                "group": "BRANDING",
                "base_price": Decimal("150000.00"),
                "currency": "KES",
                "description": "Delegate badge branding opportunity.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 35,
            },
            {
                "link_id": "TSC26-BRD-05",
                "name": "Delegate Bag Sponsor",
                "group": "BRANDING",
                "base_price": Decimal("350000.00"),
                "currency": "KES",
                "description": "Delegate bag branding opportunity.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 36,
            },
            {
                "link_id": "TSC26-BRD-06",
                "name": "Branded Water Sponsor",
                "group": "BRANDING",
                "base_price": Decimal("150000.00"),
                "currency": "KES",
                "description": "Branded water sponsorship opportunity.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 37,
            },
            {
                "link_id": "TSC26-BRD-07",
                "name": "Registration Desk Branding",
                "group": "BRANDING",
                "base_price": Decimal("100000.00"),
                "currency": "KES",
                "description": "Registration desk branding opportunity.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 38,
            },
            {
                "link_id": "TSC26-BRD-08",
                "name": "Directional Signage Sponsor",
                "group": "BRANDING",
                "base_price": Decimal("100000.00"),
                "currency": "KES",
                "description": "Directional signage sponsorship opportunity.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 39,
            },
            {
                "link_id": "TSC26-BRD-09",
                "name": "Notebooks & Pens Sponsor",
                "group": "BRANDING",
                "base_price": Decimal("250000.00"),
                "currency": "KES",
                "description": "Notebook and pen branding opportunity.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 40,
            },

            # ==========================================
            # SPONSORSHIP PACKAGES: ITEMS 41–45
            # ==========================================
            {
                "link_id": "TSC26-SPN-01",
                "name": "Title Sponsor",
                "group": "SPONSORSHIP",
                "base_price": Decimal("2500000.00"),
                "currency": "KES",
                "description": "Premier Title Sponsor package.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 41,
            },
            {
                "link_id": "TSC26-SPN-02",
                "name": "Platinum Sponsor",
                "group": "SPONSORSHIP",
                "base_price": Decimal("1500000.00"),
                "currency": "KES",
                "description": "Platinum sponsorship package.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 42,
            },
            {
                "link_id": "TSC26-SPN-03",
                "name": "Gold Sponsor",
                "group": "SPONSORSHIP",
                "base_price": Decimal("1000000.00"),
                "currency": "KES",
                "description": "Gold sponsorship package.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 43,
            },
            {
                "link_id": "TSC26-SPN-04",
                "name": "Silver Sponsor",
                "group": "SPONSORSHIP",
                "base_price": Decimal("500000.00"),
                "currency": "KES",
                "description": "Silver sponsorship package.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 44,
            },
            {
                "link_id": "TSC26-SPN-05",
                "name": "Bronze Sponsor",
                "group": "SPONSORSHIP",
                "base_price": Decimal("250000.00"),
                "currency": "KES",
                "description": "Bronze sponsorship package.",
                "is_vip": False,
                "is_custom_amount": False,
                "display_order": 45,
            },

            # ==========================================
            # GENERAL SUPPORT: ITEMS 46–50
            # ==========================================
            {
                "link_id": "TSC26-DON-01",
                "name": "Donate to the Movement",
                "group": "DONATION",
                "base_price": Decimal("0.00"),
                "currency": "KES",
                "description": (
                    "Every shilling moves a woman from conversation to action."
                ),
                "is_vip": False,
                "is_custom_amount": True,
                "display_order": 46,
            },
            {
                "link_id": "TSC26-DON-02",
                "name": "Sponsor a Student",
                "group": "DONATION",
                "base_price": Decimal("0.00"),
                "currency": "KES",
                "description": (
                    "Put a girl in the room where the future is decided."
                ),
                "is_vip": False,
                "is_custom_amount": True,
                "display_order": 47,
            },
            {
                "link_id": "TSC26-DON-03",
                "name": "Sponsor a Woman Entrepreneur",
                "group": "DONATION",
                "base_price": Decimal("0.00"),
                "currency": "KES",
                "description": "Back the hustle. Fund the breakthrough.",
                "is_vip": False,
                "is_custom_amount": True,
                "display_order": 48,
            },
            {
                "link_id": "TSC26-DON-04",
                "name": "Sponsor a Community Delegate",
                "group": "DONATION",
                "base_price": Decimal("0.00"),
                "currency": "KES",
                "description": (
                    "No woman gets left behind because she could not "
                    "afford the bus fare."
                ),
                "is_vip": False,
                "is_custom_amount": True,
                "display_order": 49,
            },
            {
                "link_id": "TSC26-DON-05",
                "name": "General Partner Contribution",
                "group": "DONATION",
                "base_price": Decimal("0.00"),
                "currency": "KES",
                "description": (
                    "You bring the resources. We bring the reach."
                ),
                "is_vip": False,
                "is_custom_amount": True,
                "display_order": 50,
            },
        ]

        contribution_tiers = {
            "TSC26-DON-01": [
                {
                    "name": "Spark",
                    "amount": Decimal("1000.00"),
                    "description": "Spark the movement.",
                    "display_order": 1,
                },
                {
                    "name": "Ignite",
                    "amount": Decimal("2500.00"),
                    "description": "Ignite opportunity.",
                    "display_order": 2,
                },
                {
                    "name": "Amplify",
                    "amount": Decimal("5000.00"),
                    "description": "Amplify women's voices and action.",
                    "display_order": 3,
                },
                {
                    "name": "Transform",
                    "amount": Decimal("10000.00"),
                    "description": "Transform lives and communities.",
                    "display_order": 4,
                },
            ],
            "TSC26-DON-02": [
                {
                    "name": "Send 1 Student",
                    "amount": Decimal("500.00"),
                    "description": "Sponsor one student.",
                    "display_order": 1,
                },
                {
                    "name": "Send 5 Students",
                    "amount": Decimal("2500.00"),
                    "description": "Sponsor five students.",
                    "display_order": 2,
                },
                {
                    "name": "Send 10 Students",
                    "amount": Decimal("5000.00"),
                    "description": "Sponsor ten students.",
                    "display_order": 3,
                },
            ],
            "TSC26-DON-03": [
                {
                    "name": "Back 1 Entrepreneur",
                    "amount": Decimal("2000.00"),
                    "description": "Support one woman entrepreneur.",
                    "display_order": 1,
                },
                {
                    "name": "Back 3 Entrepreneurs",
                    "amount": Decimal("5000.00"),
                    "description": "Support three women entrepreneurs.",
                    "display_order": 2,
                },
                {
                    "name": "Back 5 Entrepreneurs",
                    "amount": Decimal("10000.00"),
                    "description": "Support five women entrepreneurs.",
                    "display_order": 3,
                },
            ],
            "TSC26-DON-04": [
                {
                    "name": "Get 1 Delegate There",
                    "amount": Decimal("1500.00"),
                    "description": "Support one community delegate.",
                    "display_order": 1,
                },
                {
                    "name": "Get 3 Delegates There",
                    "amount": Decimal("4000.00"),
                    "description": "Support three community delegates.",
                    "display_order": 2,
                },
                {
                    "name": "Get 5 Delegates There",
                    "amount": Decimal("7500.00"),
                    "description": "Support five community delegates.",
                    "display_order": 3,
                },
            ],
        }

        created_count = 0
        updated_count = 0
        tier_created_count = 0
        tier_updated_count = 0

        for category_data in categories:
            category, created = RegistrationCategory.objects.update_or_create(
                link_id=category_data["link_id"],
                defaults={
                    "event": event,
                    "name": category_data["name"],
                    "group": category_data["group"],
                    "base_price": category_data["base_price"],
                    "currency": category_data["currency"],
                    "description": category_data["description"],
                    "is_vip": category_data["is_vip"],
                    "is_custom_amount": category_data["is_custom_amount"],
                    "requires_standard_registration_fields": True,
                    "is_active": True,
                    "display_order": category_data["display_order"],
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            tiers = contribution_tiers.get(category.link_id, [])

            for tier_data in tiers:
                tier, tier_created = ContributionTier.objects.update_or_create(
                    category=category,
                    name=tier_data["name"],
                    defaults={
                        "amount": tier_data["amount"],
                        "description": tier_data["description"],
                        "display_order": tier_data["display_order"],
                        "is_active": True,
                    },
                )

                if tier_created:
                    tier_created_count += 1
                else:
                    tier_updated_count += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Summit registration categories seeded successfully."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Categories created: {created_count}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Categories updated: {updated_count}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Contribution tiers created: {tier_created_count}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Contribution tiers updated: {tier_updated_count}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Event: {event.title} (ID: {event.id})"
            )
        )