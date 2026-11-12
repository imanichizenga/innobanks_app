# rps_app/forms.py
from django import forms
from .models import TeacherSubject, Teacher, Subject, TeacherClass, StudentSubject, Student,Mark
from django.db import models
# rps_app/forms.py
from django import forms
from .models import TeacherSubject, Teacher, Subject, TeacherClass

# rps_app/forms.py
from django import forms
from .models import TeacherSubject, Teacher, Subject, TeacherClass,EmailConfiguration,Subscriber
from django.conf import settings

from django import forms
from django.contrib.auth import get_user_model
from rps_app.models import EmailConfiguration

class EmailConfigurationAdminForm(forms.ModelForm):
       class Meta:
           model = EmailConfiguration
           fields = '__all__'

       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           # Use get_user_model() to get the User model class
           User = get_user_model()
           # Filter the user field to show only superusers
           self.fields['user'].queryset = User.objects.filter(is_superuser=True)

class SubscriberAdminForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        self.fields['user'].queryset = User.objects.filter(is_superuser=True)

class TeacherSubjectForm(forms.ModelForm):
    class Meta:
        model = TeacherSubject
        fields = ['teacher', 'subject', 'teacherclass', 'is_restricted']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'teacherclass': forms.Select(attrs={'class': 'form-select'}),
            'is_restricted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Custom initialization:
        - 'user': The currently logged-in user (passed from view via request.effective_user)
        - 'initial_teacher_id', 'initial_teacherclass_id': Optional pre-selections from session
        """
        user = kwargs.pop('user', None)
        initial_teacher_id = kwargs.pop('initial_teacher_id', None)
        initial_teacherclass_id = kwargs.pop('initial_teacherclass_id', None)
        super().__init__(*args, **kwargs)

        if not user:
            return  # Safety: if no user, form remains empty

        # ===================================================================
        # 1. TEACHER DROPDOWN: Include both:
        #    - Teachers created by this user (created_by=user)
        #    - The current user himself (if he has a Teacher profile)
        # ===================================================================
        created_teachers = Teacher.objects.filter(created_by=user)

        try:
            own_teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            own_teacher = None

        # Combine querysets: own + created (avoid duplicates)
        teacher_qs = created_teachers
        if own_teacher:
            # If own_teacher is not already in created_teachers, add it
            if not created_teachers.filter(id=own_teacher.id).exists():
                teacher_qs = (Teacher.objects.filter(id=own_teacher.id) | created_teachers)

        # Order by name for better UX
        self.fields['teacher'].queryset = teacher_qs.order_by('teacherName', 'user__username')

        # ===================================================================
        # 2. SUBJECT DROPDOWN: Only subjects created by this user
        # ===================================================================
        self.fields['subject'].queryset = Subject.objects.filter(user=user).order_by('nameSubject')

        # ===================================================================
        # 3. CLASS DROPDOWN: Only active academic year classes created by user
        # ===================================================================
        active_classes = TeacherClass.objects.filter(
            user=user,
            academicclassyear__active_year=True
        ).select_related('ClassName', 'academicclassyear').order_by(
            'ClassName__class_name', 'academicclassyear__academic_year_name'
        )

        self.fields['teacherclass'].queryset = active_classes

        # Customize display: "Class Name (Academic Year)"
        self.fields['teacherclass'].choices = [
            ('', '--------- Select a class ---------'),
            *[
                (
                    tc.id,
                    f"{tc.ClassName.class_name} ({tc.academicclassyear.academic_year_name})"
                )
                for tc in active_classes
            ]
        ]

        # ===================================================================
        # 4. INITIAL VALUES (from session)
        # ===================================================================
        if initial_teacher_id:
            self.fields['teacher'].initial = initial_teacher_id
        if initial_teacherclass_id:
            self.fields['teacherclass'].initial = initial_teacherclass_id

    # =======================================================================
    # 5. VALIDATION: Enforce unique_together (teacher, subject, teacherclass)
    # =======================================================================
    def clean(self):
        cleaned_data = super().clean()
        teacher = cleaned_data.get('teacher')
        subject = cleaned_data.get('subject')
        teacherclass = cleaned_data.get('teacherclass')

        if teacher and subject and teacherclass:
            existing = TeacherSubject.objects.filter(
                teacher=teacher,
                subject=subject,
                teacherclass=teacherclass
            )
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise forms.ValidationError(
                    f"Teacher '{teacher.teacherName or teacher.user.username}' "
                    f"is already assigned to subject '{subject.nameSubject}' "
                    f"in class '{teacherclass.ClassName.class_name}'."
                )
        return cleaned_data
from django import forms
from .models import StudentSubject, Student, Subject, TeacherClass
# forms.py
from django import forms
from .models import StudentSubject, Subject, Student

# forms.py
from django import forms
from .models import StudentSubject, Subject, Student

from django import forms
from .models import StudentSubject, Subject, Student

from django import forms
from .models import StudentSubject, Subject, Student

from django import forms
from .models import StudentSubject, Subject, Student

from django import forms
from .models import StudentSubject, Subject, Student
from django import forms
from .models import Subject, Student, StudentSubject

from django import forms
from .models import Subject, Student, StudentSubject

from django import forms
from .models import Subject, Student, StudentSubject
from django import forms
from .models import Subject, Student, StudentSubject

from django import forms
from .models import Subject, Student, StudentSubject, Mark
from django import forms
from .models import StudentSubject, Subject, Student, Mark, Vehicle, Route, FuelRecord, Maintenance, VehicleExpense

# rps_app/forms.py
from django import forms
from .models import StudentSubject, Subject, Student, Mark

class StudentSubjectForm(forms.ModelForm):
    subject = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Subjects",
    )
    student = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Students",
    )

    class Meta:
        model = StudentSubject
        fields = ['subject', 'student']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        teacherclass = kwargs.pop('teacherclass', None)
        student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)

        self.user = user
        self.is_single_update = student is not None

        if user:
            self.fields['subject'].queryset = Subject.objects.filter(user=user)

            if student:
                # Single-student scenario
                self.fields['student'].queryset = Student.objects.filter(id=student.id, manager=user)
                self.fields['student'].initial = [student]
                self.fields['student'].widget.attrs['readonly'] = True
                current_subjects = Subject.objects.filter(
                    studentsubject__student=student, studentsubject__user=user
                ).values_list('id', flat=True)
                self.fields['subject'].initial = current_subjects

            elif teacherclass:
                # Multi-student scenario
                self.fields['student'].queryset = Student.objects.filter(
                    manager=user, teacherclass=teacherclass
                )
        else:
            self.fields['subject'].queryset = Subject.objects.none()
            self.fields['student'].queryset = Student.objects.none()

    def save(self, commit=True):
        assigned_count = 0
        skipped_count = 0

        subjects = self.cleaned_data['subject']
        students = self.cleaned_data['student']

        for student in students:
            student_subject = StudentSubject.objects.filter(
                student=student, user=self.user
            ).first()

            if student_subject:
                old_subjects = set(student_subject.subject.all())

                if self.is_single_update:
                    new_subjects = set(subjects)
                else:
                    new_subjects = old_subjects | set(subjects)

                removed = old_subjects - new_subjects
                added = new_subjects - old_subjects

                other_students = student_subject.student.exclude(id=student.id)
                if other_students.exists():
                    # Clone for this student
                    new_ss = StudentSubject.objects.create(
                        teacherclass=student.teacherclass,
                        user=self.user
                    )
                    new_ss.student.add(student)
                    new_ss.subject.set(new_subjects)
                    student_subject.student.remove(student)
                    if not student_subject.student.exists():
                        student_subject.delete()

                    if added or (self.is_single_update and removed):
                        assigned_count += 1
                    else:
                        skipped_count += 1
                else:
                    # Update in place
                    if self.is_single_update and removed:
                        for subj in removed:
                            student_subject.subject.remove(subj)
                            Mark.objects.filter(student=student, subject=subj).delete()
                    if added:
                        student_subject.subject.add(*added)

                    if not student_subject.subject.exists():
                        student_subject.delete()

                    if added or (self.is_single_update and removed):
                        assigned_count += 1
                    else:
                        skipped_count += 1
            else:
                # Create new assignment
                new_ss = StudentSubject.objects.create(
                    teacherclass=student.teacherclass,
                    user=self.user
                )
                new_ss.student.add(student)
                new_ss.subject.set(subjects)
                assigned_count += 1

        return assigned_count, skipped_count



        
from django import forms
from .models import ExaminationName

class ExaminationNameForm(forms.ModelForm):
    class Meta:
        model = ExaminationName
        fields = ['exam_name']
        widgets = {
            'exam_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'Enter examination name'
            })
        }


class BootstrapModelForm(forms.ModelForm):
    """Apply bootstrap classes to generated fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(field, forms.DateField):
                merged_attrs = {**widget.attrs, 'type': 'date'}
                widget = forms.DateInput(attrs=merged_attrs, format='%Y-%m-%d')
                field.widget = widget
                field.input_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']

            existing_class = widget.attrs.get('class', '')
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)):
                css = 'form-check-input'
            elif isinstance(widget, forms.Select):
                css = 'form-select form-select-sm'
            elif isinstance(widget, forms.FileInput):
                css = 'form-control form-control-sm'
            else:
                css = 'form-control form-control-sm'
            widget.attrs['class'] = f"{existing_class} {css}".strip()


from .models import (
    StudentAcademicInformation,
    STUDENT_ACADEMIC_LEVEL_CHOICES,
    AcademicClassYear,
    StudentApplication,
    StudentGuardianInformation,
    StudentSponsorInformation,
    StudentMedicalInformation,
    StudentEmergencyContact,
    StudentPassportPhoto,
    TeacherAcademicInformation,
    TeacherPersonalInformation,
    TeacherEmergencyContact,
    TeacherMedicalInformation,
    TeacherPassportPhoto,
    TeacherBankInformation,
    TeacherContract,
    TeacherDocument,
)


class StudentAcademicInformationForm(BootstrapModelForm):
    academic_level = forms.ChoiceField(
        choices=[('', '--------- Select academic level ---------'), *STUDENT_ACADEMIC_LEVEL_CHOICES],
        required=False,
    )

    class Meta:
        model = StudentAcademicInformation
        exclude = ('student', 'created_at', 'updated_at')


class StudentGuardianInformationForm(BootstrapModelForm):
    class Meta:
        model = StudentGuardianInformation
        exclude = ('student', 'created_at', 'updated_at')


class StudentSponsorInformationForm(BootstrapModelForm):
    class Meta:
        model = StudentSponsorInformation
        exclude = ('student', 'created_at', 'updated_at')


class StudentMedicalInformationForm(BootstrapModelForm):
    class Meta:
        model = StudentMedicalInformation
        exclude = ('student', 'created_at', 'updated_at')


class StudentEmergencyContactForm(BootstrapModelForm):
    class Meta:
        model = StudentEmergencyContact
        exclude = ('student', 'created_at', 'updated_at')


class StudentPassportPhotoForm(BootstrapModelForm):
    class Meta:
        model = StudentPassportPhoto
        fields = ['passport_photo', 'photo_comment']
        widgets = {
            'passport_photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }


class StudentApplicationForm(BootstrapModelForm):
    ACADEMIC_LEVEL_CHOICES = [
        ('', '--------- Select academic level ---------'),
        ('Secondary (O-Level)', 'Secondary (O-Level)'),
        ('Secondary (A-Level)', 'Secondary (A-Level)'),
        ('Vocational', 'Vocational'),
        ('Technical', 'Technical'),
        ('Short Course', 'Short Course'),
    ]
    CLASS_CHOICES = [
        ('', '--------- Select class ---------'),
        ('FTNA', 'FTNA'),
        ('CSEE', 'CSEE'),
        ('ACSEE', 'ACSEE'),
        ('ECDE', 'ECDE'),
        ('English Course', 'English Course'),
        ('Computer Course', 'Computer Course'),
        ('Pre Form Five', 'Pre Form Five'),
        ('Pre Form One', 'Pre Form One'),
    ]
    APPLICATION_TYPE_CHOICES = [
        ('', '--------- Select application type ---------'),
        ('Physical', 'Physical'),
        ('Online', 'Online'),
    ]
    ENTRY_MODE_CHOICES = [
        ('', '--------- Select entry mode ---------'),
        ('New', 'New'),
        ('Transfer', 'Transfer'),
        ('Continuing', 'Continuing'),
    ]
    GENDER_CHOICES = [
        ('', '--------- Select gender ---------'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    academic_level = forms.ChoiceField(choices=ACADEMIC_LEVEL_CHOICES, required=True)
    academic_year = forms.ModelChoiceField(queryset=AcademicClassYear.objects.none(), required=True)
    class_name = forms.ChoiceField(choices=CLASS_CHOICES, required=True)
    application_type = forms.ChoiceField(choices=APPLICATION_TYPE_CHOICES, required=True)
    entry_mode = forms.ChoiceField(choices=ENTRY_MODE_CHOICES, required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    application_number = forms.CharField(required=False, disabled=True)

    class Meta:
        model = StudentApplication
        exclude = ('user', 'student', 'created_at', 'updated_at')
        widgets = {
            'application_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
            'sponsor_details': forms.Textarea(attrs={'rows': 3}),
            'personal_skills': forms.Textarea(attrs={'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        queryset = AcademicClassYear.objects.filter(active_year=True)
        if user:
            queryset = queryset.filter(user=user)
        self.fields['academic_year'].queryset = queryset.order_by('academic_year_name')
        self.fields['status'].required = False
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone'].required = True
        self.fields['address'].required = True
        self.fields['date_of_birth'].required = True


class TeacherAcademicInformationForm(BootstrapModelForm):
    class Meta:
        model = TeacherAcademicInformation
        exclude = ('teacher', 'created_at', 'updated_at')


class TeacherPersonalInformationForm(BootstrapModelForm):
    class Meta:
        model = TeacherPersonalInformation
        exclude = ('teacher', 'created_at', 'updated_at')


class TeacherEmergencyContactForm(BootstrapModelForm):
    class Meta:
        model = TeacherEmergencyContact
        exclude = ('teacher', 'created_at', 'updated_at')


class TeacherMedicalInformationForm(BootstrapModelForm):
    class Meta:
        model = TeacherMedicalInformation
        exclude = ('teacher', 'created_at', 'updated_at')


class TeacherPassportPhotoForm(BootstrapModelForm):
    class Meta:
        model = TeacherPassportPhoto
        exclude = ('teacher', 'uploaded_at')


class TeacherBankInformationForm(BootstrapModelForm):
    class Meta:
        model = TeacherBankInformation
        exclude = ('teacher', 'created_at', 'updated_at')


class TeacherContractForm(BootstrapModelForm):
    class Meta:
        model = TeacherContract
        exclude = ('teacher', 'created_at', 'updated_at')


class TeacherDocumentForm(BootstrapModelForm):
    class Meta:
        model = TeacherDocument
        exclude = ('teacher', 'created_at', 'updated_at')


class TransportBootstrapMixin:
    """Apply Bootstrap-friendly widgets to transport forms."""

    def _apply_bootstrap(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple, forms.DateInput, forms.TimeInput, forms.NumberInput, forms.Textarea, forms.EmailInput, forms.TextInput, forms.FileInput)):
                css_class = 'form-control' if not isinstance(widget, forms.Select) else 'form-select'
            else:
                css_class = 'form-control'
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = f"{existing} {css_class}".strip()


class VehicleForm(forms.ModelForm, TransportBootstrapMixin):
    class Meta:
        model = Vehicle
        fields = ['name', 'plate_number', 'vehicle_type', 'capacity', 'driver']
        widgets = {
            'name': forms.TextInput(),
            'plate_number': forms.TextInput(),
            'vehicle_type': forms.TextInput(),
            'capacity': forms.NumberInput(),
            'driver': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['driver'].queryset = Teacher.objects.filter(teacher_role='driver').select_related('user').order_by('teacherName', 'user__username')
        self._apply_bootstrap()


class RouteForm(forms.ModelForm, TransportBootstrapMixin):
    class Meta:
        model = Route
        fields = ['name', 'start_location', 'end_location', 'vehicle']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.select_related('driver', 'driver__user').order_by('name', 'plate_number')
        self._apply_bootstrap()


class FuelRecordForm(forms.ModelForm, TransportBootstrapMixin):
    class Meta:
        model = FuelRecord
        fields = ['vehicle', 'date', 'liters', 'cost']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.select_related('driver', 'driver__user').order_by('name', 'plate_number')
        self._apply_bootstrap()


class MaintenanceForm(forms.ModelForm, TransportBootstrapMixin):
    class Meta:
        model = Maintenance
        fields = ['vehicle', 'description', 'cost', 'date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.select_related('driver', 'driver__user').order_by('name', 'plate_number')
        self._apply_bootstrap()


class VehicleExpenseForm(forms.ModelForm, TransportBootstrapMixin):
    class Meta:
        model = VehicleExpense
        fields = ['vehicle', 'expense_type', 'amount', 'description', 'date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.select_related('driver', 'driver__user').order_by('name', 'plate_number')
        self._apply_bootstrap()

from .models import CRMLead


class CRMLeadForm(forms.ModelForm):
    class Meta:
        model = CRMLead
        fields = [
            'name',
            'phone',
            'email',
            'address',
            'student_first_name',
            'student_middle_name',
            'student_last_name',
            'academic_class',
            'focus',
            'source',
            'how_did_you_know_us',
            'status',
            'description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter lead name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address'}),
            'student_first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student first name'}),
            'student_middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student middle name'}),
            'student_last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student last name'}),
            'academic_class': forms.Select(attrs={'class': 'form-select'}),
            'focus': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter focus'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'how_did_you_know_us': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add description'}),
        }
