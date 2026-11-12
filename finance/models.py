from django.db import models
from django.conf import settings
from datetime import date




class StudentFocus(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user (e.g., accountant or admin) who created this fee."
    )
    student = models.ForeignKey(
        'rps_app.Student',
        on_delete=models.CASCADE,
        related_name='student_focus',
        help_text="The student assigned to pay this fee."
    )
    FIELD_CHOICES = [
        ('science', 'Science'),
        ('arts', 'Arts'),
        ('commerce', 'Commerce'),
        ('technical', 'Technical'),
    ]
    focus = models.CharField(max_length=20, choices=FIELD_CHOICES, default='science')

    def __str__(self):
        return f'{self.focus}'

from django.db import models
from django.conf import settings

class StudentRegistration(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_registration',
        help_text="The user (e.g., accountant or admin) who registered the student."
    )
    studentfocus = models.ForeignKey(
        'StudentFocus',
        on_delete=models.CASCADE,
        related_name='student_fcs',
        help_text="The student's focus record."
    )
    joined_date = models.DateField(
        help_text="The date the student joined the class."
    )
    initial_payment = models.DecimalField(max_digits=12, decimal_places=2,null=True,help_text='Add amount')

    def __str__(self):
        return f"{self.studentfocus.student.fullName} ({self.studentfocus.focus}) - {self.joined_date.strftime('%B %d, %Y')}"

    class Meta:
        verbose_name = "Student Registration"
        verbose_name_plural = "Student Registrations"
        unique_together = ('studentfocus', 'joined_date')
        
class Fee(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fees',
        help_text="The user (e.g., accountant or admin) who created this fee."
    )
    fee_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text="Name of the fee (e.g., Tuition Fee)."
    )
    teacherclass = models.ForeignKey(
        'rps_app.TeacherClass',
        on_delete=models.CASCADE,
        help_text="The class this fee pertains to."
	,null=True
    )
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return f"{self.fee_name} ({self.teacherclass.ClassName.class_name})"

    class Meta:
        verbose_name = "Fee"
        verbose_name_plural = "Fees"
        unique_together = ('fee_name', 'teacherclass')

class StudentFee(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_fees',
        help_text="The user (e.g., teacher or admin) who assigned this fee."
    )
    teacherclass = models.ForeignKey(
        'rps_app.TeacherClass',
        on_delete=models.CASCADE,
        help_text="The class this fee assignment pertains to.",
	null=True
    )
    student = models.ForeignKey(
        'rps_app.Student',
        on_delete=models.CASCADE,
        related_name='assigned_fees',
        help_text="The student assigned to pay this fee.",
	null=True
    )
    fee = models.ForeignKey(
        'Fee',
        on_delete=models.CASCADE,
        help_text="The fee assigned to the student.",
	null=True
    )
    amount_required = models.DecimalField(max_digits=12, decimal_places=2,null=True,help_text='Add amount')
    start_date = models.DateField(
        help_text="Start date of the fee period.",
	null=True
    )
    end_date = models.DateField(
        help_text="End date of the fee period.",
	null=True
    )
    assigned_date = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"{self.student.fullName} - {self.fee.fee_name} ({self.teacherclass.ClassName.class_name})"

    class Meta:
        verbose_name = "Student Fee Assignment"
        verbose_name_plural = "Student Fee Assignments"
        unique_together = ('student', 'fee', 'teacherclass')

class FeeAccountNumber(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fee_accounts',
        help_text="The user (e.g., teacher or admin) who assigned this fee."
    )
    fee = models.ForeignKey(
        'Fee',
        on_delete=models.CASCADE,
        help_text="Fee Account Number."
    )
    teacherclass = models.ForeignKey(
        'rps_app.TeacherClass',
        on_delete=models.CASCADE,
        help_text="The class this fee assignment pertains to.",
        null=True
    )
    account_number = models.CharField(max_length=30)
    account_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.account_number} ({self.account_name})'

class PayFee(models.Model):
    PAYMENT_METHOD_CASH = 'cash'
    PAYMENT_METHOD_BANK = 'bank'
    PAYMENT_METHOD_MOBILE = 'mobile_money'
    PAYMENT_METHOD_CARD = 'card'
    PAYMENT_METHOD_OTHER = 'other'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CASH, 'Cash'),
        (PAYMENT_METHOD_BANK, 'Bank Transfer'),
        (PAYMENT_METHOD_MOBILE, 'Mobile Money'),
        (PAYMENT_METHOD_CARD, 'Card'),
        (PAYMENT_METHOD_OTHER, 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pay_fee',
        help_text="The user (e.g., teacher or admin) who assigned this fee."
    )
    student = models.ForeignKey(
        'rps_app.Student',
        on_delete=models.CASCADE,
        related_name='payfee',
        help_text="The student assigned to pay this fee."
    )
    fee = models.ForeignKey(
        'Fee',
        on_delete=models.CASCADE,
        help_text="The fee assigned to the student."
    )
    payer_account_no = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_CASH)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
    date_paid = models.DateField(
        help_text="The date the payment was made.",
        null=True,
        blank=True,
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.date_paid and self.date_paid > date.today():
            raise ValidationError("Payment date cannot be in the future.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def latest_whatsapp_message(self):
        prefetched_messages = getattr(self, '_prefetched_objects_cache', {}).get('whatsapp_messages')
        if prefetched_messages is not None:
            ordered_messages = sorted(prefetched_messages, key=lambda message: (message.created_at, message.id))
            return next(reversed(ordered_messages), None)
        return self.whatsapp_messages.order_by('created_at', 'id').last()

    @property
    def whatsapp_status(self):
        latest_message = self.latest_whatsapp_message
        return latest_message.status if latest_message else 'pending'

    @property
    def whatsapp_message_id(self):
        latest_message = self.latest_whatsapp_message
        return latest_message.msg_id if latest_message else None

    def __str__(self):
        return f"{self.amount_paid} paid on {self.date_paid}"

    class Meta:
        ordering = ['-date_paid']


class WhatsAppMessage(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
        ("not_on_whatsapp", "Not on WhatsApp"),
        ("updated", "Updated"),
        ("update_failed", "Update Failed"),
        ("deleted", "Deleted"),
        ("delete_failed", "Delete Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student = models.ForeignKey('rps_app.Student', on_delete=models.CASCADE)
    payment = models.ForeignKey('PayFee', on_delete=models.CASCADE, related_name="whatsapp_messages")
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    msg_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    api_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f"WhatsApp message for payment {self.payment_id} ({self.status})"

class ChangeLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='change_logs'
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"{username} - {self.get_action_display()} - {self.model_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Change Log"
        verbose_name_plural = "Change Logs"
        ordering = ['-created_at']

class Discount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user (e.g., teacher or admin) who applied this discount."
    )
    student = models.ForeignKey(
        'rps_app.Student',
        on_delete=models.CASCADE,
        help_text="The student receiving this discount."
    )
    fee = models.ForeignKey(
        'Fee',
        on_delete=models.CASCADE,
        help_text="The fee this discount applies to."
    )
    teacherclass = models.ForeignKey(
        'rps_app.TeacherClass',
        on_delete=models.CASCADE,
        help_text="The class this discount pertains to."
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.student.fullName} - {self.fee.fee_name} ({self.teacherclass.ClassName.class_name}) - {self.discount_amount}"

    class Meta:
        unique_together = ('student', 'fee', 'teacherclass')

from django.conf import settings
from django.db import models


class StudentPayment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    teacherclass = models.ForeignKey(
        "rps_app.TeacherClass",
        on_delete=models.CASCADE,
        null=True, blank=True,
        help_text="The class this payment belongs to."
    )
    student = models.ForeignKey(
        "rps_app.Student",
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    fee = models.ForeignKey(
        "Fee",
        on_delete=models.SET_NULL,
        related_name="student_payments",
        null=True, blank=True
    )

    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    notify_student_account = models.BooleanField(default=False)

    STATUS_PENDING = "pending"
    STATUS_PARTIAL = "partial"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PARTIAL, "Partial"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    description = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"StudentPayment #{self.id} - {self.student} - {self.amount_paid}/{self.amount_due} ({self.status})"


class PaymentTransaction(models.Model):
    payment = models.ForeignKey(
        StudentPayment,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True
    )

    # Your own unique order id for idempotency
    order_id = models.CharField(max_length=80, unique=True)

    METHOD_QR = "dynamic-qr"
    METHOD_MOBILE = "mobile"
    METHOD_BILLPAY = "billpay"
    method = models.CharField(
        max_length=30,
        choices=[
            (METHOD_QR, "Dynamic QR"),
            (METHOD_MOBILE, "Mobile Push"),
            (METHOD_BILLPAY, "Bill Pay"),
        ]
    )

    currency = models.CharField(max_length=10, default="TZS")
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    phone_number = models.CharField(max_length=20, blank=True, default="")
    bill_pay_number = models.CharField(max_length=50, blank=True, default="")

    snippe_reference = models.CharField(max_length=120, blank=True, default="", db_index=True)
    payment_token = models.CharField(max_length=120, blank=True, default="", db_index=True)

    payment_url = models.TextField(blank=True, default="")
    payment_qr_code = models.TextField(blank=True, default="")

    idempotency_key = models.CharField(max_length=120, blank=True, default="")

    TX_PENDING = "pending"
    TX_SUCCESS = "success"
    TX_COMPLETED = "completed"
    TX_FAILED = "failed"
    TX_EXPIRED = "expired"
    tx_status = models.CharField(
        max_length=20,
        choices=[
            (TX_PENDING, "Pending"),
            (TX_SUCCESS, "Success"),
            (TX_COMPLETED, "Completed"),
            (TX_FAILED, "Failed"),
            (TX_EXPIRED, "Expired"),
        ],
        default=TX_PENDING
    )

    raw_response = models.JSONField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.method} {self.order_id} ({self.tx_status})"

from django.db import models
from django.conf import settings


class CreatePayment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    FIELD_CHOICES = [
        ('mobile_payment', 'Mobile'),
        ('payment_token', 'Payment Token'),
    ]

    payment_option = models.CharField(
        max_length=20,
        choices=FIELD_CHOICES,
        default='payment_token',
        null=True,
        blank=True
    )

    payment_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # ✅ Currency fixed to TZS
    CURRENCY_CHOICES = [
        ('TZS', 'Tanzanian Shilling'),
    ]

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='TZS'
    )

    full_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    email = models.EmailField(
        null=True,
        blank=True
    )

    description = models.TextField(
        default="Payment description",
        null=True,
        blank=True
    )

    success_message = models.TextField(
        null=True,
        blank=True,
        help_text="Message sent to the payer after successful payment."
    )

    # ✅ Payment Token / Bill Number
    payment_token = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Token or bill number from payment gateway"
    )

    order_id = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        help_text="Unique order reference for the payment request."
    )

    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    payment_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        null=True,
        blank=True
    )

    notification_sent = models.BooleanField(default=True)

    # ✅ Date & Time Tracking
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.payment_name or f"Payment #{self.id}"


class SmsConfiguration(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="finance_sms_configuration",
        help_text="The user (e.g., accountant) who owns the SMS configuration."
    )
    url_required = models.URLField(default="https://apisms.beem.africa/v1/send")
    source_addr = models.CharField(default="innobanks", max_length=20)
    destination_addr = models.CharField(default="255616257477", max_length=20)
    message = models.TextField(default="innobanks messages")
    username = models.CharField(default="fa41fbc274f5097c", max_length=50)
    pswd = models.CharField(
        default="YzVhOTRlYmNhMmRkYWU5ZjBlYzUyY2U1NmNmYTNkNmIzZjZkODc3MjQzNDk3ZWMyNDE3MTJjN2Q5NTVlMTI2NA==",
        max_length=500,
    )

    def __str__(self):
        return f"{self.source_addr}"

    class Meta:
        verbose_name = "SMS CONFIGURATIONS"
        verbose_name_plural = "SMS CONFIGURATION"


class WebhookConfiguration(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, default="default")
    webhook_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.webhook_url or self.name or "Webhook Configuration"

    class Meta:
        verbose_name = "Webhook Configuration"
        verbose_name_plural = "Webhook Configurations"


class WhatsAppSetting(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='finance_whatsapp_setting',
        help_text='The user who owns the WhatsApp configuration.'
    )
    api_key = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    base_url = models.URLField(default='https://www.wasenderapi.com/api')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"WhatsApp Setting - {self.user.username}"

    class Meta:
        verbose_name = 'WhatsApp Setting'
        verbose_name_plural = 'WhatsApp Settings'


class PaymentSegment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_segment",
        help_text="The user (e.g., accountant) who owns the SMS configuration."
    )
    teacherclass = models.ForeignKey(
        'rps_app.TeacherClass',
        on_delete=models.CASCADE,
        help_text="The class this discount pertains to."
    )
    student = models.ForeignKey(
        'rps_app.Student',
        on_delete=models.CASCADE,
        related_name='payment_segment',
        help_text="The student assigned to pay this fee."
    )
    fee_name = models.ForeignKey(Fee, on_delete=models.CASCADE, null=True)
    studentfee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, null=True)
    segment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Last segment amount requested by student.'
    )
    amount_required = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    STATUS_PENDING = "pending"
    STATUS_COMPLETE = "complete"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETE, "Complete"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = ('student', 'teacherclass', 'fee_name', 'studentfee')

    def __str__(self):
        return f"{self.student} - {self.fee_name} ({self.total_paid}/{self.amount_required})"


class PaymentSegmentTransaction(models.Model):
    payment_segment = models.ForeignKey(
        PaymentSegment,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    METHOD_MOBILE = "mobile"
    METHOD_BILLPAY = "billpay"
    METHOD_CHOICES = [
        (METHOD_MOBILE, "Mobile Push"),
        (METHOD_BILLPAY, "Bill Pay"),
    ]
    method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    order_id = models.CharField(max_length=80, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    phone_number = models.CharField(max_length=20, blank=True, default="")
    bill_pay_number = models.CharField(max_length=50, blank=True, default="")
    payment_token = models.CharField(max_length=120, blank=True, default="", db_index=True)
    snippe_reference = models.CharField(max_length=120, blank=True, default="", db_index=True)
    TX_PENDING = "pending"
    TX_COMPLETED = "completed"
    TX_SUCCESS = "success"
    TX_FAILED = "failed"
    TX_EXPIRED = "expired"
    TX_CHOICES = [
        (TX_PENDING, "Pending"),
        (TX_COMPLETED, "Completed"),
        (TX_SUCCESS, "Success"),
        (TX_FAILED, "Failed"),
        (TX_EXPIRED, "Expired"),
    ]
    tx_status = models.CharField(max_length=20, choices=TX_CHOICES, default=TX_PENDING)
    raw_response = models.JSONField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment_segment_id}-{self.order_id} ({self.tx_status})"
