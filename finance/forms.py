from django import forms
from .models import  Fee,  StudentFee
from rps_app.models import Student, Teacher, TeacherClass

from django import forms
# finance/forms.py
from django import forms
from .models import  Fee,  StudentFee
from rps_app.models import Student, Teacher, TeacherClass
# finance/forms.py
from django import forms
from .models import  Fee, StudentFee
from rps_app.models import Student, Teacher, TeacherClass

from django import forms
from .models import Fee
from rps_app.models import Student

# class StudentFeeForm(forms.Form):
#     student = forms.ModelMultipleChoiceField(
#         queryset=Student.objects.none(),
#         widget=forms.CheckboxSelectMultiple,
#         required=True,
#         label="Select Students"
#     )
#     fee = forms.ModelChoiceField(
#         queryset=Fee.objects.none(),
#         required=True,
#         label="Select Fee"
#     )

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         creator = kwargs.pop('creator', None)
#         teacherclass = kwargs.pop('teacherclass', None)
#         year_id = kwargs.pop('year_id', None)
#         super().__init__(*args, **kwargs)

#         if teacherclass:
#             self.fields['student'].queryset = Student.objects.filter(
#                 teacherclass=teacherclass
#             ).order_by('fullName')

#         if year_id and teacherclass:
#             self.fields['fee'].queryset = Fee.objects.filter(
#                 installment__academic_year_id=year_id,
#                 installment__academic_year__is_active=True,
#                 teacherclasses=teacherclass
#             ).order_by('fee_name')
from django import forms
from django.core.exceptions import ValidationError


from django import forms
from django.core.exceptions import ValidationError

from django.db.models import Sum


import json
from django import forms
from django.db.models import Sum
from django.core.exceptions import ValidationError

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
import logging



from django import forms
from django.db.models import Sum,Q

from django.db import models

from django import forms
from django.db.models import Q
from .models import Fee, StudentFee
from rps_app.models import TeacherClass, Student
from datetime import date
import logging

logger = logging.getLogger(__name__)

class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['fee_name', 'teacherclass']
        widgets = {
            'fee_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Tuition Fee'}),
            'teacherclass': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)

        if self.user and creator:
            self.fields['teacherclass'].queryset = TeacherClass.objects.filter(
                user=creator,
                academicclassyear__active_year=True
            ).distinct()
        else:
            self.fields['teacherclass'].queryset = TeacherClass.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        fee_name = cleaned_data.get('fee_name')
        teacherclass = cleaned_data.get('teacherclass')

        if not fee_name:
            self.add_error('fee_name', "This field is required.")
        if not teacherclass:
            self.add_error('teacherclass', "This field is required.")

        if fee_name and teacherclass:
            if Fee.objects.filter(fee_name=fee_name, teacherclass=teacherclass).exclude(
                pk=self.instance.pk if self.instance and self.instance.pk else None
            ).exists():
                self.add_error('fee_name', "A fee with this name already exists for the selected class.")

        return cleaned_data
class StudentFeeForm(forms.Form):
    fee = forms.ModelChoiceField(
        queryset=Fee.objects.none(),
        empty_label="-- Select a Fee --",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_fee'})
    )
    student = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'student-checkbox'}),
        required=True
    )
    amount_required = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5000', 'id': 'id_amount_required'})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_start_date'}),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_end_date'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        creator = kwargs.pop('creator', None)
        self.teacherclass = kwargs.pop('teacherclass', None)
        super().__init__(*args, **kwargs)

        if self.user and creator and self.teacherclass:
            # Filter fees by the selected teacherclass
            self.fields['fee'].queryset = Fee.objects.filter(
                teacherclass=self.teacherclass
            ).distinct()
            self.fields['student'].queryset = Student.objects.filter(
                teacherclass=self.teacherclass
            ).distinct()
        else:
            self.fields['fee'].queryset = Fee.objects.none()
            self.fields['student'].queryset = Student.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        fee = cleaned_data.get('fee')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        amount_required = cleaned_data.get('amount_required')

        if not fee:
            self.add_error('fee', "This field is required.")
        if not cleaned_data.get('student'):
            self.add_error('student', "At least one student must be selected.")
        if not amount_required or amount_required < 0:
            self.add_error('amount_required', "A valid positive amount is required.")
        # if start_date and end_date:
        #     if start_date > end_date:
        #         self.add_error('end_date', "End date must not be before start date.")
        #     if start_date < date.today():
        #         self.add_error('start_date', "Start date cannot be in the past.")

        return cleaned_data

from django import forms
from rps_app.models import Student
from finance.models import StudentFocus

class StudentFocusAssignmentForm(forms.Form):
    student = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        label="Students",
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'student-checkbox'})
    )
    focus = forms.ChoiceField(
        choices=StudentFocus.FIELD_CHOICES,
        label="Focus",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_focus'})
    )

    def __init__(self, *args, **kwargs):
        creator = kwargs.pop('creator', None)
        class_id = kwargs.pop('class_id', None)
        super().__init__(*args, **kwargs)
        if creator and class_id:
            try:
                from rps_app.models import TeacherClass
                teacherclass = TeacherClass.objects.get(id=class_id, user=creator,academicclassyear__active_year=True)
                # Exclude students who already have a focus
                assigned_student_ids = StudentFocus.objects.filter(
                    student__teacherclass=teacherclass, 
                    student__manager=creator
                ).values_list('student__id', flat=True)
                self.fields['student'].queryset = Student.objects.filter(
                    teacherclass=teacherclass, 
                    manager=creator
                ).exclude(id__in=assigned_student_ids)
            except TeacherClass.DoesNotExist:
                self.fields['student'].queryset = Student.objects.none()


from .models import StudentRegistration
logger = logging.getLogger(__name__)

from django import forms
from .models import StudentFocus, StudentRegistration
from rps_app.models import TeacherClass
import logging

from django import forms
from .models import StudentFocus, StudentRegistration
from rps_app.models import TeacherClass
import logging

logger = logging.getLogger(__name__)

class StudentRegistrationForm(forms.Form):
    studentfocus = forms.ModelMultipleChoiceField(
        queryset=StudentFocus.objects.none(),
        label="Students",
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'student-checkbox'})
    )
    joined_date = forms.DateField(
        label="Joined Date",
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_joined_date'})
    )
    initial_payment = forms.DecimalField(
        label="Initial Payment",
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_initial_payment', 'placeholder': 'e.g., 5000.00'})
    )

    def __init__(self, *args, **kwargs):
        creator = kwargs.pop('creator', None)
        class_id = kwargs.pop('class_id', None)
        super().__init__(*args, **kwargs)
        if creator and class_id:
            try:
                teacherclass = TeacherClass.objects.get(
                    id=class_id, 
                    user=creator, 
                    academicclassyear__active_year=True
                )
                assigned_studentfocus_ids = StudentRegistration.objects.filter(
                    studentfocus__student__teacherclass=teacherclass,
                    studentfocus__student__manager=creator
                ).values_list('studentfocus__id', flat=True)
                self.fields['studentfocus'].queryset = StudentFocus.objects.filter(
                    student__teacherclass=teacherclass,
                    student__manager=creator
                ).exclude(id__in=assigned_studentfocus_ids).select_related('student__user')
                self.fields['studentfocus'].label_from_instance = lambda obj: (
                    f"{obj.student.fullName or obj.student.user.username or 'Unnamed Student'} "
                    f"({obj.focus or 'Unknown Focus'})"
                )
                logger.debug(f"StudentFocus queryset for class_id={class_id}: {[sf.id for sf in self.fields['studentfocus'].queryset]}")
            except TeacherClass.DoesNotExist:
                logger.warning(f"TeacherClass with id={class_id} does not exist or is not active")
                self.fields['studentfocus'].queryset = StudentFocus.objects.none()
            except Exception as e:
                logger.error(f"Error setting StudentFocus queryset: {str(e)}")
                self.fields['studentfocus'].queryset = StudentFocus.objects.none()

    def clean_studentfocus(self):
        studentfocus = self.cleaned_data.get('studentfocus')
        if not studentfocus:
            raise forms.ValidationError("At least one student must be selected.")
        valid_ids = set(str(sf.id) for sf in self.fields['studentfocus'].queryset)
        submitted_ids = set(str(sf.id) for sf in studentfocus)
        if not submitted_ids.issubset(valid_ids):
            raise forms.ValidationError("One or more selected students are not valid choices.")
        return studentfocus

    def clean_initial_payment(self):
        initial_payment = self.cleaned_data.get('initial_payment')
        if initial_payment is not None and initial_payment < 0:
            raise forms.ValidationError("Initial payment cannot be negative.")
        return initial_payment

# rps_app/forms.py
from django import forms
from .models import FeeAccountNumber
from django import forms
from .models import FeeAccountNumber, Fee
from rps_app.models import TeacherClass
from django import forms
from .models import FeeAccountNumber, Fee

class FeeAccountNumberForm(forms.ModelForm):
    class Meta:
        model = FeeAccountNumber
        fields = ['fee', 'account_number', 'account_name', 'is_active']
        widgets = {
        'fee': forms.Select(attrs={'class': 'form-select pill', 'id': 'fee'}),
        'account_number': forms.TextInput(attrs={'class': 'form-control pill'}),
        'account_name': forms.TextInput(attrs={'class': 'form-control pill'}),
        'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)

        if self.creator:
            # ✅ Fee.teacherclass is the FK (NOT teacherclasses)
            self.fields['fee'].queryset = Fee.objects.filter(
                teacherclass__user=self.creator,
                teacherclass__academicclassyear__active_year=True
            ).select_related('teacherclass', 'teacherclass__ClassName').order_by('fee_name')
        else:
            self.fields['fee'].queryset = Fee.objects.none()

    def clean_account_number(self):
        acc = (self.cleaned_data.get("account_number") or "").strip()
        if not acc:
            raise forms.ValidationError("Account number is required.")
        if len(acc) < 5:
            raise forms.ValidationError("Account number is too short.")
        return acc

    def clean_account_name(self):
        name = (self.cleaned_data.get("account_name") or "").strip()
        if not name:
            raise forms.ValidationError("Account name is required.")
        return name

from django import forms
from .models import PayFee

from django import forms
from .models import PayFee
from datetime import date

class PayFeeForm(forms.ModelForm):
    class Meta:
        model = PayFee
        fields = ['payer_account_no', 'description', 'amount_paid', 'payment_method', 'payment_reference', 'date_paid']
        widgets = {
            'payer_account_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1234567890'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Tuition Payment'
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'payment_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., TXN123456'
            }),
            'date_paid': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean_amount_paid(self):
        amount_paid = self.cleaned_data.get('amount_paid')
        if amount_paid <= 0:
            raise forms.ValidationError("Amount paid must be positive.")
        return amount_paid

    def clean_date_paid(self):
        date_paid = self.cleaned_data.get('date_paid')
        if not date_paid:
            raise forms.ValidationError("Payment date is required.")
        if date_paid > date.today():
            raise forms.ValidationError("Payment date cannot be in the future.")
        return date_paid

class PaymentUploadForm(forms.Form):
    pass



class StudentFeeUpdateForm(forms.Form):
    pass


from django import forms
from django.core.exceptions import ValidationError
from datetime import date

class StudentFeeUpdateForm(forms.Form):
    amount_required = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5000', 'id': 'update_amount_required'})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'update_start_date'}),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'update_end_date'}),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        amount_required = cleaned_data.get('amount_required')

        if not amount_required or amount_required < 0:
            self.add_error('amount_required', "A valid positive amount is required.")
        # if start_date and end_date:
        #     if start_date > end_date:
        #         self.add_error('end_date', "End date must not be before start date.")
        #     if start_date < date.today():
        #         self.add_error('start_date', "Start date cannot be in the past.")

        return cleaned_data