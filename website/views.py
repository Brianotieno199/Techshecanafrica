from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EventRegistrationForm, VIPProfileForm
from .models import (
    BlogPost,
    ContactMessage,
    Event,
    EventRegistration,
    GalleryImage,
    PaymentTransaction,
    RegistrationCategory,
    VIPProfile,
)


def home(request):
    posts = BlogPost.objects.filter(
        is_published=True
    )[:3]

    gallery_images = GalleryImage.objects.all()[:6]

    events = Event.objects.filter(
        is_active=True
    )

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not subject or not message:
            messages.error(
                request,
                "Please complete all contact form fields.",
            )

            context = {
                "posts": posts,
                "gallery_images": gallery_images,
                "events": events,
            }

            return render(
                request,
                "website/home.html",
                context,
            )

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        messages.success(
            request,
            "Thank you. Your message has been received.",
        )

        return redirect("home")

    context = {
        "posts": posts,
        "gallery_images": gallery_images,
        "events": events,
    }

    return render(
        request,
        "website/home.html",
        context,
    )


def blog_detail(request, slug):
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        is_published=True,
    )

    context = {
        "post": post,
    }

    return render(
        request,
        "website/blog_detail.html",
        context,
    )


def event_detail(request, event_id):
    event = get_object_or_404(
        Event,
        id=event_id,
        is_active=True,
    )

    categories = (
        RegistrationCategory.objects.filter(
            event=event,
            is_active=True,
        )
        .prefetch_related("contribution_tiers")
        .order_by(
            "display_order",
            "link_id",
        )
    )

    grouped_categories = {}

    for category in categories:
        group_name = category.get_group_display()

        if group_name not in grouped_categories:
            grouped_categories[group_name] = []

        grouped_categories[group_name].append(category)

    context = {
        "event": event,
        "categories": categories,
        "grouped_categories": grouped_categories,
    }

    return render(
        request,
        "website/event_detail.html",
        context,
    )


def event_register(request, event_id=None, link_id=None):
    """
    Handles standard registrations, bookings, sponsorships,
    donations, custom contributions, VIP intake and marketing
    attribution.

    A category can be preselected using either:

        /event/register/<event_id>/<link_id>/

    or:

        ?link=TSC26-REG-01
    """

    if event_id is not None:
        event = get_object_or_404(
            Event,
            id=event_id,
            is_active=True,
        )
    else:
        event = (
            Event.objects.filter(
                is_active=True,
                registration_open=True,
            )
            .order_by("event_date", "created_at")
            .first()
        )

        if event is None:
            messages.error(
                request,
                "No active event is currently available for registration.",
            )

            return redirect("home")

    if not event.registration_open:
        messages.error(
            request,
            "Registration for this event is currently closed.",
        )

        return redirect(
            "event_detail",
            event_id=event.id,
        )

    categories = (
        RegistrationCategory.objects.filter(
            event=event,
            is_active=True,
        )
        .prefetch_related("contribution_tiers")
        .order_by(
            "display_order",
            "link_id",
        )
    )

    category_code = (
        link_id
        or request.GET.get("link", "")
    ).strip()

    selected_category = None

    if category_code:
        selected_category = categories.filter(
            link_id__iexact=category_code
        ).first()

        if selected_category is None:
            messages.warning(
                request,
                "The requested registration or payment option "
                "was not found. Please select an available option.",
            )

    tracking_initial = {
        "utm_source": request.GET.get(
            "utm_source",
            "",
        ).strip(),
        "utm_medium": request.GET.get(
            "utm_medium",
            "",
        ).strip(),
        "utm_campaign": request.GET.get(
            "utm_campaign",
            "",
        ).strip(),
        "utm_content": request.GET.get(
            "utm_content",
            "",
        ).strip(),
        "utm_term": request.GET.get(
            "utm_term",
            "",
        ).strip(),
        "referral_code": request.GET.get(
            "ref",
            request.GET.get(
                "referral_code",
                "",
            ),
        ).strip(),
    }

    if request.method == "POST":
        form = EventRegistrationForm(
            request.POST,
            event=event,
        )

        submitted_category = None
        submitted_category_id = request.POST.get(
            "category_item"
        )

        if submitted_category_id:
            submitted_category = categories.filter(
                pk=submitted_category_id
            ).first()

        is_vip = bool(
            submitted_category
            and submitted_category.is_vip
        )

        vip_form = None

        if is_vip:
            temporary_registration = EventRegistration(
                event=event,
                category_item=submitted_category,
            )

            vip_form = VIPProfileForm(
                request.POST,
                request.FILES,
                registration=temporary_registration,
            )

        standard_form_is_valid = form.is_valid()

        vip_form_is_valid = (
            not is_vip
            or (
                vip_form is not None
                and vip_form.is_valid()
            )
        )

        if standard_form_is_valid and vip_form_is_valid:
            try:
                with transaction.atomic():
                    registration = form.save(
                        commit=False
                    )

                    registration.event = event
                    registration.status = "pending"
                    registration.save()

                    vip_profile = None

                    if is_vip and vip_form is not None:
                        vip_profile = vip_form.save(
                            commit=False
                        )

                        vip_profile.registration = registration
                        vip_profile.save()

                        registration.refresh_from_db()

                    send_registration_confirmation(
                        registration=registration,
                        vip_profile=vip_profile,
                    )

                messages.success(
                    request,
                    (
                        "Your registration information has been "
                        "submitted successfully. Please complete "
                        "payment to confirm your booking."
                    ),
                )

                return redirect(
                    "registration_payment",
                    registration_id=registration.id,
                )

            except Exception:
                messages.error(
                    request,
                    (
                        "We could not complete your registration. "
                        "Please check your information and try again."
                    ),
                )

    else:
        form = EventRegistrationForm(
            event=event,
            initial_category=selected_category,
            initial=tracking_initial,
        )

        vip_form = VIPProfileForm()

    selected_category_from_form = selected_category

    if request.method == "POST":
        submitted_category_id = request.POST.get(
            "category_item"
        )

        if submitted_category_id:
            selected_category_from_form = categories.filter(
                pk=submitted_category_id
            ).first()

    context = {
        "event": event,
        "form": form,
        "vip_form": vip_form,
        "selected_category": selected_category_from_form,
        "categories": categories,
    }

    return render(
        request,
        "website/event_register.html",
        context,
    )


def registration_payment(request, registration_id):
    registration = get_object_or_404(
        EventRegistration.objects.select_related(
            "event",
            "category_item",
            "selected_contribution_tier",
        ),
        id=registration_id,
    )

    if registration.status == "paid":
        return redirect(
            "registration_success",
            registration_id=registration.id,
        )

    payment_methods = {
        "MPESA_TILL": {
            "name": "M-PESA Till",
            "number": "5627312",
            "account": "Jelidata Tech Solutions",
        },
        "ABSA": {
            "name": "ABSA",
            "number": "303030",
            "account": "2053012658",
        },
        "IM_BANK": {
            "name": "I&M Bank",
            "number": "524524",
            "account": "24905",
        },
    }

    if request.method == "POST":
        payment_method = request.POST.get(
            "payment_method",
            "",
        ).strip()

        transaction_reference = request.POST.get(
            "transaction_reference",
            "",
        ).strip()

        if payment_method not in payment_methods:
            messages.error(
                request,
                "Please select a valid payment method.",
            )

        elif not transaction_reference:
            messages.error(
                request,
                "Please enter your payment transaction reference.",
            )

        elif PaymentTransaction.objects.filter(
            gateway_reference__iexact=transaction_reference
        ).exists():
            messages.error(
                request,
                "This payment reference has already been submitted.",
            )

        else:
            merchant_reference = (
                f"MANUAL-{registration.id}-"
                f"{uuid4().hex[:12].upper()}"
            )

            PaymentTransaction.objects.create(
                registration=registration,
                gateway="MANUAL",
                merchant_reference=merchant_reference,
                gateway_reference=transaction_reference,
                amount=registration.amount_payable,
                currency=registration.currency,
                phone_number=registration.phone_number,
                status="pending",
                gateway_response={
                    "payment_method": payment_method,
                    "payment_method_name": (
                        payment_methods[payment_method]["name"]
                    ),
                    "payment_number": (
                        payment_methods[payment_method]["number"]
                    ),
                    "payment_account": (
                        payment_methods[payment_method]["account"]
                    ),
                },
            )

            registration.payment_reference = transaction_reference
            registration.status = "pending"

            registration.save(
                update_fields=[
                    "payment_reference",
                    "status",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                "Your payment information has been submitted successfully. "
                "Your payment is now pending verification.",
            )

            return redirect(
                "registration_success",
                registration_id=registration.id,
            )

    context = {
        "registration": registration,
        "event": registration.event,
        "total_amount": registration.amount_payable,
        "payment_methods": payment_methods,
    }

    return render(
        request,
        "website/registration_payment.html",
        context,
    )


def registration_success(request, registration_id):
    registration = get_object_or_404(
        EventRegistration.objects.select_related(
            "event",
            "category_item",
            "selected_contribution_tier",
        ),
        id=registration_id,
    )

    try:
        vip_profile = registration.vip_profile
    except VIPProfile.DoesNotExist:
        vip_profile = None

    payment_transactions = (
        registration.payment_transactions.all()
        .order_by("-created_at")
    )

    context = {
        "registration": registration,
        "vip_profile": vip_profile,
        "total_amount": registration.amount_payable,
        "event": registration.event,
        "payment_transactions": payment_transactions,
    }

    return render(
        request,
        "website/registration_success.html",
        context,
    )


def send_registration_confirmation(
    registration,
    vip_profile=None,
):
    """
    Sends a registration receipt.

    The registration remains pending until payment is successfully
    processed or manually confirmed by an administrator.
    """

    if not registration.email:
        return

    event = registration.event
    category = registration.category_item

    formatted_date = (
        event.event_date.strftime("%B %d, %Y")
        if event.event_date
        else "To be announced"
    )

    event_location = (
        event.location
        if event.location
        else "Homa Bay"
    )

    vip_text = ""

    if vip_profile is not None:
        vip_text = (
            "\nVIP Intake\n"
            "----------------------------------------\n"
            f"Preferred Address: "
            f"{vip_profile.preferred_address}\n"
            f"Accompanying Aides: "
            f"{vip_profile.accompanying_aides_count}\n"
            f"VIP Fees: KES "
            f"{registration.vip_addons_amount:,.2f}\n"
        )

    subject = (
        f"Registration Received - {event.title}"
    )

    message = (
        f"Hello {registration.full_name},\n\n"
        f"Thank you for registering for {event.title}.\n\n"
        "Registration Details\n"
        "----------------------------------------\n"
        f"Registration ID: TSCA-{registration.id}\n"
        f"Tracking Code: {category.link_id}\n"
        f"Category: {category.name}\n"
        f"Event Date: {formatted_date}\n"
        f"Location: {event_location}\n"
        f"Amount Payable: "
        f"{registration.currency} "
        f"{registration.amount_payable:,.2f}\n"
        f"Payment Status: "
        f"{registration.get_status_display()}\n"
        f"{vip_text}\n"
        "Your information has been received. "
        "Your booking will be confirmed after successful payment.\n\n"
        "Kind regards,\n"
        "TechShe Can Africa"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[
                registration.email,
            ],
            fail_silently=True,
        )
    except Exception:
        pass