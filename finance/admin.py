from django.contrib import admin
from .models import (
    StudentFocus,
    StudentRegistration,
    Fee,
    StudentFee,
    FeeAccountNumber,
    PayFee,
    WhatsAppMessage,
    ChangeLog,
    Discount,
    SmsConfiguration,
    WebhookConfiguration,
    CreatePayment,
    WhatsAppSetting
)

@admin.register(StudentFocus)
class StudentFocusAdmin(admin.ModelAdmin):
    list_display = ('student', 'focus', 'user')
    list_filter = ('focus', 'user')
    search_fields = ('student__fullName', 'focus')
    raw_id_fields = ('student', 'user')

@admin.register(StudentRegistration)
class StudentRegistrationAdmin(admin.ModelAdmin):
    list_display = ('studentfocus', 'joined_date', 'initial_payment', 'user')
    list_filter = ('joined_date', 'user')
    search_fields = ('studentfocus__student__fullName', 'studentfocus__focus')
    date_hierarchy = 'joined_date'
    raw_id_fields = ('studentfocus', 'user')

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('fee_name', 'teacherclass', 'created_at', 'updated_at', 'user')
    list_filter = ('created_at', 'user')
    search_fields = ('fee_name', 'teacherclass__ClassName__class_name')
    date_hierarchy = 'created_at'
    raw_id_fields = ('teacherclass', 'user')

@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee', 'teacherclass', 'amount_required', 'start_date', 'end_date', 'assigned_date')
    list_filter = ('start_date', 'end_date', 'user')
    search_fields = ('student__fullName', 'fee__fee_name', 'teacherclass__ClassName__class_name')
    date_hierarchy = 'assigned_date'
    raw_id_fields = ('student', 'fee', 'teacherclass', 'user')

@admin.register(FeeAccountNumber)
class FeeAccountNumberAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'account_name', 'is_active', 'fee', 'teacherclass', 'user')
    list_filter = ('is_active', 'user')
    search_fields = ('account_number', 'account_name', 'fee__fee_name')
    raw_id_fields = ('fee', 'teacherclass', 'user')

@admin.register(PayFee)
class PayFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee', 'amount_paid', 'payment_method', 'payment_reference', 'date_paid', 'user')
    list_filter = ('date_paid', 'payment_method', 'user')
    search_fields = ('student__fullName', 'fee__fee_name', 'payer_account_no', 'payment_reference')
    date_hierarchy = 'date_paid'
    raw_id_fields = ('student', 'fee', 'user')


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('payment', 'student', 'phone_number', 'status', 'msg_id', 'created_at', 'user')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('student__fullName', 'payment__payment_reference', 'phone_number', 'msg_id', 'message')
    date_hierarchy = 'created_at'
    raw_id_fields = ('payment', 'student', 'user')

@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'created_at')
    list_filter = ('action', 'model_name', 'created_at')
    search_fields = ('user__username', 'model_name', 'description')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee', 'teacherclass', 'discount_amount', 'user')
    list_filter = ('user',)
    search_fields = ('student__fullName', 'fee__fee_name', 'teacherclass__ClassName__class_name')
    raw_id_fields = ('student', 'fee', 'teacherclass', 'user')


@admin.register(SmsConfiguration)
class SmsConfigurationAdmin(admin.ModelAdmin):
    list_display = ("user", "source_addr", "url_required")
    search_fields = ("user__username", "source_addr", "url_required")


@admin.register(WebhookConfiguration)
class WebhookConfigurationAdmin(admin.ModelAdmin):
    list_display = ("name", "webhook_url")
    search_fields = ("name", "webhook_url")


from django.contrib import admin
from .models import StudentPayment, PaymentTransaction, CreatePayment


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    fields = (
        "order_id", "method", "currency", "amount",
        "phone_number", "bill_pay_number",
        "payment_token", "snippe_reference",
        "tx_status", "expires_at",
        "notification_sent", "created_at",
    )
    readonly_fields = ("created_at", "updated_at")
    show_change_link = True


@admin.register(StudentPayment)
class StudentPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "student", "teacherclass", "fee",
        "amount_due", "amount_paid", "status",
        "notify_student_account",
        "created_at", "updated_at",
    )
    list_filter = (
        "status", "notify_student_account", "created_at",
        "teacherclass", "fee",
    )
    search_fields = (
        "student__id",
        "student__full_name",   # change if your Student model uses different field
        "student__name",        # safe extra (won't crash unless admin tries it? remove if not in model)
        "fee__name",            # adjust if Fee model field differs
        "description",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("student", "teacherclass", "fee", "user")
    autocomplete_fields = ("user", "teacherclass", "student", "fee")
    readonly_fields = ("created_at", "updated_at")
    inlines = [PaymentTransactionInline]

    fieldsets = (
        ("Links", {"fields": ("user", "teacherclass", "student", "fee")}),
        ("Amounts", {"fields": ("amount_due", "amount_paid")}),
        ("Status", {"fields": ("status", "notify_student_account")}),
        ("Notes", {"fields": ("description",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "order_id", "payment", "method",
        "currency", "amount", "tx_status",
        "payment_token", "snippe_reference",
        "expires_at", "notification_sent",
        "created_at",
    )
    list_filter = ("method", "tx_status", "currency", "notification_sent", "created_at")
    search_fields = (
        "order_id",
        "payment_token",
        "snippe_reference",
        "bill_pay_number",
        "phone_number",
        "idempotency_key",
        "payment__student__full_name",  # adjust if needed
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("payment", "payment__student", "payment__fee")
    autocomplete_fields = ("payment",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Payment Link", {"fields": ("payment",)}),
        ("Identifiers", {"fields": ("order_id", "idempotency_key")}),
        ("Method & Amount", {"fields": ("method", "currency", "amount")}),
        ("Payer Details", {"fields": ("phone_number", "bill_pay_number")}),
        ("Gateway References", {"fields": ("payment_token", "snippe_reference")}),
        ("Gateway Output", {"fields": ("payment_url", "payment_qr_code")}),
        ("Status", {"fields": ("tx_status", "expires_at", "notification_sent")}),
        ("Raw Response", {"fields": ("raw_response",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(CreatePayment)
class CreatePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "payment_name", "payment_option",
        "amount", "currency", "payment_status",
        "payment_token", "order_id",
        "phone_number", "email",
        "notification_sent",
        "created_at", "updated_at",
    )
    list_filter = ("payment_option", "payment_status", "currency", "notification_sent", "created_at")
    search_fields = (
        "payment_name",
        "full_name",
        "phone_number",
        "email",
        "payment_token",
        "order_id",
        "description",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Owner", {"fields": ("user",)}),
        ("Payment Setup", {"fields": ("payment_option", "payment_name", "amount", "currency")}),
        ("Payer Details", {"fields": ("full_name", "phone_number", "email")}),
        ("Status", {"fields": ("payment_status", "notification_sent")}),
        ("Gateway Data", {"fields": ("payment_token", "order_id")}),
        ("Messages", {"fields": ("description", "success_message")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


from django.contrib import admin
from .models import PaymentSegment, PaymentSegmentTransaction


# ================================
# Inline Transactions (Inside Segment)
# ================================
class PaymentSegmentTransactionInline(admin.TabularInline):
    model = PaymentSegmentTransaction
    extra = 0
    readonly_fields = (
        "order_id",
        "method",
        "amount",
        "tx_status",
        "phone_number",
        "bill_pay_number",
        "payment_token",
        "snippe_reference",
        "completed_at",
        "created_at",
    )
    show_change_link = True


# ================================
# Payment Segment Admin
# ================================
@admin.register(PaymentSegment)
class PaymentSegmentAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "teacherclass",
        "fee_name",
        "amount_required",
        "total_paid",
        "segment_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "teacherclass",
        "fee_name",
        "created_at",
    )

    search_fields = (
        "student__fullName",
        "student__registration_number",
        "teacherclass__name",
        "fee_name__fee_name",
    )

    readonly_fields = (
        "total_paid",
        "created_at",
        "updated_at",
    )

    inlines = [PaymentSegmentTransactionInline]

    ordering = ("-created_at",)

    fieldsets = (
        ("Student & Class Info", {
            "fields": (
                "student",
                "teacherclass",
                "fee_name",
                "studentfee",
                "user",
            )
        }),

        ("Payment Details", {
            "fields": (
                "amount_required",
                "segment_amount",
                "total_paid",
                "status",
            )
        }),

        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


# ================================
# Payment Segment Transaction Admin
# ================================
@admin.register(PaymentSegmentTransaction)
class PaymentSegmentTransactionAdmin(admin.ModelAdmin):

    list_display = (
        "order_id",
        "payment_segment",
        "method",
        "amount",
        "tx_status",
        "phone_number",
        "bill_pay_number",
        "notification_sent",
        "completed_at",
        "created_at",
    )

    list_filter = (
        "method",
        "tx_status",
        "notification_sent",
        "created_at",
    )

    search_fields = (
        "order_id",
        "snippe_reference",
        "payment_token",
        "phone_number",
        "bill_pay_number",
        "payment_segment__student__fullName",
    )

    readonly_fields = (
        "order_id",
        "payment_segment",
        "method",
        "amount",
        "phone_number",
        "bill_pay_number",
        "payment_token",
        "snippe_reference",
        "raw_response",
        "completed_at",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    fieldsets = (
        ("Transaction Info", {
            "fields": (
                "payment_segment",
                "order_id",
                "method",
                "amount",
                "tx_status",
            )
        }),

        ("Payment Details", {
            "fields": (
                "phone_number",
                "bill_pay_number",
                "payment_token",
                "snippe_reference",
            )
        }),

        ("System Data", {
            "fields": (
                "raw_response",
                "notification_sent",
                "completed_at",
            )
        }),

        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


from django.contrib import admin
from .models import WhatsAppSetting


@admin.register(WhatsAppSetting)
class WhatsAppSettingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'api_key',
        'base_url',
        'created_at',
        'updated_at',
    )
    
    search_fields = (
        'user__username',
        'user__email',
        'api_key',
    )
    
    list_filter = (
        'created_at',
        'updated_at',
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('API Configuration', {
            'fields': ('api_key', 'base_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
