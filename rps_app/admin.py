from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import (
    ExaminationName, TeacherClass, User, Teacher, Student, Subject, Mark,
    TeacherSubject, GradingModel, DisplayModel, ExcludeSubject, StudentSubject,
    UserSessionAccount, TermMarksUpload, EmailVerificationOTP, RequiredSubject,EmailConfiguration,UserAmount,
    StudentApplication
)
from django.contrib.admin import SimpleListFilter


class SubscriberStatusFilter(SimpleListFilter):
    title = 'subscription status'
    parameter_name = 'is_subscribe'

    def lookups(self, request, model_admin):
        return (
            ('subscribed', 'Subscribed'),
            ('not_subscribed', 'Not Subscribed'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'subscribed':
            return queryset.filter(is_subscribe=True)
        if self.value() == 'not_subscribed':
            return queryset.filter(is_subscribe=False)
        return queryset



@admin.register(ExaminationName)
class ExaminationNameAdmin(admin.ModelAdmin):
    list_display = ('exam_name', 'user', 'id')
    search_fields = ('exam_name', 'user__username')
    list_filter = ('user',)
    ordering = ('exam_name',)

from django.contrib import admin
from .models import AcademicClassYear, TeacherClass

@admin.register(AcademicClassYear)
class AcademicClassYearAdmin(admin.ModelAdmin):
    list_display = ('academic_year_name', 'active_year', 'id')
    list_filter = ('active_year',)
    search_fields = ('academic_year_name',)
    list_editable = ('active_year',)
    ordering = ('-active_year', 'academic_year_name')
    fieldsets = (
        (None, {
            'fields': ('academic_year_name', 'active_year')
        }),
    )
    
    def get_queryset(self, request):
        # Optimize queryset by selecting related fields if needed
        return super().get_queryset(request).select_related()

    def save_model(self, request, obj, form, change):
        # If setting as active, deactivate other academic years
        if obj.active_year:
            AcademicClassYear.objects.exclude(pk=obj.pk).update(active_year=False)
        super().save_model(request, obj, form, change)

@admin.register(TeacherClass)
class TeacherClassAdmin(admin.ModelAdmin):
    list_display = ('ClassName', 'academicclassyear', 'user', 'id')
    list_filter = ('academicclassyear__active_year', 'user')
    search_fields = ('ClassName', 'user__username', 'academicclassyear__academic_year_name')
    list_select_related = ('user', 'academicclassyear')
    autocomplete_fields = ('user', 'academicclassyear')
    ordering = ('ClassName',)
    fieldsets = (
        (None, {
            'fields': ('user', 'ClassName', 'academicclassyear')
        }),
    )

    def get_queryset(self, request):
        # Optimize queryset by selecting related fields
        return super().get_queryset(request).select_related('user', 'academicclassyear')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Restrict academicclassyear to active years only
        if db_field.name == 'academicclassyear':
            kwargs['queryset'] = AcademicClassYear.objects.filter(active_year=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username','is_superuser','is_staff','is_active', 'email', 'date_joined','is_student','is_teacher')
    search_fields = ('is_student','is_teacher','username', 'email')
    list_filter = ('is_active','is_student','is_teacher')
    ordering = ('username',)
    
    # Customize fields for add/edit forms
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser','is_student','is_teacher')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2','is_staff', 'is_superuser'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Save the User object first
        super().save_model(request, obj, form, change)
        
        # If the user is a teacher and has no Teacher profile, create one
        if obj.is_teacher and not Teacher.objects.filter(user=obj).exists():
            Teacher.objects.create(
                user=obj,
                teacherName=obj.username,  # Default to username
                teacher_key=f"T{obj.id}{int(timezone.now().timestamp())}",  # Generate unique teacher_key
                created_by=request.user if request.user.is_authenticated and request.user.is_teacher else None
            )




@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacherName', 'user', 'teacher_key', 'created_by')
    search_fields = ('teacherName', 'user__username', 'teacher_key')
    list_filter = ('created_by',)
    ordering = ('teacherName',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('fullName','photo', 'user', 'indexNumber', 'sex', 'contact', 'teacherclass', 'manager')
    search_fields = ('fullName', 'user__username', 'indexNumber')
    list_filter = ('sex', 'teacherclass', 'manager')
    ordering = ('fullName',)


@admin.register(StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'application_number', 'get_full_name', 'phone', 'academic_level',
        'academic_year', 'class_name', 'status', 'application_type',
        'application_date', 'user'
    )
    search_fields = (
        'application_number', 'first_name', 'middle_name', 'last_name',
        'phone', 'email', 'class_name', 'user__username'
    )
    list_filter = ('status', 'academic_level', 'academic_year', 'class_name', 'application_type', 'user')
    ordering = ('-created_at',)

    def get_full_name(self, obj):
        return obj.full_name
    get_full_name.short_description = 'Full Name'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('nameSubject', 'user', 'teacherclass')
    search_fields = ('nameSubject', 'user__username', 'teacherclass__ClassName')
    list_filter = ('user', 'teacherclass')
    ordering = ('nameSubject',)

@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'marks', 'teacherclass', 'examinationname', 'user')
    search_fields = ('student__fullName', 'subject__nameSubject', 'teacherclass__ClassName')
    list_filter = ('teacherclass', 'examinationname', 'subject', 'user')
    ordering = ('student__fullName',)

@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'teacherclass', 'is_restricted', 'user')
    search_fields = ('teacher__teacherName', 'subject__nameSubject', 'teacherclass__ClassName')
    list_filter = ('is_restricted', 'teacherclass', 'user')
    ordering = ('teacher__teacherName',)

@admin.register(GradingModel)
class GradingModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_advance', 'grade_a', 'grade_b', 'grade_c', 'grade_d', 'grade_e', 'grade_s', 'grade_f')
    search_fields = ('user__username',)
    list_filter = ('is_advance', 'user')
    ordering = ('user__username',)

@admin.register(DisplayModel)
class DisplayModelAdmin(admin.ModelAdmin):
    list_display = ('header', 'body', 'user', 'image')
    search_fields = ('header', 'body', 'user__username')
    list_filter = ('user',)
    ordering = ('header',)

@admin.register(ExcludeSubject)
class ExcludeSubjectAdmin(admin.ModelAdmin):
    list_display = ('exclude_subject', 'user')
    search_fields = ('exclude_subject__nameSubject', 'user__username')
    list_filter = ('user',)
    ordering = ('exclude_subject__nameSubject',)

@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ('teacherclass', 'user', 'get_subjects', 'get_students')
    search_fields = ('teacherclass__ClassName', 'user__username')
    list_filter = ('teacherclass', 'user')
    ordering = ('teacherclass__ClassName',)

    def get_subjects(self, obj):
        return ", ".join(s.nameSubject or "Unnamed Subject" for s in obj.subject.all())
    get_subjects.short_description = 'Subjects'

    def get_students(self, obj):
        return ", ".join(s.fullName or s.user.username for s in obj.student.all())
    get_students.short_description = 'Students'

@admin.register(UserSessionAccount)
class UserSessionAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'session_key', 'last_login', 'is_active', 'user')
    search_fields = ('username', 'session_key', 'user__username')
    list_filter = ('is_active', 'user')
    ordering = ('last_login',)

@admin.register(TermMarksUpload)
class TermMarksUploadAdmin(admin.ModelAdmin):
    list_display = ('term_name', 'teacherclass', 'uploaded_at', 'for_merging_pdf', 'user')
    search_fields = ('term_name', 'teacherclass__ClassName', 'user__username')
    list_filter = ('teacherclass', 'for_merging_pdf', 'user')
    ordering = ('uploaded_at',)

@admin.register(EmailVerificationOTP)
class EmailVerificationOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'otp_code', 'created_at', 'expires_at', 'is_used', 'is_verified', 'purpose')
    search_fields = ('user__username', 'email', 'otp_code')
    list_filter = ('is_used', 'is_verified', 'purpose', 'user')
    ordering = ('created_at',)

@admin.register(RequiredSubject)
class RequiredSubjectAdmin(admin.ModelAdmin):
    list_display = ('subject', 'level', 'user')
    search_fields = ('subject__nameSubject', 'level', 'user__username')
    list_filter = ('level', 'user')
    ordering = ('subject__nameSubject',)



from django.contrib import admin
from .models import SmsConfiguration

@admin.register(SmsConfiguration)
class SmsConfigurationAdmin(admin.ModelAdmin):
    list_display = ('user', 'source_addr', 'destination_addr', 'username','url_required')
    search_fields = ('user__username', 'source_addr', 'destination_addr', 'username')
    list_filter = ('source_addr',)

    def get_queryset(self, request):
        # Filter the queryset to show only SmsConfiguration for superusers
        queryset = super().get_queryset(request)
        return queryset.filter(user__is_superuser=True)

    def has_add_permission(self, request):
        # Restrict adding new settings to superusers only
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Restrict editing to superusers only
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Restrict deletion to superusers only
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        # Make sensitive fields like pswd read-only to prevent accidental changes
        if obj:  # Editing an existing object
            return ('pswd',)
        return ()

from .forms import EmailConfigurationAdminForm
@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    form = EmailConfigurationAdminForm  # Use custom form to filter superusers
    list_display = ('user', 'email_host', 'email_port', 'email_host_user', 'email_use_tls', 'email_host_password')
    search_fields = ('user__username', 'email_host', 'email_host_user')
    list_filter = ('email_use_tls',)
    readonly_fields = ()
    fieldsets = (
        (None, {
            'fields': ('user', 'email_backend', 'email_host', 'email_port', 'email_use_tls')
        }),
        ('Credentials', {
            'fields': ('email_host_user', 'email_host_password', 'default_from_email'),
            'description': 'Be cautious when editing credentials.'
        }),
    )


from .models import Subscriber
from .forms import SubscriberAdminForm




@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    form = SubscriberAdminForm  # Use custom form to filter superusers
    list_display = ('user', 'is_subscribe')
    search_fields = ('user__username',)
    list_filter = (SubscriberStatusFilter,)
    fieldsets = (
        (None, {
            'fields': ('user', 'is_subscribe')
        }),
    )



from django.contrib import admin
from .models import SourceDocument, RemarkRange


@admin.register(SourceDocument)
class SourceDocumentAdmin(admin.ModelAdmin):
    list_display = ("user", "comment", "file_signature", "file_stamp", "extracted_signature", "created_at")
    search_fields = ("comment", "user__username", "user__email")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)


@admin.register(RemarkRange)
class RemarkRangeAdmin(admin.ModelAdmin):
    list_display = ("min_value", "max_value", "remark")
    search_fields = ("remark",)
    list_filter = ("min_value", "max_value")
    ordering = ("min_value",)




from django.contrib import admin
from .models import Payment, PaymentNotification

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'transaction_id', 'user__username']

@admin.register(PaymentNotification)
class PaymentNotificationAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'amount', 'status', 'success_payment', 'created_at']
    list_filter = ['status', 'success_payment', 'created_at']
    search_fields = ['order_id', 'user__username']




@admin.register(UserAmount)
class UserAmountAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount']
    list_filter = ['user']
    search_fields = ['user']



from django.contrib import admin
from .models import RegisterClass


@admin.register(RegisterClass)
class RegisterClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'user', 'get_active_academic_year')
    list_filter = ('user',)
    search_fields = ('class_name', 'user__username', 'user__email')
    ordering = ('-id',)

    def get_queryset(self, request):
        """
        Optimize query to reduce DB hits when calling __str__ or custom methods
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            'teacherclass_set__academicclassyear'
        )

    def get_active_academic_year(self, obj):
        """
        Show active academic year in admin list
        """
        teacher_class = obj.teacherclass_set.filter(
            academicclassyear__active_year=True
        ).select_related('academicclassyear').first()

        if teacher_class and teacher_class.academicclassyear:
            return teacher_class.academicclassyear.academic_year_name
        return "—"

    get_active_academic_year.short_description = "Active Academic Year"
