from decimal import Decimal

from django import forms

from .models import (
    ContributionTier,
    EventRegistration,
    RegistrationCategory,
    VIPProfile,
)


INPUT_CLASSES = (
    "w-full rounded-lg border border-gray-300 px-4 py-3 "
    "focus:border-blue-600 focus:outline-none "
    "focus:ring-2 focus:ring-blue-200"
)

CHECKBOX_CLASSES = (
    "h-5 w-5 rounded border-gray-300 "
    "text-blue-600 focus:ring-blue-500"
)

FILE_INPUT_CLASSES = (
    "block w-full rounded-lg border border-gray-300 "
    "bg-white px-3 py-2 text-sm "
    "file:mr-4 file:rounded-lg file:border-0 "
    "file:bg-blue-50 file:px-4 file:py-2 "
    "file:text-blue-700 hover:file:bg-blue-100"
)


class EventRegistrationForm(forms.ModelForm):
    selected_contribution_tier = forms.ModelChoiceField(
        queryset=ContributionTier.objects.none(),
        required=False,
        empty_label="Select a suggested contribution",
        widget=forms.Select(
            attrs={
                "class": INPUT_CLASSES,
            }
        ),
        label="Suggested Contribution",
    )

    custom_amount = forms.DecimalField(
        required=False,
        min_value=Decimal("1.00"),
        decimal_places=2,
        max_digits=12,
        widget=forms.NumberInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Enter a custom amount",
                "step": "0.01",
                "min": "1",
            }
        ),
        label="Custom Contribution Amount",
    )

    # Hidden marketing attribution fields
    utm_source = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    utm_medium = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    utm_campaign = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    utm_content = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    utm_term = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    referral_code = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = EventRegistration

        fields = [
            "category_item",
            "selected_contribution_tier",
            "custom_amount",
            "full_name",
            "organization_or_title",
            "phone_number",
            "email",
            "national_id_number",
            "county",
            "sub_county",
            "ward",
            "additional_information",
            "consent_to_record_storage",
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_content",
            "utm_term",
            "referral_code",
        ]

        widgets = {
            "category_item": forms.Select(
                attrs={
                    "class": INPUT_CLASSES,
                }
            ),
            "full_name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Enter your full name",
                    "autocomplete": "name",
                }
            ),
            "organization_or_title": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": (
                        "Organization, company, office, or official title"
                    ),
                    "autocomplete": "organization",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Example: 0712345678 or +254712345678",
                    "autocomplete": "tel",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Enter your email address",
                    "autocomplete": "email",
                }
            ),
            "national_id_number": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "National ID or passport number, if applicable",
                }
            ),
            "county": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Enter your county",
                    "autocomplete": "address-level1",
                }
            ),
            "sub_county": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Enter your sub-county",
                    "autocomplete": "address-level2",
                }
            ),
            "ward": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Enter your ward",
                }
            ),
            "additional_information": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 4,
                    "placeholder": (
                        "Enter accessibility needs or other "
                        "important information"
                    ),
                }
            ),
            "consent_to_record_storage": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASSES,
                }
            ),
        }

        labels = {
            "category_item": "Registration, Booking, or Support Category",
            "full_name": "Full Name",
            "organization_or_title": "Organization / Official Title",
            "phone_number": "Phone Number",
            "email": "Email Address",
            "national_id_number": "National ID or Passport Number",
            "county": "County",
            "sub_county": "Sub-county",
            "ward": "Ward",
            "additional_information": "Additional Information",
            "consent_to_record_storage": (
                "I consent to my information being stored and used "
                "for event registration, payment processing, "
                "communication, and administration."
            ),
        }

    def __init__(
        self,
        *args,
        event=None,
        initial_category=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.event = event

        category_queryset = RegistrationCategory.objects.filter(
            is_active=True
        ).select_related("event")

        if self.event is not None:
            category_queryset = category_queryset.filter(
                event=self.event
            )

        self.fields["category_item"].queryset = category_queryset

        self.fields["organization_or_title"].required = False
        self.fields["national_id_number"].required = False
        self.fields["sub_county"].required = False
        self.fields["ward"].required = False
        self.fields["additional_information"].required = False

        selected_category = None

        if self.is_bound:
            category_id = self.data.get(
                self.add_prefix("category_item")
            )

            if category_id:
                try:
                    selected_category = category_queryset.get(
                        pk=category_id
                    )
                except (
                    RegistrationCategory.DoesNotExist,
                    TypeError,
                    ValueError,
                ):
                    selected_category = None

        elif self.instance.pk and self.instance.category_item_id:
            selected_category = self.instance.category_item

        elif initial_category:
            if isinstance(
                initial_category,
                RegistrationCategory,
            ):
                selected_category = initial_category
            else:
                try:
                    selected_category = category_queryset.get(
                        pk=initial_category
                    )
                except (
                    RegistrationCategory.DoesNotExist,
                    TypeError,
                    ValueError,
                ):
                    try:
                        selected_category = category_queryset.get(
                            link_id=initial_category
                        )
                    except RegistrationCategory.DoesNotExist:
                        selected_category = None

        if selected_category:
            self.fields["category_item"].initial = selected_category

            self.fields[
                "selected_contribution_tier"
            ].queryset = ContributionTier.objects.filter(
                category=selected_category,
                is_active=True,
            ).order_by(
                "display_order",
                "amount",
            )

            if not selected_category.is_custom_amount:
                self.fields[
                    "selected_contribution_tier"
                ].widget = forms.HiddenInput()

                self.fields[
                    "custom_amount"
                ].widget = forms.HiddenInput()

        else:
            self.fields[
                "selected_contribution_tier"
            ].queryset = ContributionTier.objects.filter(
                category__in=category_queryset,
                is_active=True,
            ).select_related(
                "category"
            ).order_by(
                "category__display_order",
                "display_order",
                "amount",
            )

    def clean_phone_number(self):
        phone_number = (
            (self.cleaned_data.get("phone_number") or "")
            .strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        if phone_number.startswith("+"):
            digits = phone_number[1:]
        else:
            digits = phone_number

        if not digits.isdigit():
            raise forms.ValidationError(
                "Enter a valid phone number using numbers only."
            )

        if len(digits) < 9 or len(digits) > 15:
            raise forms.ValidationError(
                "Enter a valid phone number containing 9 to 15 digits."
            )

        return phone_number

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()

        if not email:
            raise forms.ValidationError(
                "Enter your email address."
            )

        return email

    def clean_national_id_number(self):
        national_id_number = (
            (self.cleaned_data.get("national_id_number") or "")
            .strip()
            .upper()
        )

        if not national_id_number:
            return ""

        if self.event:
            duplicate = EventRegistration.objects.filter(
                event=self.event,
                national_id_number=national_id_number,
            )

            if self.instance.pk:
                duplicate = duplicate.exclude(
                    pk=self.instance.pk
                )

            if duplicate.exists():
                raise forms.ValidationError(
                    "This ID or passport number is already "
                    "registered for this event."
                )

        return national_id_number

    def clean(self):
        cleaned_data = super().clean()

        category_item = cleaned_data.get("category_item")
        selected_tier = cleaned_data.get(
            "selected_contribution_tier"
        )
        custom_amount = cleaned_data.get("custom_amount")

        if not category_item:
            return cleaned_data

        if self.event and category_item.event_id != self.event.id:
            self.add_error(
                "category_item",
                "The selected category is not available for this event.",
            )

        if not category_item.is_active:
            self.add_error(
                "category_item",
                "The selected category is no longer available.",
            )

        if selected_tier:
            if selected_tier.category_id != category_item.id:
                self.add_error(
                    "selected_contribution_tier",
                    "The selected contribution does not belong "
                    "to this category.",
                )

            if not selected_tier.is_active:
                self.add_error(
                    "selected_contribution_tier",
                    "The selected contribution is no longer available.",
                )

        if category_item.is_custom_amount:
            if selected_tier and custom_amount is not None:
                self.add_error(
                    "custom_amount",
                    "Choose a suggested contribution or enter "
                    "a custom amount, not both.",
                )

            if (
                not selected_tier
                and custom_amount is None
                and category_item.base_price <= Decimal("0.00")
            ):
                self.add_error(
                    "custom_amount",
                    "Select a suggested contribution or enter "
                    "a custom amount.",
                )

            if (
                custom_amount is not None
                and category_item.base_price > Decimal("0.00")
                and custom_amount < category_item.base_price
            ):
                self.add_error(
                    "custom_amount",
                    (
                        "The minimum contribution for this option is "
                        f"{category_item.currency} "
                        f"{category_item.base_price:,.2f}."
                    ),
                )

        else:
            if selected_tier:
                self.add_error(
                    "selected_contribution_tier",
                    "Suggested contribution tiers are not available "
                    "for this category.",
                )

            if custom_amount is not None:
                self.add_error(
                    "custom_amount",
                    "A custom amount is not allowed for this category.",
                )

            cleaned_data["selected_contribution_tier"] = None
            cleaned_data["custom_amount"] = None

        return cleaned_data

    def save(self, commit=True):
        registration = super().save(commit=False)

        if self.event is not None:
            registration.event = self.event
        elif registration.category_item_id:
            registration.event = registration.category_item.event

        registration.currency = registration.category_item.currency

        if commit:
            registration.save()
            self.save_m2m()

        return registration


class VIPProfileForm(forms.ModelForm):
    class Meta:
        model = VIPProfile

        fields = [
            "preferred_address",
            "official_bio",
            "headshot",
            "passport_or_id",
            "security_detail_size",
            "vehicle_details",
            "parking_requirements",
            "arrival_date",
            "arrival_time",
            "departure_date",
            "departure_time",
            "transport_coordination_needed",
            "transport_coordination_details",
            "dietary_requirements",
            "accommodation_needed",
            "accommodation_details",
            "accompanying_aides_count",
            "add_on_meet_greet",
            "add_on_stage_shoutout",
            "is_speaking",
            "speaking_or_presentation_notes",
            "specific_request",
        ]

        widgets = {
            "preferred_address": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": (
                        "Example: Hon., H.E., Ambassador, Dr."
                    ),
                }
            ),
            "official_bio": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 5,
                    "placeholder": (
                        "Enter a short official biography for the "
                        "programme booklet and media mentions"
                    ),
                }
            ),
            "headshot": forms.FileInput(
                attrs={
                    "class": FILE_INPUT_CLASSES,
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),
            "passport_or_id": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": (
                        "Passport, national ID, or diplomatic ID number"
                    ),
                }
            ),
            "security_detail_size": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "0",
                    "min": "0",
                }
            ),
            "vehicle_details": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 3,
                    "placeholder": (
                        "Vehicle type, registration numbers, "
                        "motorcade, or security vehicle details"
                    ),
                }
            ),
            "parking_requirements": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 3,
                    "placeholder": (
                        "Enter parking or motorcade space requirements"
                    ),
                }
            ),
            "arrival_date": forms.DateInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "type": "date",
                }
            ),
            "arrival_time": forms.TimeInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "type": "time",
                }
            ),
            "departure_date": forms.DateInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "type": "date",
                }
            ),
            "departure_time": forms.TimeInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "type": "time",
                }
            ),
            "transport_coordination_needed": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASSES,
                }
            ),
            "transport_coordination_details": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 3,
                    "placeholder": (
                        "Enter airport pickup, transport, flight, "
                        "or coordination details"
                    ),
                }
            ),
            "dietary_requirements": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": (
                        "Enter dietary preferences, allergies, "
                        "or restrictions"
                    ),
                }
            ),
            "accommodation_needed": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASSES,
                }
            ),
            "accommodation_details": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 3,
                    "placeholder": (
                        "Enter accommodation dates, room needs, "
                        "or other requirements"
                    ),
                }
            ),
            "accompanying_aides_count": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "0",
                    "min": "0",
                }
            ),
            "add_on_meet_greet": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASSES,
                }
            ),
            "add_on_stage_shoutout": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASSES,
                }
            ),
            "is_speaking": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASSES,
                }
            ),
            "speaking_or_presentation_notes": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 4,
                    "placeholder": (
                        "Enter speaking topic, session, presentation, "
                        "or technical requirements"
                    ),
                }
            ),
            "specific_request": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 4,
                    "placeholder": (
                        "Enter any partnership announcement, "
                        "recognition, protocol, or programme request"
                    ),
                }
            ),
        }

        labels = {
            "preferred_address": "Preferred Form of Address",
            "official_bio": "Short Official Biography",
            "headshot": "Official Headshot",
            "passport_or_id": "Passport / National ID / Diplomatic ID",
            "security_detail_size": "Number of Security Personnel",
            "vehicle_details": "Vehicle / Motorcade Details",
            "parking_requirements": "Parking Requirements",
            "arrival_date": "Arrival Date",
            "arrival_time": "Arrival Time",
            "departure_date": "Departure Date",
            "departure_time": "Departure Time",
            "transport_coordination_needed": (
                "I require transport or airport coordination"
            ),
            "transport_coordination_details": (
                "Transport Coordination Details"
            ),
            "dietary_requirements": "Dietary Requirements",
            "accommodation_needed": (
                "I require accommodation assistance"
            ),
            "accommodation_details": "Accommodation Details",
            "accompanying_aides_count": (
                "Number of Accompanying Aides or Staff"
            ),
            "add_on_meet_greet": (
                "Private Meet-and-Greet Slot — KSh 15,000"
            ),
            "add_on_stage_shoutout": (
                "On-Stage Recognition or Shout-Out — KSh 10,000"
            ),
            "is_speaking": (
                "I will be speaking or presenting"
            ),
            "speaking_or_presentation_notes": (
                "Speaking or Presentation Details"
            ),
            "specific_request": "Specific Programme Request",
        }

    def __init__(
        self,
        *args,
        registration=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.registration = registration

        optional_fields = [
            "official_bio",
            "headshot",
            "passport_or_id",
            "security_detail_size",
            "vehicle_details",
            "parking_requirements",
            "arrival_date",
            "arrival_time",
            "departure_date",
            "departure_time",
            "transport_coordination_details",
            "dietary_requirements",
            "accommodation_details",
            "accompanying_aides_count",
            "speaking_or_presentation_notes",
            "specific_request",
        ]

        for field_name in optional_fields:
            self.fields[field_name].required = False

        if registration is None and self.instance.pk:
            registration = self.instance.registration
            self.registration = registration

        if registration and registration.category_item_id:
            category_name = registration.category_item.name.lower()

            passport_required = any(
                keyword in category_name
                for keyword in [
                    "diplomat",
                    "embassy",
                    "international delegate",
                ]
            )

            if passport_required:
                self.fields["passport_or_id"].required = True

                self.fields[
                    "passport_or_id"
                ].help_text = (
                    "Required for diplomats and "
                    "international delegates."
                )

    def clean_headshot(self):
        headshot = self.cleaned_data.get("headshot")

        if not headshot:
            return headshot

        maximum_size = 5 * 1024 * 1024

        if headshot.size > maximum_size:
            raise forms.ValidationError(
                "The headshot must be 5 MB or smaller."
            )

        allowed_content_types = [
            "image/jpeg",
            "image/png",
            "image/webp",
        ]

        content_type = getattr(
            headshot,
            "content_type",
            None,
        )

        if (
            content_type
            and content_type not in allowed_content_types
        ):
            raise forms.ValidationError(
                "Upload a JPG, PNG, or WebP image."
            )

        return headshot

    def clean_passport_or_id(self):
        passport_or_id = (
            (self.cleaned_data.get("passport_or_id") or "")
            .strip()
            .upper()
        )

        return passport_or_id

    def clean(self):
        cleaned_data = super().clean()

        registration = self.registration

        if registration and not registration.category_item.is_vip:
            raise forms.ValidationError(
                "VIP information can only be submitted "
                "for a VIP registration category."
            )

        accommodation_needed = cleaned_data.get(
            "accommodation_needed"
        )

        accommodation_details = (cleaned_data.get(
            "accommodation_details"
        ) or "").strip()

        if accommodation_needed and not accommodation_details:
            self.add_error(
                "accommodation_details",
                "Enter the accommodation assistance required.",
            )

        transport_needed = cleaned_data.get(
            "transport_coordination_needed"
        )

        transport_details = (cleaned_data.get(
            "transport_coordination_details"
        ) or "").strip()

        if transport_needed and not transport_details:
            self.add_error(
                "transport_coordination_details",
                "Enter the transport or airport coordination required.",
            )

        arrival_date = cleaned_data.get("arrival_date")
        arrival_time = cleaned_data.get("arrival_time")
        departure_date = cleaned_data.get("departure_date")
        departure_time = cleaned_data.get("departure_time")

        if arrival_time and not arrival_date:
            self.add_error(
                "arrival_date",
                "Select an arrival date when providing an arrival time.",
            )

        if departure_time and not departure_date:
            self.add_error(
                "departure_date",
                "Select a departure date when providing a departure time.",
            )

        if (
            arrival_date
            and departure_date
            and departure_date < arrival_date
        ):
            self.add_error(
                "departure_date",
                "The departure date cannot be before the arrival date.",
            )

        is_speaking = cleaned_data.get("is_speaking")

        speaking_notes = (cleaned_data.get(
            "speaking_or_presentation_notes"
        ) or "").strip()

        if is_speaking and not speaking_notes:
            self.add_error(
                "speaking_or_presentation_notes",
                "Provide the speaking or presentation details.",
            )

        return cleaned_data

    def save(self, commit=True):
        vip_profile = super().save(commit=False)

        if self.registration is not None:
            vip_profile.registration = self.registration

        if commit:
            vip_profile.save()

        return vip_profile