


import csv
from decimal import Decimal

from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone

from .models import (
    BlogPost,
    ContactMessage,
    ContributionTier,
    Event,
    EventRegistration,
    GalleryImage,
    PaymentTransaction,
    RegistrationCategory,
    VIPProfile,
)


def send_payment_confirmation_email(registration):
    """
    Send a payment-confirmation email after payment has been verified.
    Returns True when the email is sent successfully, otherwise False.
    """

    if not registration.email:
        return False

    event = registration.event
    category = registration.category_item

    transaction_reference = (
        registration.payment_reference or "Not provided"
    )

    subject = f"Payment Confirmed - {event.title}"

    message = (
        f"Hello {registration.full_name},\n\n"
        "Payment Confirmed!\n\n"
        f"We are pleased to confirm that your payment for "
        f"{event.title} has been successfully verified.\n\n"
        "Registration Details\n"
        "----------------------------------------\n"
        f"Registration ID: TSCA-{registration.id}\n"
        f"Category: {category.name}\n"
        f"Amount Paid: {registration.currency} "
        f"{registration.amount_payable:,.2f}\n"
        f"Transaction Reference: {transaction_reference}\n"
        "Payment Status: PAID / CONFIRMED\n\n"
        "Your registration is now fully confirmed.\n\n"
        "Please keep this email for your records.\n\n"
        "Thank you for registering with TechShe Can Africa. "
        "We look forward to welcoming you.\n\n"
        "Kind regards,\n"
        "TechShe Can Africa"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            fail_silently=False,
        )
        return True
    except Exception:
        return False


def mark_latest_manual_transaction_successful(registration):
    """
    Mark the newest pending manual payment transaction as successful.
    """

    payment_transaction = (
        registration.payment_transactions.filter(
            gateway="MANUAL",
            status="pending",
        )
        .order_by("-created_at")
        .first()
    )

    if payment_transaction is None:
        return None

    payment_transaction.status = "successful"

    if payment_transaction.paid_at is None:
        payment_transaction.paid_at = timezone.now()

    payment_transaction.save(
        update_fields=[
            "status",
            "paid_at",
            "updated_at",
        ]
    )

    if payment_transaction.gateway_reference:
        registration.payment_reference = (
            payment_transaction.gateway_reference
        )
        registration.save(
            update_fields=[
                "payment_reference",
                "updated_at",
            ]
        )

    return payment_transaction


# ==========================================
# INLINE ADMIN CLASSES
# ==========================================


class ContributionTierInline(admin.TabularInline):
    model = ContributionTier
    extra = 0

    fields = (
        "name",
        "amount",
        "description",
        "display_order",
        "is_active",
    )

    ordering = (
        "display_order",
        "amount",
    )


class VIPProfileInline(admin.StackedInline):
    model = VIPProfile
    can_delete = False
    verbose_name = "VIP Profile"
    verbose_name_plural = "VIP Profile Details"
    fk_name = "registration"
    extra = 0

    readonly_fields = (
        "aides_fee_charged",
        "add_on_fee_charged",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Identity and Protocol",
            {
                "fields": (
                    "preferred_address",
                    "official_bio",
                    "headshot",
                    "passport_or_id",
                )
            },
        ),
        (
            "Security and Logistics",
            {
                "fields": (
                    "security_detail_size",
                    "vehicle_details",
                    "parking_requirements",
                    (
                        "arrival_date",
                        "arrival_time",
                    ),
                    (
                        "departure_date",
                        "departure_time",
                    ),
                    "transport_coordination_needed",
                    "transport_coordination_details",
                    (
                        "security_notification_required",
                        "security_notification_completed",
                    ),
                )
            },
        ),
        (
            "Hospitality",
            {
                "fields": (
                    "dietary_requirements",
                    "accommodation_needed",
                    "accommodation_details",
                    "accompanying_aides_count",
                    "aides_fee_charged",
                )
            },
        ),
        (
            "VIP Add-ons",
            {
                "fields": (
                    (
                        "add_on_meet_greet",
                        "add_on_stage_shoutout",
                    ),
                    "add_on_fee_charged",
                )
            },
        ),
        (
            "Programme and Administration",
            {
                "fields": (
                    "is_speaking",
                    "speaking_or_presentation_notes",
                    "specific_request",
                    "rsvp_deadline",
                    "assigned_liaison",
                )
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    can_delete = False

    fields = (
        "merchant_reference",
        "gateway",
        "amount",
        "currency",
        "status",
        "gateway_reference",
        "paid_at",
        "created_at",
    )

    readonly_fields = (
        "merchant_reference",
        "gateway",
        "amount",
        "currency",
        "gateway_reference",
        "paid_at",
        "created_at",
    )

    show_change_link = True


# ==========================================
# CONTENT ADMIN
# ==========================================


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "is_published",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_published",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "title",
        "excerpt",
        "content",
        "author",
    )

    prepopulated_fields = {
        "slug": (
            "title",
        )
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "event_date",
        "location",
        "registration_open",
        "is_active",
        "registration_count",
        "category_count",
        "created_at",
    )

    list_filter = (
        "registration_open",
        "is_active",
        "event_date",
        "created_at",
    )

    search_fields = (
        "title",
        "location",
        "description",
    )

    prepopulated_fields = {
        "slug": (
            "title",
        )
    }

    readonly_fields = (
        "created_at",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "registrations",
                "registration_categories",
            )
        )

    @admin.display(description="Registrations")
    def registration_count(self, obj):
        return obj.registrations.count()

    @admin.display(description="Categories")
    def category_count(self, obj):
        return obj.registration_categories.count()


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "subject",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "subject",
        "message",
    )

    readonly_fields = (
        "created_at",
    )

    list_editable = (
        "is_read",
    )


# ==========================================
# REGISTRATION CATEGORY ADMIN
# ==========================================


@admin.register(RegistrationCategory)
class RegistrationCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "link_id",
        "name",
        "event",
        "group",
        "display_price",
        "currency",
        "is_vip",
        "is_custom_amount",
        "display_order",
        "is_active",
    )

    list_filter = (
        "event",
        "group",
        "currency",
        "is_vip",
        "is_custom_amount",
        "is_active",
    )

    search_fields = (
        "link_id",
        "name",
        "description",
        "event__title",
    )

    ordering = (
        "event",
        "display_order",
        "link_id",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    prepopulated_fields = {
        "slug": (
            "name",
        )
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [
        ContributionTierInline,
    ]

    fieldsets = (
        (
            "Category Information",
            {
                "fields": (
                    "event",
                    "link_id",
                    "name",
                    "slug",
                    "description",
                    "group",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "base_price",
                    "currency",
                    "is_custom_amount",
                )
            },
        ),
        (
            "Form and Display Settings",
            {
                "fields": (
                    "is_vip",
                    "requires_standard_registration_fields",
                    "display_order",
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(description="Price")
    def display_price(self, obj):
        if obj.is_custom_amount and obj.base_price == Decimal("0.00"):
            return "Custom amount"

        return f"{obj.currency} {obj.base_price:,.2f}"


@admin.register(ContributionTier)
class ContributionTierAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "display_amount",
        "display_order",
        "is_active",
    )

    list_filter = (
        "category__event",
        "category",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
        "category__name",
        "category__link_id",
    )

    ordering = (
        "category",
        "display_order",
        "amount",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    readonly_fields = (
        "created_at",
    )

    @admin.display(description="Amount")
    def display_amount(self, obj):
        return f"{obj.category.currency} {obj.amount:,.2f}"


# ==========================================
# EVENT REGISTRATION ADMIN
# ==========================================


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "event",
        "category_item",
        "is_vip_registration",
        "phone_number",
        "email",
        "display_total_fee",
        "currency",
        "status",
        "created_at",
    )

    list_filter = (
        "event",
        "status",
        "category_item__group",
        "category_item",
        "category_item__is_vip",
        "currency",
        "county",
        "utm_source",
        "created_at",
    )

    search_fields = (
        "full_name",
        "organization_or_title",
        "national_id_number",
        "phone_number",
        "email",
        "payment_reference",
        "county",
        "sub_county",
        "ward",
        "category_item__name",
        "category_item__link_id",
        "referral_code",
        "vip_profile__preferred_address",
        "vip_profile__passport_or_id",
        "vip_profile__assigned_liaison",
    )

    readonly_fields = (
        "base_amount",
        "vip_addons_amount",
        "amount_payable",
        "currency",
        "created_at",
        "updated_at",
    )

    list_per_page = 25
    date_hierarchy = "created_at"

    inlines = [
        VIPProfileInline,
        PaymentTransactionInline,
    ]

    fieldsets = (
        (
            "Registration Information",
            {
                "fields": (
                    "event",
                    "category_item",
                    "selected_contribution_tier",
                    "custom_amount",
                    "full_name",
                    "organization_or_title",
                    "email",
                    "phone_number",
                    "national_id_number",
                )
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "county",
                    "sub_county",
                    "ward",
                )
            },
        ),
        (
            "Financial Information",
            {
                "fields": (
                    "base_amount",
                    "vip_addons_amount",
                    "amount_payable",
                    "currency",
                    "payment_reference",
                    "status",
                )
            },
        ),
        (
            "Additional Information and Consent",
            {
                "fields": (
                    "additional_information",
                    "consent_to_record_storage",
                )
            },
        ),
        (
            "Marketing Attribution",
            {
                "classes": ("collapse",),
                "fields": (
                    "utm_source",
                    "utm_medium",
                    "utm_campaign",
                    "utm_content",
                    "utm_term",
                    "referral_code",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    actions = (
        "mark_as_paid",
        "mark_as_attended",
        "mark_as_cancelled",
        "mark_as_refunded",
        "export_selected_registrations",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "event",
                "category_item",
                "selected_contribution_tier",
                "vip_profile",
            )
        )

    @admin.display(boolean=True, description="VIP")
    def is_vip_registration(self, obj):
        return bool(
            obj.category_item
            and obj.category_item.is_vip
        )

    @admin.display(description="Total Payable")
    def display_total_fee(self, obj):
        amount = obj.amount_payable or Decimal("0.00")
        currency = obj.currency or "KES"

        return f"{currency} {amount:,.2f}"

    def save_model(self, request, obj, form, change):
        previous_status = None

        if change and obj.pk:
            previous_status = (
                EventRegistration.objects.filter(pk=obj.pk)
                .values_list("status", flat=True)
                .first()
            )

        super().save_model(request, obj, form, change)

        if obj.status == "paid" and previous_status != "paid":
            mark_latest_manual_transaction_successful(obj)

            email_sent = send_payment_confirmation_email(obj)

            if email_sent:
                self.message_user(
                    request,
                    "Payment confirmed and confirmation email sent successfully.",
                )
            else:
                self.message_user(
                    request,
                    "Payment was confirmed, but the confirmation email "
                    "could not be sent.",
                    level="warning",
                )

    @admin.action(
        description="Confirm payment and email selected registrations"
    )
    def mark_as_paid(self, request, queryset):
        confirmed_count = 0
        email_count = 0
        already_paid_count = 0

        registrations = queryset.select_related(
            "event",
            "category_item",
        )

        for registration in registrations:
            if registration.status == "paid":
                already_paid_count += 1
                continue

            with transaction.atomic():
                registration.status = "paid"
                registration.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                mark_latest_manual_transaction_successful(
                    registration
                )

                email_sent = send_payment_confirmation_email(
                    registration
                )

            confirmed_count += 1

            if email_sent:
                email_count += 1

        message = (
            f"{confirmed_count} registration(s) marked as paid. "
            f"{email_count} payment confirmation email(s) sent."
        )

        if already_paid_count:
            message += (
                f" {already_paid_count} already-paid registration(s) "
                "were skipped."
            )

        self.message_user(
            request,
            message,
        )

    @admin.action(description="Mark selected registrations as attended")
    def mark_as_attended(self, request, queryset):
        updated = queryset.update(status="attended")

        self.message_user(
            request,
            f"{updated} registration(s) marked as attended.",
        )

    @admin.action(description="Mark selected registrations as cancelled")
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status="cancelled")

        self.message_user(
            request,
            f"{updated} registration(s) marked as cancelled.",
        )

    @admin.action(description="Mark selected registrations as refunded")
    def mark_as_refunded(self, request, queryset):
        updated = queryset.update(status="refunded")

        self.message_user(
            request,
            f"{updated} registration(s) marked as refunded.",
        )

    @admin.action(
        description="Export selected registrations to CSV"
    )
    def export_selected_registrations(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv"
        )

        response["Content-Disposition"] = (
            'attachment; '
            'filename="event_registrations_detailed.csv"'
        )

        writer = csv.writer(response)

        writer.writerow(
            [
                "Registration ID",
                "Event",
                "Link ID",
                "Category",
                "Category Group",
                "Full Name",
                "Organization / Title",
                "National ID / Passport",
                "Phone Number",
                "Email",
                "Is VIP",
                "Selected Contribution Tier",
                "Custom Amount",
                "Base Amount",
                "VIP Add-ons Amount",
                "Total Amount Payable",
                "Currency",
                "Payment Reference",
                "County",
                "Sub-county",
                "Ward",
                "Status",
                "Preferred Address",
                "VIP Passport / ID",
                "Security Detail Size",
                "Vehicle Details",
                "Parking Requirements",
                "Arrival Date",
                "Arrival Time",
                "Departure Date",
                "Departure Time",
                "Accommodation Needed",
                "Accompanying Aides",
                "Aides Fee",
                "Meet-and-Greet",
                "Stage Shout-Out",
                "VIP Add-on Fee",
                "Speaker / Presenter",
                "Assigned Liaison",
                "UTM Source",
                "UTM Medium",
                "UTM Campaign",
                "UTM Content",
                "UTM Term",
                "Referral Code",
                "Registration Date",
            ]
        )

        registrations = queryset.select_related(
            "event",
            "category_item",
            "selected_contribution_tier",
            "vip_profile",
        )

        for registration in registrations:
            event_title = (
                registration.event.title
                if registration.event
                else ""
            )

            category = registration.category_item

            category_name = (
                category.name
                if category
                else ""
            )

            category_link_id = (
                category.link_id
                if category
                else ""
            )

            category_group = (
                category.get_group_display()
                if category
                else ""
            )

            is_vip = bool(
                category
                and category.is_vip
            )

            contribution_tier = (
                registration.selected_contribution_tier.name
                if registration.selected_contribution_tier
                else ""
            )

            vip = None

            try:
                vip = registration.vip_profile
            except VIPProfile.DoesNotExist:
                vip = None

            preferred_address = ""
            vip_passport_or_id = ""
            security_detail_size = 0
            vehicle_details = ""
            parking_requirements = ""
            arrival_date = ""
            arrival_time = ""
            departure_date = ""
            departure_time = ""
            accommodation_needed = "No"
            accompanying_aides = 0
            aides_fee = Decimal("0.00")
            meet_greet = "No"
            stage_shoutout = "No"
            vip_add_on_fee = Decimal("0.00")
            is_speaking = "No"
            assigned_liaison = ""

            if vip:
                preferred_address = vip.preferred_address or ""
                vip_passport_or_id = vip.passport_or_id or ""
                security_detail_size = vip.security_detail_size or 0
                vehicle_details = vip.vehicle_details or ""
                parking_requirements = vip.parking_requirements or ""

                arrival_date = (
                    vip.arrival_date.strftime("%Y-%m-%d")
                    if vip.arrival_date
                    else ""
                )

                arrival_time = (
                    vip.arrival_time.strftime("%H:%M")
                    if vip.arrival_time
                    else ""
                )

                departure_date = (
                    vip.departure_date.strftime("%Y-%m-%d")
                    if vip.departure_date
                    else ""
                )

                departure_time = (
                    vip.departure_time.strftime("%H:%M")
                    if vip.departure_time
                    else ""
                )

                accommodation_needed = (
                    "Yes"
                    if vip.accommodation_needed
                    else "No"
                )

                accompanying_aides = (
                    vip.accompanying_aides_count or 0
                )

                aides_fee = (
                    vip.aides_fee_charged
                    or Decimal("0.00")
                )

                meet_greet = (
                    "Yes"
                    if vip.add_on_meet_greet
                    else "No"
                )

                stage_shoutout = (
                    "Yes"
                    if vip.add_on_stage_shoutout
                    else "No"
                )

                vip_add_on_fee = (
                    vip.add_on_fee_charged
                    or Decimal("0.00")
                )

                is_speaking = (
                    "Yes"
                    if vip.is_speaking
                    else "No"
                )

                assigned_liaison = (
                    vip.assigned_liaison or ""
                )

            writer.writerow(
                [
                    f"TSCA-{registration.id}",
                    event_title,
                    category_link_id,
                    category_name,
                    category_group,
                    registration.full_name,
                    registration.organization_or_title,
                    registration.national_id_number or "",
                    registration.phone_number,
                    registration.email,
                    "Yes" if is_vip else "No",
                    contribution_tier,
                    (
                        f"{registration.custom_amount:,.2f}"
                        if registration.custom_amount is not None
                        else ""
                    ),
                    f"{registration.base_amount:,.2f}",
                    f"{registration.vip_addons_amount:,.2f}",
                    f"{registration.amount_payable:,.2f}",
                    registration.currency,
                    registration.payment_reference or "",
                    registration.county,
                    registration.sub_county,
                    registration.ward,
                    registration.get_status_display(),
                    preferred_address,
                    vip_passport_or_id,
                    security_detail_size,
                    vehicle_details,
                    parking_requirements,
                    arrival_date,
                    arrival_time,
                    departure_date,
                    departure_time,
                    accommodation_needed,
                    accompanying_aides,
                    f"{aides_fee:,.2f}",
                    meet_greet,
                    stage_shoutout,
                    f"{vip_add_on_fee:,.2f}",
                    is_speaking,
                    assigned_liaison,
                    registration.utm_source,
                    registration.utm_medium,
                    registration.utm_campaign,
                    registration.utm_content,
                    registration.utm_term,
                    registration.referral_code,
                    registration.created_at.strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                ]
            )

        return response


# ==========================================
# VIP PROFILE ADMIN
# ==========================================


@admin.register(VIPProfile)
class VIPProfileAdmin(admin.ModelAdmin):
    list_display = (
        "registration",
        "preferred_address",
        "security_detail_size",
        "accompanying_aides_count",
        "display_vip_fees",
        "is_speaking",
        "assigned_liaison",
        "updated_at",
    )

    list_filter = (
        "is_speaking",
        "accommodation_needed",
        "transport_coordination_needed",
        "security_notification_required",
        "security_notification_completed",
        "add_on_meet_greet",
        "add_on_stage_shoutout",
    )

    search_fields = (
        "registration__full_name",
        "registration__email",
        "registration__phone_number",
        "preferred_address",
        "passport_or_id",
        "vehicle_details",
        "assigned_liaison",
    )

    readonly_fields = (
        "aides_fee_charged",
        "add_on_fee_charged",
        "created_at",
        "updated_at",
    )

    @admin.display(description="VIP Fees")
    def display_vip_fees(self, obj):
        total = (
            obj.aides_fee_charged
            + obj.add_on_fee_charged
        )

        return f"KES {total:,.2f}"


# ==========================================
# PAYMENT TRANSACTION ADMIN
# ==========================================


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "merchant_reference",
        "registration",
        "gateway",
        "display_amount",
        "status",
        "gateway_reference",
        "paid_at",
        "created_at",
    )

    list_filter = (
        "gateway",
        "status",
        "currency",
        "paid_at",
        "created_at",
    )

    search_fields = (
        "merchant_reference",
        "gateway_reference",
        "checkout_request_id",
        "registration__full_name",
        "registration__email",
        "registration__phone_number",
        "phone_number",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Payment Information",
            {
                "fields": (
                    "registration",
                    "gateway",
                    "merchant_reference",
                    "gateway_reference",
                    "checkout_request_id",
                    "amount",
                    "currency",
                    "phone_number",
                    "status",
                    "paid_at",
                )
            },
        ),
        (
            "Gateway Response",
            {
                "classes": ("collapse",),
                "fields": (
                    "gateway_response",
                    "failure_reason",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        previous_status = None

        if change and obj.pk:
            previous_status = (
                PaymentTransaction.objects.filter(pk=obj.pk)
                .values_list("status", flat=True)
                .first()
            )

        if (
            obj.status == "successful"
            and previous_status != "successful"
            and obj.paid_at is None
        ):
            obj.paid_at = timezone.now()

        super().save_model(request, obj, form, change)

        if obj.status == "successful" and previous_status != "successful":
            registration = obj.registration

            registration.status = "paid"

            if obj.gateway_reference:
                registration.payment_reference = (
                    obj.gateway_reference
                )

            registration.save(
                update_fields=[
                    "status",
                    "payment_reference",
                    "updated_at",
                ]
            )

            email_sent = send_payment_confirmation_email(
                registration
            )

            if email_sent:
                self.message_user(
                    request,
                    "Payment confirmed and confirmation email sent successfully.",
                )
            else:
                self.message_user(
                    request,
                    "Payment was confirmed, but the confirmation email "
                    "could not be sent.",
                    level="warning",
                )

    @admin.display(description="Amount")
    def display_amount(self, obj):
        return f"{obj.currency} {obj.amount:,.2f}"