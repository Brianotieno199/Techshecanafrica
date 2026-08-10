from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = CKEditor5Field("Content", config_name="extends")
    image = models.ImageField(upload_to="blog/", blank=True, null=True)
    meta_description = models.CharField(max_length=160, blank=True)
    author = models.CharField(
        max_length=100,
        default="TechShe Can Africa",
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            original_slug = slugify(self.title)
            slug = original_slug
            counter = 1

            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            self.slug = slug

        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="gallery/")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
    )
    flyer = models.ImageField(
        upload_to="event_flyers/",
        blank=True,
        null=True,
    )
    event_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    registration_open = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            original_slug = slugify(self.title)
            slug = original_slug
            counter = 1

            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"


# ==========================================
# EVENT REGISTRATION AND TRACKING SYSTEM
# ==========================================


class RegistrationCategory(models.Model):
    GROUP_CHOICES = [
        ("REGISTRATION", "Registration Links"),
        ("EXHIBITION", "Exhibition & Business"),
        ("CORPORATE", "Corporate Packages"),
        ("ADVERTISING", "Programme Advertising"),
        ("BRANDING", "Branding Opportunities"),
        ("SPONSORSHIP", "Sponsorship Packages"),
        ("DONATION", "General Support & Donations"),
    ]

    CURRENCY_CHOICES = [
        ("KES", "KSh"),
        ("USD", "USD"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registration_categories",
    )

    link_id = models.CharField(
        max_length=30,
        unique=True,
        help_text="Example: TSC26-REG-01",
    )

    name = models.CharField(max_length=200)

    slug = models.SlugField(
        max_length=240,
        blank=True,
    )

    description = models.TextField(blank=True)

    group = models.CharField(
        max_length=30,
        choices=GROUP_CHOICES,
    )

    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Set the fixed base price. Use 0 for custom-only contributions.",
    )

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="KES",
    )

    is_vip = models.BooleanField(
        default=False,
        help_text="Displays the VIP intake form.",
    )

    is_custom_amount = models.BooleanField(
        default=False,
        help_text="Allows the user to enter a custom contribution amount.",
    )

    requires_standard_registration_fields = models.BooleanField(
        default=True,
        help_text=(
            "Collect full name, organization/title, phone, email and category."
        ),
    )

    is_active = models.BooleanField(default=True)

    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registration Category"
        verbose_name_plural = "Registration Categories"
        ordering = ["display_order", "link_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "slug"],
                name="unique_registration_category_slug_per_event",
            )
        ]

    def clean(self):
        errors = {}

        if self.base_price < Decimal("0.00"):
            errors["base_price"] = "The base price cannot be negative."

        if self.currency == "USD" and self.group != "REGISTRATION":
            pass

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.slug:
            original_slug = slugify(self.name)
            slug = original_slug
            counter = 1

            while RegistrationCategory.objects.filter(
                event=self.event,
                slug=slug,
            ).exclude(pk=self.pk).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            self.slug = slug

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.link_id} - {self.name} "
            f"({self.currency} {self.base_price})"
        )


class ContributionTier(models.Model):
    category = models.ForeignKey(
        RegistrationCategory,
        on_delete=models.CASCADE,
        related_name="contribution_tiers",
    )

    name = models.CharField(
        max_length=100,
        help_text="Example: Spark, Ignite or Send 1 Student",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.00"))],
    )

    description = models.CharField(max_length=255, blank=True)

    display_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "amount"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"],
                name="unique_contribution_tier_name_per_category",
            )
        ]

    def __str__(self):
        return f"{self.category.name} - {self.name} ({self.amount})"


class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("paid", "Paid / Confirmed"),
        ("attended", "Attended"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
    )

    category_item = models.ForeignKey(
        RegistrationCategory,
        on_delete=models.PROTECT,
        related_name="registrations",
    )

    selected_contribution_tier = models.ForeignKey(
        ContributionTier,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="registrations",
    )

    # Core registrant information
    full_name = models.CharField(max_length=200)

    organization_or_title = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Organization / Title / CBO",
    )

    phone_number = models.CharField(max_length=30)

    email = models.EmailField()

    national_id_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    # Location details
    county = models.CharField(
        max_length=100,
        default="Homa Bay",
    )

    sub_county = models.CharField(
        max_length=100,
        blank=True,
    )

    ward = models.CharField(
        max_length=100,
        blank=True,
    )

    # Financial details
    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    custom_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("1.00"))],
    )

    vip_addons_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    amount_payable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    currency = models.CharField(
        max_length=3,
        choices=RegistrationCategory.CURRENCY_CHOICES,
        default="KES",
    )

    payment_reference = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Latest gateway transaction reference.",
    )

    # Marketing channel tracking
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    utm_content = models.CharField(max_length=100, blank=True)
    utm_term = models.CharField(max_length=100, blank=True)
    referral_code = models.CharField(max_length=100, blank=True)

    additional_information = models.TextField(blank=True)

    consent_to_record_storage = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event", "status"]),
            models.Index(fields=["email"]),
            models.Index(fields=["payment_reference"]),
            models.Index(fields=["utm_source"]),
        ]

    def clean(self):
        errors = {}

        if not self.consent_to_record_storage:
            errors["consent_to_record_storage"] = (
                "You must consent before completing registration."
            )

        if self.category_item_id and self.event_id:
            if self.category_item.event_id != self.event_id:
                errors["category_item"] = (
                    "The selected category does not belong to this event."
                )

        if self.selected_contribution_tier_id and self.category_item_id:
            if (
                self.selected_contribution_tier.category_id
                != self.category_item_id
            ):
                errors["selected_contribution_tier"] = (
                    "The selected contribution tier does not belong "
                    "to this category."
                )

        if self.category_item_id:
            if self.category_item.is_custom_amount:
                if (
                    self.custom_amount is None
                    and self.selected_contribution_tier_id is None
                    and self.category_item.base_price <= Decimal("0.00")
                ):
                    errors["custom_amount"] = (
                        "Select a suggested contribution or enter "
                        "a custom amount."
                    )
            elif self.custom_amount is not None:
                errors["custom_amount"] = (
                    "A custom amount is not allowed for this category."
                )

        if errors:
            raise ValidationError(errors)

    def calculate_base_amount(self):
        if not self.category_item_id:
            return Decimal("0.00")

        if self.custom_amount is not None:
            return self.custom_amount

        if self.selected_contribution_tier_id:
            return self.selected_contribution_tier.amount

        return self.category_item.base_price

    def calculate_total_amount(self):
        return self.calculate_base_amount() + self.vip_addons_amount

    def save(self, *args, **kwargs):
        if self.category_item_id:
            self.event = self.category_item.event
            self.currency = self.category_item.currency
            self.base_amount = self.calculate_base_amount()
            self.amount_payable = self.calculate_total_amount()

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} — {self.category_item.link_id}"


class VIPProfile(models.Model):
    registration = models.OneToOneField(
        EventRegistration,
        on_delete=models.CASCADE,
        related_name="vip_profile",
    )

    # Identity and protocol
    preferred_address = models.CharField(
        max_length=100,
        help_text="Example: Hon., H.E., Ambassador or Dr.",
    )

    official_bio = models.TextField(blank=True)

    headshot = models.ImageField(
        upload_to="vip_headshots/",
        blank=True,
        null=True,
    )

    passport_or_id = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Required for diplomats and international delegates. "
            "Optional for other VIP categories."
        ),
    )

    # Security and logistics
    security_detail_size = models.PositiveIntegerField(default=0)

    vehicle_details = models.TextField(
        blank=True,
        help_text="Motorcade, vehicle type and registration details.",
    )

    parking_requirements = models.TextField(blank=True)

    arrival_date = models.DateField(blank=True, null=True)
    arrival_time = models.TimeField(blank=True, null=True)

    departure_date = models.DateField(blank=True, null=True)
    departure_time = models.TimeField(blank=True, null=True)

    transport_coordination_needed = models.BooleanField(default=False)

    transport_coordination_details = models.TextField(blank=True)

    security_notification_required = models.BooleanField(default=False)

    security_notification_completed = models.BooleanField(default=False)

    # Hospitality
    dietary_requirements = models.CharField(
        max_length=255,
        blank=True,
    )

    accommodation_needed = models.BooleanField(default=False)

    accommodation_details = models.TextField(blank=True)

    accompanying_aides_count = models.PositiveIntegerField(default=0)

    aides_fee_charged = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    # VIP add-ons
    add_on_meet_greet = models.BooleanField(
        default=False,
        help_text="Private meet-and-greet slot: KSh 15,000.",
    )

    add_on_stage_shoutout = models.BooleanField(
        default=False,
        help_text="On-stage recognition or shout-out: KSh 10,000.",
    )

    add_on_fee_charged = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    # Programme and administration
    is_speaking = models.BooleanField(default=False)

    speaking_or_presentation_notes = models.TextField(blank=True)

    specific_request = models.TextField(blank=True)

    rsvp_deadline = models.DateField(blank=True, null=True)

    assigned_liaison = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: Mike or David",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "VIP Profile"
        verbose_name_plural = "VIP Profiles"

    def clean(self):
        errors = {}

        if self.registration_id:
            if not self.registration.category_item.is_vip:
                errors["registration"] = (
                    "A VIP profile can only be created for a VIP category."
                )

            category_name = self.registration.category_item.name.lower()

            requires_passport_or_id = any(
                keyword in category_name
                for keyword in [
                    "diplomat",
                    "embassy",
                    "international delegate",
                ]
            )

            if requires_passport_or_id and not self.passport_or_id:
                errors["passport_or_id"] = (
                    "Passport or ID number is required for diplomats "
                    "and international delegates."
                )

        if self.accommodation_needed and not self.accommodation_details:
            errors["accommodation_details"] = (
                "Please provide accommodation details."
            )

        if (
            self.transport_coordination_needed
            and not self.transport_coordination_details
        ):
            errors["transport_coordination_details"] = (
                "Please provide transport coordination details."
            )

        if errors:
            raise ValidationError(errors)

    def calculate_aides_fee(self):
        count = self.accompanying_aides_count

        if count <= 1:
            return Decimal("0.00")

        fee = Decimal("0.00")

        if count >= 2:
            fee += Decimal("3000.00")

        if count >= 3:
            fee += Decimal("3000.00")

        if count >= 4:
            fee += Decimal(count - 3) * Decimal("5000.00")

        return fee

    def calculate_addons_fee(self):
        fee = Decimal("0.00")

        if self.add_on_meet_greet:
            fee += Decimal("15000.00")

        if self.add_on_stage_shoutout:
            fee += Decimal("10000.00")

        return fee

    def save(self, *args, **kwargs):
        self.aides_fee_charged = self.calculate_aides_fee()
        self.add_on_fee_charged = self.calculate_addons_fee()

        self.full_clean()
        super().save(*args, **kwargs)

        total_vip_fees = (
            self.aides_fee_charged + self.add_on_fee_charged
        )

        if self.registration.vip_addons_amount != total_vip_fees:
            self.registration.vip_addons_amount = total_vip_fees
            self.registration.amount_payable = (
                self.registration.calculate_base_amount()
                + total_vip_fees
            )

            self.registration.save(
                update_fields=[
                    "vip_addons_amount",
                    "amount_payable",
                    "updated_at",
                ]
            )

    def __str__(self):
        return f"VIP Protocol: {self.registration.full_name}"


class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ("initiated", "Initiated"),
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    GATEWAY_CHOICES = [
        ("MPESA", "M-Pesa"),
        ("PESAPAL", "Pesapal"),
        ("FLUTTERWAVE", "Flutterwave"),
        ("STRIPE", "Stripe"),
        ("PAYPAL", "PayPal"),
        ("MANUAL", "Manual Payment"),
        ("OTHER", "Other"),
    ]

    registration = models.ForeignKey(
        EventRegistration,
        on_delete=models.CASCADE,
        related_name="payment_transactions",
    )

    gateway = models.CharField(
        max_length=30,
        choices=GATEWAY_CHOICES,
    )

    merchant_reference = models.CharField(
        max_length=150,
        unique=True,
    )

    gateway_reference = models.CharField(
        max_length=150,
        blank=True,
    )

    checkout_request_id = models.CharField(
        max_length=150,
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    currency = models.CharField(
        max_length=3,
        choices=RegistrationCategory.CURRENCY_CHOICES,
    )

    phone_number = models.CharField(
        max_length=30,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="initiated",
    )

    gateway_response = models.JSONField(
        default=dict,
        blank=True,
    )

    failure_reason = models.TextField(blank=True)

    paid_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["merchant_reference"]),
            models.Index(fields=["gateway_reference"]),
            models.Index(fields=["checkout_request_id"]),
            models.Index(fields=["status"]),
        ]

    def clean(self):
        errors = {}

        if self.registration_id:
            if self.currency != self.registration.currency:
                errors["currency"] = (
                    "The payment currency must match the registration currency."
                )

            if self.amount <= Decimal("0.00"):
                errors["amount"] = (
                    "The payment amount must be greater than zero."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.registration_id and not self.currency:
            self.currency = self.registration.currency

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.merchant_reference} - "
            f"{self.gateway} - {self.status}"
        )