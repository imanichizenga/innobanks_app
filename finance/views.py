from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from django.db import OperationalError, ProgrammingError
from django.urls import reverse
from urllib.parse import urlencode
from django.db.models import Sum
from django import forms
from decimal import Decimal, InvalidOperation
import json
import logging
import uuid
import pandas as pd
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt


from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum
from .models import StudentFee, PayFee
from rps_app.models import Student
from django.shortcuts import redirect
from rps_app.models import Student # Make sure Student is imported
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# Models
from .models import Fee, StudentFee, FeeAccountNumber, PayFee, ChangeLog, SmsConfiguration
from .models import StudentPayment, PaymentTransaction, CreatePayment, WebhookConfiguration, PaymentSegment, PaymentSegmentTransaction
from snippe_payment import SnippePaymentClient
from rps_app.models import Teacher, TeacherClass, Student, EmailConfiguration, StudentCommunicationLog
from rps_app.utils import get_email_settings

# Forms
from .forms import StudentFeeForm, FeeForm, FeeAccountNumberForm, PayFeeForm, PaymentUploadForm

logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

def accountant_role_required(view_func):
    """Decorator to ensure the user has the 'Accountant' role or is a superuser."""
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.is_superuser:
                # Superusers are their own creators
                request.creator = request.user
                logger.debug(f"Superuser {request.user.username} set as creator")
            else:
                # For non-superusers, retrieve creator from Teacher profile
                teacher_profile = Teacher.objects.get(user=request.user)
                creator = teacher_profile.created_by
                if not creator:
                    messages.error(request, "Your account is not properly configured: No creator assigned.")
                    logger.warning(f"User {request.user.username} has no creator assigned")
                    return redirect('teacher_dashboard')
                request.creator = creator
                logger.debug(f"User {request.user.username} assigned creator {creator.username}")
            return view_func(request, *args, **kwargs)
        except Teacher.DoesNotExist:
            messages.error(request, "You do not have permission to view this page: No teacher profile found.")
            logger.error(f"Teacher profile not found for user {request.user.username}")
            return redirect('teacher_dashboard')
    return wrapper

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib import messages
import json
import logging

logger = logging.getLogger(__name__)


from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@accountant_role_required
def fee_update(request, fee_id):
    user = request.user
    creator = request.creator  # Set by accountant_role_required: request.user for superusers, Teacher.created_by otherwise

    fee = get_object_or_404(Fee, id=fee_id, teacherclasses__user=creator)

    if request.method == 'POST':
        form = FeeForm(request.POST, instance=fee, user=user, creator=creator)
        if form.is_valid():
            updated_fee = form.save()

            ChangeLog.objects.create(
                user=user,
                action='UPDATE',
                model_name='Fee',
                object_id=updated_fee.id,
                description=f"Updated fee {updated_fee.fee_name}"
            )

            messages.success(request, f"Fee '{updated_fee.fee_name}' updated successfully!")
            logger.debug(f"Fee {updated_fee.fee_name} updated by user {user.username} for creator {creator.username}")
            return redirect('finance:fee_list')
        else:
            messages.error(request, "Please correct the errors below.")
            logger.error(f"Form errors: {form.errors.as_json()}")
    else:
        form = FeeForm(instance=fee, user=user, creator=creator)

    # Prepare installment data for JavaScript validation
    installment_data = {}
    for inst in form.fields['installment'].queryset:
        existing_fees = inst.fee_set.exclude(pk=fee.id).aggregate(total=Sum('amount'))['total'] or 0
        installment_data[str(inst.id)] = {
            'fees': float(inst.fees),
            'existing_fees': float(existing_fees),
            'remaining_fees': float(inst.fees - existing_fees),
            'start_date': str(inst.start_date),
            'end_date': str(inst.end_date),
        }

    context = {
        'form': form,
        'fee': fee,
        'installment_data_json': json.dumps(installment_data, default=str),
        'active_tab': 'accountant'
    }
    return render(request, 'accountant/fee_update.html', context)
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@accountant_role_required
def fee_delete(request, fee_id):
    user = request.user
    creator = request.creator  # Set by accountant_role_required: request.user for superusers, Teacher.created_by otherwise

    fee = get_object_or_404(Fee, id=fee_id, teacherclasses__user=creator)

    if request.method == 'POST':
        fee_name = fee.fee_name
        
        ChangeLog.objects.create(
            user=user,
            action='DELETE',
            model_name='Fee',
            object_id=fee_id,
            description=f"Deleted fee {fee_name}"
        )
        
        fee.delete()
        messages.success(request, f"Fee '{fee_name}' deleted successfully!")
        logger.debug(f"Fee {fee_name} deleted by user {user.username} for creator {creator.username}")
        return redirect('finance:fee_list')

    messages.warning(request, "Invalid request method for deletion.")
    logger.debug(f"Deletion of fee {fee_id} not confirmed by user {user.username}")
    return redirect('finance:fee_list')
# finance/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Fee, StudentFee, ChangeLog
from .forms import FeeForm, StudentFeeForm
from rps_app.models import TeacherClass, Student, Teacher
import logging
from .decorators import accountant_role_required

logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Fee, StudentFee, ChangeLog
from .forms import FeeForm, StudentFeeForm
from rps_app.models import TeacherClass, Student, Teacher
import logging
from .decorators import accountant_role_required

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Fee, StudentFee, StudentFocus, StudentRegistration
from rps_app.models import TeacherClass, Student
from .forms import FeeForm, StudentFeeForm
import logging
from .decorators import accountant_role_required


logger = logging.getLogger(__name__)

@accountant_role_required
def get_student_fees_for_class(request, class_id):
    creator = getattr(request, 'creator', request.user)
    try:
        teacherclass = TeacherClass.objects.filter(id=class_id, user=creator).first()
        if not teacherclass:
            logger.error(f"TeacherClass with id {class_id} not found for creator {creator.username}")
            return JsonResponse({'success': False, 'error': 'Class not found'}, status=404)

        students = Student.objects.filter(teacherclass=teacherclass, manager=creator).select_related('teacherclass')
        student_fee_data = []
        for student in students:
            student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
            studentfocus = StudentFocus.objects.filter(student=student).first()
            registration = StudentRegistration.objects.filter(studentfocus=studentfocus).first() if studentfocus else None
            total_amount_required = sum(sf.amount_required for sf in student_fees) if student_fees else 0
            fees_info = [{
                'id': sf.id,  # Changed from sf.fee.id to sf.id to reference StudentFee ID
                'fee_name': sf.fee.fee_name,
                'amount_required': str(sf.amount_required),
                'start_date': sf.start_date.strftime('%Y-%m-%d'),
                'end_date': sf.end_date.strftime('%Y-%m-%d')
            } for sf in student_fees]
            student_fee_data.append({
                'student_id': student.id,
                'student_name': f"{student.fullName or 'Unnamed Student'} - {registration.joined_date.strftime('%B %d, %Y') if registration else 'Not registered'} - {studentfocus.focus if studentfocus else 'No focus'}",
                'class_name': teacherclass.ClassName.class_name if teacherclass.ClassName else 'Unnamed Class',
                'fees': fees_info,
                'total_amount_required': str(total_amount_required),
                'joined_date': registration.joined_date.strftime('%Y-%m-%d') if registration else None
            })

        logger.debug(f"Fetched {len(student_fee_data)} student fee records for class_id={class_id}")
        return JsonResponse({'success': True, 'student_fee_data': student_fee_data})
    except Exception as e:
        logger.error(f"Error fetching student fees for class_id={class_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.db.models import Q
import logging
from .decorators import accountant_role_required

from .forms import FeeForm

logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Fee, ChangeLog
from .forms import FeeForm
from rps_app.models import TeacherClass
import logging

logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required
from .decorators import accountant_role_required

def get_descendant_users(user):
    """Get all users created by the given user, recursively."""
    descendants = set()
    try:
        # Get all Teacher profiles where the user is the creator
        created_teachers = Teacher.objects.filter(created_by=user)
        for teacher in created_teachers:
            descendants.add(teacher.user)
            # Recursively get descendants of this teacher
            descendants.update(get_descendant_users(teacher.user))
    except Exception as e:
        logger.error(f"Error fetching descendants for user {user.username}: {str(e)}")
    return descendants

@accountant_role_required
def fee_create(request):
    user = request.user
    creator = getattr(request, 'creator', user)

    if request.method == 'POST':
        form = FeeForm(request.POST, user=user, creator=creator)
        if form.is_valid():
            fee = form.save(commit=False)
            fee.user = user
            fee.save()

            ChangeLog.objects.create(
                user=user,
                action='CREATE',
                model_name='Fee',
                object_id=fee.id,
                description=f"Created fee {fee.fee_name} for class {fee.teacherclass.ClassName.class_name}"
            )

            messages.success(request, f"Fee '{fee.fee_name}' created successfully!")
            logger.debug(f"Fee {fee.fee_name} created by user {user.username} for creator {creator.username}")
            return redirect('finance:fee_create')
        else:
            messages.error(request, "Please correct the errors below.")
            logger.error(f"Form errors: {form.errors.as_json()}")
    else:
        form = FeeForm(user=user, creator=creator)

    # Include fees created by the user or their descendants
    descendant_users = get_descendant_users(creator)
    fees = Fee.objects.filter(
        Q(user=creator) | Q(user__in=descendant_users) | Q(teacherclass__user=creator) | Q(teacherclass__user__in=descendant_users)
    ).select_related('teacherclass', 'teacherclass__academicclassyear').distinct()

    return render(request, 'accountant/fee_form.html', {
        'form': form,
        'fees': fees,
        'active_tab': 'accountant'
    })

@accountant_role_required
def fee_list(request):
    user = request.user
    creator = getattr(request, 'creator', user)

    # Include fees created by the user or their descendants
    descendant_users = get_descendant_users(creator)
    fees = Fee.objects.filter(
        Q(user=creator) | Q(user__in=descendant_users) | Q(teacherclass__user=creator) | Q(teacherclass__user__in=descendant_users)
    ).select_related('teacherclass', 'teacherclass__academicclassyear').distinct()

    logger.debug(f"Retrieved {fees.count()} fees for creator {creator.username}")

    return render(request, 'accountant/fee_list.html', {
        'fees': fees,
        'active_tab': 'accountant'
    })

@accountant_role_required
def fee_update(request, fee_id):
    user = request.user
    creator = getattr(request, 'creator', user)
    
    # Include fees created by the user or their descendants
    descendant_users = get_descendant_users(creator)
    fee = get_object_or_404(Fee, id=fee_id, user__in=[creator] + list(descendant_users))

    if request.method == 'POST':
        form = FeeForm(request.POST, instance=fee, user=user, creator=creator)
        if form.is_valid():
            fee = form.save()
            ChangeLog.objects.create(
                user=user,
                action='UPDATE',
                model_name='Fee',
                object_id=fee.id,
                description=f"Updated fee {fee.fee_name} for class {fee.teacherclass.ClassName.class_name}"
            )
            messages.success(request, f"Fee '{fee.fee_name}' updated successfully!")
            logger.debug(f"Fee {fee.fee_name} updated by user {user.username} for creator {creator.username}")
            return redirect('finance:fee_create')
        else:
            messages.error(request, "Please correct the errors below.")
            logger.error(f"Form errors: {form.errors.as_json()}")
    else:
        form = FeeForm(instance=fee, user=user, creator=creator)

    # Include fees created by the user or their descendants
    fees = Fee.objects.filter(
        Q(user=creator) | Q(user__in=descendant_users) | Q(teacherclass__user=creator) | Q(teacherclass__user__in=descendant_users)
    ).select_related('teacherclass', 'teacherclass__academicclassyear').distinct()

    return render(request, 'accountant/fee_form.html', {
        'form': form,
        'fees': fees,
        'active_tab': 'accountant',
        'is_update': True
    })

@accountant_role_required
def fee_delete(request, fee_id):
    user = request.user
    creator = getattr(request, 'creator', user)
    
    # Include fees created by the user or their descendants
    descendant_users = get_descendant_users(creator)
    fee = get_object_or_404(Fee, id=fee_id, user__in=[creator] + list(descendant_users))

    if request.method == 'POST':
        fee_name = fee.fee_name
        class_name = fee.teacherclass.ClassName.class_name
        fee.delete()
        ChangeLog.objects.create(
            user=user,
            action='DELETE',
            model_name='Fee',
            object_id=fee_id,
            description=f"Deleted fee {fee_name} for class {class_name}"
        )
        messages.success(request, f"Fee '{fee_name}' deleted successfully!")
        logger.debug(f"Fee {fee_name} deleted by user {user.username} for creator {creator.username}")
        return redirect('finance:fee_create')
    else:
        fees = Fee.objects.filter(
            Q(user=creator) | Q(user__in=descendant_users) | Q(teacherclass__user=creator) | Q(teacherclass__user__in=descendant_users)
        ).select_related('teacherclass', 'teacherclass__academicclassyear').distinct()
        return render(request, 'accountant/fee_delete_confirm.html', {
            'fee': fee,
            'fees': fees,
            'active_tab': 'accountant'
        })
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from decimal import Decimal
import logging

from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import StudentFeeForm
import logging

logger = logging.getLogger(__name__)

@accountant_role_required
def fee_management(request):
    user = request.user
    creator = getattr(request, 'creator', user)
    selected_class_id = request.GET.get('class_id')
    selected_fee_id = request.GET.get('fee_id')
    status_filter = request.GET.get('status')
    focus_filter = request.GET.get('focus')
    date_range_start = request.GET.get('date_range_start')
    date_range_end = request.GET.get('date_range_end')
    search_query = request.GET.get('search')

    # Filter TeacherClass by creator, including academic year
    teacher_classes = TeacherClass.objects.filter(user=creator, academicclassyear__active_year=True).select_related('ClassName', 'academicclassyear').distinct()

    # Filter Fees by teacher_classes and creator
    fees = Fee.objects.filter(teacherclass__in=teacher_classes, user=creator).distinct() if teacher_classes.exists() else Fee.objects.none()

    selected_class = None
    selected_fee = None

    if selected_class_id:
        fees = fees.filter(teacherclass__id=selected_class_id)
        try:
            selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=creator)
        except Exception as e:
            logger.error(f"Error fetching selected class {selected_class_id}: {e}")
            messages.error(request, "Invalid class selected.")

    student_fee_data = []
    summary = None

    if selected_class_id and selected_fee_id:
        try:
            selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=creator)
            selected_fee = Fee.objects.filter(id=selected_fee_id, teacherclass__id=selected_class_id, user=creator).first()
            if not selected_fee:
                logger.warning(f"No fee found for fee_id={selected_fee_id} and class_id={selected_class_id}")
                messages.error(request, "Selected fee is not associated with the chosen class.")
            else:
                student_fees = StudentFee.objects.filter(
                    teacherclass_id=selected_class_id,
                    fee__id=selected_fee_id
                ).select_related('student', 'fee')

                logger.debug(f"Fetched {student_fees.count()} student fee records for teacherclass_id={selected_class_id}, fee_id={selected_fee_id}")

                from collections import defaultdict
                student_ids = [sf.student_id for sf in student_fees]
                online_paid_by_student = defaultdict(Decimal)
                completed_totals_by_payment = defaultdict(Decimal)
                completed_statuses = [PaymentTransaction.TX_COMPLETED, PaymentTransaction.TX_SUCCESS]
                student_online_payments = StudentPayment.objects.filter(
                    teacherclass_id=selected_class_id,
                    fee_id=selected_fee_id,
                    student_id__in=student_ids,
                ).prefetch_related("transactions")
                payment_by_id = {payment.id: payment for payment in student_online_payments}
                if payment_by_id:
                    online_transactions = PaymentTransaction.objects.filter(
                        payment_id__in=payment_by_id.keys(),
                        tx_status__in=completed_statuses,
                    )
                    for tx in online_transactions:
                        payment = payment_by_id.get(tx.payment_id)
                        if not payment:
                            continue
                        completed_totals_by_payment[payment.id] += tx.amount
                        online_paid_by_student[payment.student_id] += tx.amount

                    for payment in student_online_payments:
                        if payment.status != StudentPayment.STATUS_PAID:
                            continue
                        completed_total = completed_totals_by_payment.get(payment.id, Decimal("0.00"))
                        if payment.amount_paid <= completed_total:
                            continue
                        online_paid_by_student[payment.student_id] += payment.amount_paid - completed_total

                for sf in student_fees:
                    # Fetch payments
                    payments = PayFee.objects.filter(
                        student=sf.student,
                        fee=sf.fee,
                        user=creator
                    ).order_by('date_paid')
                    total_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
                    online_paid = online_paid_by_student.get(sf.student_id, Decimal("0.00"))
                    total_paid += online_paid
                    discount = Discount.objects.filter(
                        student=sf.student,
                        fee=sf.fee,
                        teacherclass_id=selected_class_id,
                        user=creator
                    ).first()
                    discount_amount = discount.discount_amount if discount else Decimal('0.00')
                    balance = sf.amount_required - total_paid - discount_amount
                    status = 'Complete' if balance == 0 else ('Complete & Exceed' if balance < 0 else 'Remain')

                    # Calculate payment status
                    payment_status = 'No Payment'
                    if payments.exists():
                        payment_dates = payments.values_list('date_paid', flat=True)
                        if any(sf.start_date <= date_paid <= sf.end_date for date_paid in payment_dates):
                            payment_status = 'On Time'
                        elif all(date_paid < sf.start_date for date_paid in payment_dates):
                            payment_status = 'Advance'
                        elif all(date_paid > sf.end_date for date_paid in payment_dates):
                            payment_status = 'Late'

                    # Fetch initial payment from StudentRegistration
                    student_registration = StudentRegistration.objects.filter(
                        studentfocus__student=sf.student,
                        user=creator
                    ).first()
                    initial_payment = student_registration.initial_payment if student_registration and student_registration.initial_payment is not None else Decimal('0.00')
                    joined_date = student_registration.joined_date.strftime('%Y-%m-%d') if student_registration and student_registration.joined_date else 'Not registered'
                    focus = StudentFocus.objects.filter(student=sf.student, user=creator).first()
                    focus_value = focus.focus if focus else 'No focus'

                    include = True
                    if status_filter and status != status_filter:
                        include = False
                    if focus_filter and focus_value != focus_filter:
                        include = False
                    if date_range_start and joined_date != 'Not registered' and joined_date < date_range_start:
                        include = False
                    if date_range_end and joined_date != 'Not registered' and joined_date > date_range_end:
                        include = False
                    if search_query and search_query.lower() not in sf.student.fullName.lower():
                        include = False

                    if include:
                        student_fee_data.append({
                            'student_id': sf.student.id,
                            'student_name': sf.student.fullName,
                            'amount_required': sf.amount_required,
                            'total_paid': total_paid,
                            'balance': balance,
                            'status': status,
                            'discount_amount': discount_amount,
                            'has_discount': discount_amount > 0,
                            'joined_date': joined_date,
                            'focus': focus_value,
                            'payment_status': payment_status,
                            'initial_payment': initial_payment
                        })

                if student_fee_data:
                    total_payments = sum(data['total_paid'] for data in student_fee_data)
                    total_expected_fees = sum(data['amount_required'] for data in student_fee_data)
                    complete_count = sum(1 for data in student_fee_data if data['status'] == 'Complete')
                    remain_count = sum(1 for data in student_fee_data if data['status'] == 'Remain')
                    students_exceeded = sum(1 for data in student_fee_data if data['status'] == 'Complete & Exceed')
                    total_complete_amount = sum(data['total_paid'] for data in student_fee_data if data['status'] == 'Complete')
                    total_remaining_amount = sum(data['balance'] for data in student_fee_data if data['status'] == 'Remain')
                    total_exceed = sum(-data['balance'] for data in student_fee_data if data['status'] == 'Complete & Exceed')
                    students_with_discounts = sum(1 for data in student_fee_data if data['has_discount'])
                    total_discount_amount = sum(data['discount_amount'] for data in student_fee_data if data['has_discount'])
                    total_initial_payments = sum(data['initial_payment'] for data in student_fee_data)
                    students_with_initial_payments = sum(1 for data in student_fee_data if data['initial_payment'] > 0)

                    summary = {
                        'total_payments': total_payments,
                        'total_expected_fees': total_expected_fees,
                        'complete_count': complete_count,
                        'remain_count': remain_count,
                        'students_exceeded': students_exceeded,
                        'total_complete_amount': total_complete_amount,
                        'total_remaining_amount': total_remaining_amount,
                        'total_exceed': total_exceed,
                        'students_with_discounts': students_with_discounts,
                        'total_discount_amount': total_discount_amount,
                        'total_initial_payments': total_initial_payments,
                        'students_with_initial_payments': students_with_initial_payments
                    }
        except Exception as e:
            logger.error(f"Error fetching student fee data: {e}")
            messages.error(request, "Error loading student fee data.")

    context = {
        'teacher_classes': teacher_classes,
        'fees': fees,
        'selected_class_id': selected_class_id,
        'selected_fee_id': selected_fee_id,
        'student_fee_data': student_fee_data,
        'selected_class': selected_class,
        'selected_fee': selected_fee,
        'summary': summary,
        'status_filter': status_filter,
        'focus_filter': focus_filter,
        'date_range_start': date_range_start,
        'date_range_end': date_range_end,
        'search_query': search_query
    }
    return render(request, 'accountant/fee_management.html', context)

@accountant_role_required
def get_student_fees_for_class(request, class_id):
    creator = getattr(request, 'creator', request.user)
    try:
        teacherclass = TeacherClass.objects.filter(id=class_id, user=creator).first()
        if not teacherclass:
            logger.error(f"TeacherClass with id {class_id} not found for creator {creator.username}")
            return JsonResponse({'success': False, 'error': 'Class not found'}, status=404)

        students = Student.objects.filter(teacherclass=teacherclass, manager=creator).select_related('user')
        student_fee_data = []
        for student in students:
            student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
            studentfocus = StudentFocus.objects.filter(student=student, user=creator).first()
            registration = StudentRegistration.objects.filter(studentfocus=studentfocus, user=creator).first() if studentfocus else None
            total_amount_required = sum(sf.amount_required for sf in student_fees) if student_fees else Decimal('0.00')
            initial_payment = registration.initial_payment if registration and registration.initial_payment is not None else Decimal('0.00')
            joined_date = registration.joined_date.strftime('%Y-%m-%d') if registration and registration.joined_date else 'Not registered'
            focus = studentfocus.focus if studentfocus else 'No focus'

            fees_info = [{
                'id': sf.id,
                'fee_name': sf.fee.fee_name,
                'amount_required': str(sf.amount_required),
                'start_date': sf.start_date.strftime('%Y-%m-%d'),
                'end_date': sf.end_date.strftime('%Y-%m-%d')
            } for sf in student_fees]
            student_fee_data.append({
                'student_id': student.id,
                'student_name': student.fullName or student.user.username or 'Unnamed Student',
                'class_name': teacherclass.ClassName.class_name if teacherclass.ClassName else 'Unnamed Class',
                'fees': fees_info,
                'total_amount_required': str(total_amount_required),
                'joined_date': joined_date,
                'focus': focus,
                'initial_payment': str(initial_payment)
            })

        logger.debug(f"Fetched {len(student_fee_data)} student fee records for class_id={class_id}")
        return JsonResponse({'success': True, 'student_fee_data': student_fee_data})
    except Exception as e:
        logger.error(f"Error fetching student fees for class_id={class_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def get_student_registration_for_class(request, class_id):
    creator = getattr(request, 'creator', request.user)
    try:
        teacherclass = TeacherClass.objects.filter(
            id=class_id, 
            user=creator, 
            academicclassyear__active_year=True
        ).first()
        if not teacherclass:
            logger.error(f"TeacherClass with id {class_id} not found for creator {creator.username}")
            return JsonResponse({'success': False, 'error': 'Class not found'}, status=404)

        student_focuses = StudentFocus.objects.filter(
            student__teacherclass=teacherclass,
            student__manager=creator
        ).select_related('student__user')
        student_registration_data = []
        for sf in student_focuses:
            registration = StudentRegistration.objects.filter(studentfocus=sf, user=creator).first()
            student_name = sf.student.fullName or sf.student.user.username or 'Unnamed Student'
            focus_display = sf.focus or 'Unknown Focus'
            student_registration_data.append({
                'student_id': sf.student.id,
                'student_name': student_name,
                'class_name': teacherclass.ClassName.class_name or 'Unnamed Class',
                'joined_date': registration.joined_date.strftime('%B %d, %Y') if registration else 'Not registered',
                'focus': focus_display,
                'initial_payment': str(registration.initial_payment) if registration and registration.initial_payment is not None else '0.00'
            })

        logger.debug(f"Fetched {len(student_focuses)} student focuses for class_id={class_id}")
        return JsonResponse({'success': True, 'student_registration_data': student_registration_data})
    except Exception as e:
        logger.error(f"Error fetching student registrations for class_id={class_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from django.db.models import Q

logger = logging.getLogger(__name__)

from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from django.db.models import Q

logger = logging.getLogger(__name__)

@accountant_role_required
def assign_fees_to_students(request, class_id=None):
    """Assign fees to students for a specific class, with optional preselected fee via ?fee_id="""
    user = request.user
    creator = getattr(request, 'creator', request.user)

    teacher_classes = TeacherClass.objects.filter(
        user=creator,
        academicclassyear__active_year=True
    ).distinct()

    teacherclass = None
    form = None
    all_students_data = []

    # ✅ fee_id can come from fee_list page (GET) or remain in URL
    selected_fee_id = request.GET.get("fee_id") or None

    if class_id:
        teacherclass = get_object_or_404(
            TeacherClass,
            id=class_id,
            user=creator,
            academicclassyear__active_year=True
        )

        students = Student.objects.filter(
            teacherclass=teacherclass,
            manager=creator
        ).select_related('user')

        # ✅ If fee_id exists, ensure it belongs to this class
        preselected_fee_obj = None
        if selected_fee_id:
            preselected_fee_obj = Fee.objects.filter(
                id=selected_fee_id,
                teacherclass=teacherclass
            ).first()
            # If fee doesn't belong to this class, ignore it
            if not preselected_fee_obj:
                selected_fee_id = None

        if request.method == 'POST':
            # NOTE: fee_id may be lost on POST unless kept in URL or JS action includes it.
            # We'll also read it from GET here (still available if action kept it).
            selected_fee_id = request.GET.get("fee_id") or selected_fee_id

            form = StudentFeeForm(
                request.POST,
                user=user,
                creator=creator,
                teacherclass=teacherclass
            )

            logger.debug(f"POST data: {request.POST}")

            if form.is_valid():
                with transaction.atomic():
                    selected_students = form.cleaned_data['student']
                    selected_fee = form.cleaned_data['fee']
                    amount_required = form.cleaned_data['amount_required']
                    start_date = form.cleaned_data['start_date']
                    end_date = form.cleaned_data['end_date']

                    assigned_count, skipped_count = 0, 0

                    for student in selected_students:
                        exists = StudentFee.objects.filter(
                            student=student,
                            fee=selected_fee,
                            teacherclass=teacherclass
                        ).exists()

                        if not exists:
                            student_fee = StudentFee.objects.create(
                                user=user,
                                teacherclass=teacherclass,
                                student=student,
                                fee=selected_fee,
                                amount_required=amount_required,
                                start_date=start_date,
                                end_date=end_date
                            )
                            assigned_count += 1

                            ChangeLog.objects.create(
                                user=user,
                                action='CREATE',
                                model_name='StudentFee',
                                object_id=str(student_fee.id),
                                description=f"Assigned fee '{selected_fee.fee_name}' to student '{student.fullName}' in '{teacherclass.ClassName.class_name}'"
                            )
                        else:
                            skipped_count += 1

                    if assigned_count > 0:
                        messages.success(request, f"Assigned fee '{selected_fee.fee_name}' to {assigned_count} student(s).")
                    if skipped_count > 0:
                        messages.info(request, f"Skipped {skipped_count} student(s) already assigned this fee.")

                    # ✅ Redirect back but keep fee_id in query so it stays selected
                    url = reverse('finance:assign_fees_to_students', kwargs={'class_id': class_id})
                    if selected_fee:
                        url += f"?fee_id={selected_fee.id}"
                    return redirect(url)
            else:
                messages.error(request, "Please correct the errors in the form.")
                logger.error(f"Form errors: {form.errors.as_json()}")

        else:
            # ✅ Preselect fee on initial GET
            initial = {}
            if preselected_fee_obj:
                initial["fee"] = preselected_fee_obj

            form = StudentFeeForm(
                user=user,
                creator=creator,
                teacherclass=teacherclass,
                initial=initial
            )

        # Prepare fee status table
        student_fees = StudentFee.objects.filter(
            teacherclass=teacherclass
        ).select_related('student', 'fee')

        all_students_data = []
        for student in students:
            student_fees_for_student = student_fees.filter(student=student)

            studentfocus = StudentFocus.objects.filter(student=student, user=creator).first()
            registration = StudentRegistration.objects.filter(studentfocus=studentfocus, user=creator).first() if studentfocus else None

            total_amount = sum(sf.amount_required for sf in student_fees_for_student) if student_fees_for_student else Decimal('0.00')
            initial_payment = registration.initial_payment if registration and registration.initial_payment is not None else Decimal('0.00')
            joined_date = registration.joined_date.strftime('%Y-%m-%d') if registration and registration.joined_date else 'Not registered'
            focus = studentfocus.focus if studentfocus else 'No focus'

            fees_info = [
                {
                    'id': sf.id,
                    'fee_name': sf.fee.fee_name,
                    'amount_required': str(sf.amount_required),
                    'start_date': sf.start_date.strftime('%Y-%m-%d') if sf.start_date else '',
                    'end_date': sf.end_date.strftime('%Y-%m-%d') if sf.end_date else ''
                }
                for sf in student_fees_for_student
            ]

            all_students_data.append({
                'student_id': student.id,
                'student_name': student.fullName or student.user.username or 'Unnamed Student',
                'joined_date': joined_date,
                'fees': fees_info,
                'total_amount_required': str(total_amount),
                'focus': focus,
                'initial_payment': str(initial_payment)
            })

    return render(request, 'accountant/assign_fees.html', {
        'form': form,
        'teacherclass': teacherclass,
        'teacher_classes': teacher_classes,
        'all_students_data': all_students_data,
        'class_id': class_id,
        'selected_fee_id': selected_fee_id,  # ✅ used by template JS
        'active_tab': 'accountant'
    })


from django.shortcuts import get_object_or_404, render
from django.contrib import messages
import logging
from .decorators import accountant_role_required


logger = logging.getLogger(__name__)


@accountant_role_required
def student_fee_list(request, class_id=None):
    user = request.user
    creator = getattr(request, 'creator', user)

    # Fetch TeacherClass instances with non-null academicclassyear
    teacher_classes = TeacherClass.objects.filter(
        user=creator,
        academicclassyear__isnull=False
    ).select_related('ClassName', 'academicclassyear').distinct()
    teacherclass = None
    student_fee_data = None

    if class_id:
        # Validate the selected class
        teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator, academicclassyear__isnull=False)
        students_in_class = Student.objects.filter(teacherclass=teacherclass)
        student_fees = StudentFee.objects.filter(
            student__in=students_in_class
        ).select_related('student', 'fee')
        
        student_fee_data = {}
        for student in students_in_class:
            student_fee_data[student] = {
                'class_name': str(teacherclass),
                'is_active': teacherclass.is_active,
                'teacherclass': teacherclass,
                'fee_list': []
            }
        
        for assignment in student_fees:
            if assignment.student in student_fee_data:
                student_fee_data[assignment.student]['fee_list'].append({
                    'fee': assignment.fee,
                    'amount_required': assignment.amount_required,
                    'start_date': assignment.start_date,
                    'end_date': assignment.end_date
                })

        logger.debug(f"Retrieved {students_in_class.count()} students and {student_fees.count()} fee assignments for creator {creator.username}, class_id={class_id}")

    context = {
        'teacher_classes': teacher_classes,
        'student_fee_data': student_fee_data,
        'class_id': class_id,
        'teacherclass': teacherclass,
        'active_tab': 'accountant'
    }
    return render(request, 'accountant/student_fee_list.html', context)

@accountant_role_required
def get_fees_for_class(request, class_id):
    creator = getattr(request, 'creator', request.user)
    try:
        teacherclass = TeacherClass.objects.filter(id=class_id, user=creator).first()
        if not teacherclass:
            logger.error(f"TeacherClass with id {class_id} not found for creator {creator.username}")
            return JsonResponse({'success': False, 'error': 'Class not found'}, status=404)

        fees = Fee.objects.filter(teacherclass=teacherclass).values('id', 'fee_name')
        students = Student.objects.filter(teacherclass=teacherclass, manager=creator).select_related('teacherclass')
        student_data = []
        for student in students:
            studentfocus = StudentFocus.objects.filter(student=student).first()
            registration = StudentRegistration.objects.filter(studentfocus=studentfocus).first() if studentfocus else None
            student_data.append({
                'id': student.id,
                'fullName': f"{student.fullName or 'Unnamed Student'} - {registration.joined_date.strftime('%B %d, %Y') if registration else 'Not registered'} - {studentfocus.focus if studentfocus else 'No focus'}"
            })

        logger.debug(f"Fetched {fees.count()} fees and {students.count()} students for class_id={class_id}")
        return JsonResponse({
            'success': True,
            'fees': list(fees),
            'students': student_data
        })
    except Exception as e:
        logger.error(f"Error fetching fees for class_id={class_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@accountant_role_required
def student_fee_list_dynamic(request):
    user = request.user
    creator = request.creator

    teacher_classes = TeacherClass.objects.filter(
        user=creator,
        academicclassyear__active_year=True
    ).distinct()

    context = {
        'teacher_classes': teacher_classes,
        'active_tab': 'accountant'
    }
    return render(request, 'accountant/student_fee_list_dynamic.html', context)


from .forms import StudentFeeUpdateForm
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
import logging
from django.http import Http404

logger = logging.getLogger(__name__)
@accountant_role_required
def update_student_fee(request, student_id):
    user = request.user
    creator = request.creator

    try:
        student = get_object_or_404(Student, id=student_id, manager=creator)
    except Http404:
        messages.error(request, "Student not found or you do not have permission to access this student.")
        logger.error(f"Student with id {student_id} not found for creator {creator.username}")
        return redirect('finance:student_fee_list')

    teacherclass = student.teacherclass
    academic_year = teacherclass.academicyear_set.filter(is_active=True).first()
    if not academic_year:
        messages.error(request, "No active academic year found for this class.")
        logger.error(f"No active academic year for teacherclass {teacherclass.ClassName} and creator {creator.username}")
        return redirect('finance:student_fee_list')

    if request.method == 'POST':
        form = StudentFeeUpdateForm(request.POST, student=student)
        if form.is_valid():
            selected_fees = form.cleaned_data['fee']
            StudentFee.objects.filter(student=student, teacherclass=teacherclass).delete()
            
            for fee in selected_fees:
                StudentFee.objects.create(
                    user=user,
                    teacherclass=teacherclass,
                    student=student,
                    fee=fee
                )
                ChangeLog.objects.create(
                    user=user,
                    action='UPDATE',
                    model_name='StudentFee',
                    object_id=f"{student.id}-{fee.id}",
                    description=f"Assigned fee {fee.fee_name} to student {student.fullName}"
                )
                logger.debug(f"Assigned fee {fee.fee_name} to student {student.fullName} for creator {creator.username}")

            messages.success(request, f"Fees for {student.fullName} updated successfully!")
            logger.debug(f"Updated fees for student {student.fullName} by user {user.username} for creator {creator.username}")
            return redirect('finance:student_fee_list', class_id=teacherclass.id)
        else:
            messages.error(request, "Please correct the errors below.")
            logger.error(f"Form errors: {form.errors.as_json()}")
    else:
        current_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).values_list('fee__id', flat=True)
        form = StudentFeeUpdateForm(student=student, initial={'fee': list(current_fees)})

    return render(request, 'accountant/update_student_fee.html', {
        'form': form,
        'student': student,
        'teacherclass': teacherclass,
        'active_tab': 'accountant'
    })
@accountant_role_required
def delete_student_fee(request, student_id, fee_id):
    user = request.user
    creator = request.creator

    try:
        student = get_object_or_404(Student, id=student_id, manager=creator)
    except Http404:
        messages.error(request, "Student not found or you do not have permission to access this student.")
        logger.error(f"Student with id {student_id} not found for creator {creator.username}")
        return redirect('finance:student_fee_list')

    teacherclass = student.teacherclass
    academic_year = teacherclass.academicyear_set.filter(is_active=True).first()
    if not academic_year:
        messages.error(request, "No active academic year found for this class.")
        logger.error(f"No active academic year for teacherclass {teacherclass.ClassName} and creator {creator.username}")
        return redirect('finance:student_fee_list')

    if fee_id == 0:  # Delete all fees
        student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass)
        if not student_fees.exists():
            messages.error(request, "No fee assignments found for this student.")
            logger.error(f"No fee assignments for student {student_id} in class {teacherclass.id}, creator {creator.username}")
            return redirect('finance:student_fee_list', class_id=teacherclass.id)
    else:
        fee = get_object_or_404(Fee, id=fee_id, teacherclass=teacherclass)
        student_fees = StudentFee.objects.filter(student=student, fee=fee, teacherclass=teacherclass)
        if not student_fees.exists():
            messages.error(request, "Fee assignment not found.")
            logger.error(f"Fee assignment not found for student {student_id}, fee {fee_id}, creator {creator.username}")
            return redirect('finance:student_fee_list', class_id=teacherclass.id)

    if request.method == 'POST':
        student_fees.delete()
        ChangeLog.objects.create(
            user=user,
            action='DELETE',
            model_name='StudentFee',
            object_id=f"{student_id}-{fee_id or 'all'}",
            description=f"Removed {'all fees' if fee_id == 0 else fee.fee_name} from student {student.fullName}"
        )
        messages.success(request, f"{'All fees' if fee_id == 0 else f'Fee {fee.fee_name}'} removed from {student.fullName}.")
        logger.debug(f"Deleted {'all fees' if fee_id == 0 else f'fee {fee.fee_name}'} for student {student.fullName} by user {user.username} for creator {creator.username}")
        return redirect('finance:student_fee_list', class_id=teacherclass.id)
    else:
        return render(request, 'accountant/delete_student_fee.html', {
            'student': student,
            'fee': None if fee_id == 0 else fee,
            'teacherclass': teacherclass,
            'active_tab': 'accountant'
        })
    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import FeeAccountNumber, ChangeLog
from .forms import FeeAccountNumberForm
from rps_app.models import Teacher
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

from .models import FeeAccountNumber, Fee
from .forms import FeeAccountNumberForm

@accountant_role_required
def fee_account_number_list(request):
    user = request.user
    creator = getattr(request, "creator", user)

    # ✅ Show only accounts belonging to this creator
    fee_accounts = FeeAccountNumber.objects.filter(
        user=creator
    ).select_related("fee", "teacherclass").order_by("-id")

    if request.method == "POST":
        form = FeeAccountNumberForm(request.POST, creator=creator)
        if form.is_valid():
            with transaction.atomic():
                obj = form.save(commit=False)

                # ✅ Always store who owns these settings (creator)
                obj.user = creator

                # ✅ keep teacherclass consistent (your model has teacherclass field)
                # fee.teacherclass can be null in your model, so handle safely
                obj.teacherclass = obj.fee.teacherclass if obj.fee else None

                obj.save()

                # ✅ Optional: Only one active per fee
                if obj.is_active:
                    FeeAccountNumber.objects.filter(
                        user=creator,
                        fee=obj.fee
                    ).exclude(id=obj.id).update(is_active=False)

            messages.success(request, "Fee account number added successfully.")
            return redirect("finance:fee_account_number_list")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = FeeAccountNumberForm(creator=creator)

    return render(request, "accountant/fee_account_number_list.html", {
        "form": form,
        "fee_accounts": fee_accounts,
        "active_tab": "accountant",
    })


@accountant_role_required
def fee_account_number_update(request, pk):
    """
    Called via fetch() in your template.
    Must return JSON.
    """
    user = request.user
    creator = getattr(request, "creator", user)

    account = get_object_or_404(FeeAccountNumber, pk=pk, user=creator)

    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    form = FeeAccountNumberForm(request.POST, instance=account, creator=creator)
    if form.is_valid():
        with transaction.atomic():
            obj = form.save(commit=False)
            obj.user = creator
            obj.teacherclass = obj.fee.teacherclass if obj.fee else None
            obj.save()

            # ✅ Optional: Only one active per fee
            if obj.is_active:
                FeeAccountNumber.objects.filter(
                    user=creator,
                    fee=obj.fee
                ).exclude(id=obj.id).update(is_active=False)

        return JsonResponse({"success": True, "message": "Updated successfully."})

    # Return field errors clearly
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@accountant_role_required
def fee_account_number_delete(request, pk):
    """
    Called via fetch() in your template.
    Must return JSON.
    """
    user = request.user
    creator = getattr(request, "creator", user)

    account = get_object_or_404(FeeAccountNumber, pk=pk, user=creator)

    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    account.delete()
    return JsonResponse({"success": True, "message": "Deleted successfully."})



from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal

from .models import  Fee, StudentFee, PayFee, Discount, ChangeLog
from rps_app.models import TeacherClass, Student, Teacher
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal

from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .models import Fee, StudentFee, PayFee, Discount
from rps_app.models import TeacherClass, Student
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from finance.models import Fee, StudentFee, PayFee, Discount, StudentFocus, StudentRegistration
from rps_app.models import TeacherClass, Student
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from finance.models import Fee, StudentFee, PayFee, Discount, StudentFocus, StudentRegistration
from rps_app.models import TeacherClass, Student
import logging

logger = logging.getLogger(__name__)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
import json
import requests
from requests.auth import HTTPBasicAuth
import logging
from django.db import transaction
from .decorators import accountant_role_required
from django.urls import reverse

logger = logging.getLogger(__name__)
@accountant_role_required
def fee_management(request):
    user = request.user
    creator = getattr(request, 'creator', user)
    selected_class_id = request.GET.get('class_id')
    selected_fee_id = request.GET.get('fee_id')
    status_filter = request.GET.get('status')
    focus_filter = request.GET.get('focus')
    date_range_start = request.GET.get('date_range_start')
    date_range_end = request.GET.get('date_range_end')
    search_query = request.GET.get('search')

    # Filter TeacherClass by creator, including academic year
    teacher_classes = TeacherClass.objects.filter(user=creator, academicclassyear__active_year=True).select_related('ClassName', 'academicclassyear').distinct()

    # Filter Fees by teacher_classes and creator
    fees = Fee.objects.filter(teacherclass__in=teacher_classes, user=creator).distinct() if teacher_classes.exists() else Fee.objects.none()

    selected_class = None
    selected_fee = None

    if selected_class_id:
        fees = fees.filter(teacherclass__id=selected_class_id)
        try:
            selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=creator)
        except Exception as e:
            logger.error(f"Error fetching selected class {selected_class_id}: {e}")
            messages.error(request, "Invalid class selected.")

    student_fee_data = []
    summary = None

    if selected_class_id and selected_fee_id:
        try:
            selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=creator)
            selected_fee = Fee.objects.filter(id=selected_fee_id, teacherclass__id=selected_class_id, user=creator).first()
            if not selected_fee:
                logger.warning(f"No fee found for fee_id={selected_fee_id} and class_id={selected_class_id}")
                messages.error(request, "Selected fee is not associated with the chosen class.")
            else:
                student_fees = StudentFee.objects.filter(
                    teacherclass_id=selected_class_id,
                    fee__id=selected_fee_id
                ).select_related('student', 'fee')

                logger.debug(f"Fetched {student_fees.count()} student fee records for teacherclass_id={selected_class_id}, fee_id={selected_fee_id}")

                from collections import defaultdict
                student_ids = [sf.student_id for sf in student_fees]
                online_paid_by_student = defaultdict(Decimal)
                completed_totals_by_payment = defaultdict(Decimal)
                completed_statuses = [PaymentTransaction.TX_COMPLETED, PaymentTransaction.TX_SUCCESS]
                student_online_payments = StudentPayment.objects.filter(
                    teacherclass_id=selected_class_id,
                    fee_id=selected_fee_id,
                    student_id__in=student_ids,
                ).prefetch_related("transactions")
                payment_by_id = {payment.id: payment for payment in student_online_payments}
                if payment_by_id:
                    online_transactions = PaymentTransaction.objects.filter(
                        payment_id__in=payment_by_id.keys(),
                        tx_status__in=completed_statuses,
                    )
                    for tx in online_transactions:
                        payment = payment_by_id.get(tx.payment_id)
                        if not payment:
                            continue
                        completed_totals_by_payment[payment.id] += tx.amount
                        online_paid_by_student[payment.student_id] += tx.amount

                    for payment in student_online_payments:
                        if payment.status != StudentPayment.STATUS_PAID:
                            continue
                        completed_total = completed_totals_by_payment.get(payment.id, Decimal("0.00"))
                        if payment.amount_paid <= completed_total:
                            continue
                        online_paid_by_student[payment.student_id] += payment.amount_paid - completed_total

                for sf in student_fees:
                    # Fetch payments
                    payments = PayFee.objects.filter(
                        student=sf.student,
                        fee=sf.fee,
                        user=creator
                    ).order_by('date_paid')
                    total_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
                    online_paid = online_paid_by_student.get(sf.student_id, Decimal("0.00"))
                    total_paid += online_paid
                    discount = Discount.objects.filter(
                        student=sf.student,
                        fee=sf.fee,
                        teacherclass_id=selected_class_id,
                        user=creator
                    ).first()
                    discount_amount = discount.discount_amount if discount else Decimal('0.00')
                    balance = sf.amount_required - total_paid - discount_amount
                    status = 'Complete' if balance == 0 else ('Complete & Exceed' if balance < 0 else 'Remain')

                    # Calculate payment status
                    payment_status = 'No Payment'
                    if payments.exists():
                        payment_dates = payments.values_list('date_paid', flat=True)
                        if any(sf.start_date <= date_paid <= sf.end_date for date_paid in payment_dates):
                            payment_status = 'On Time'
                        elif all(date_paid < sf.start_date for date_paid in payment_dates):
                            payment_status = 'Advance'
                        elif all(date_paid > sf.end_date for date_paid in payment_dates):
                            payment_status = 'Late'

                    # Fetch initial payment from StudentRegistration
                    student_registration = StudentRegistration.objects.filter(
                        studentfocus__student=sf.student,
                        user=creator
                    ).first()
                    initial_payment = student_registration.initial_payment if student_registration and student_registration.initial_payment is not None else Decimal('0.00')
                    joined_date = student_registration.joined_date.strftime('%Y-%m-%d') if student_registration and student_registration.joined_date else 'Not registered'
                    focus = StudentFocus.objects.filter(student=sf.student, user=creator).first()
                    focus_value = focus.focus if focus else 'No focus'

                    include = True
                    if status_filter and status != status_filter:
                        include = False
                    if focus_filter and focus_value != focus_filter:
                        include = False
                    if date_range_start and joined_date != 'Not registered' and joined_date < date_range_start:
                        include = False
                    if date_range_end and joined_date != 'Not registered' and joined_date > date_range_end:
                        include = False
                    if search_query and search_query.lower() not in sf.student.fullName.lower():
                        include = False

                    if include:
                        student_fee_data.append({
                            'student_id': sf.student.id,
                            'student_name': sf.student.fullName,
                            'amount_required': sf.amount_required,
                            'total_paid': total_paid,
                            'balance': balance,
                            'status': status,
                            'discount_amount': discount_amount,
                            'has_discount': discount_amount > 0,
                            'joined_date': joined_date,
                            'focus': focus_value,
                            'payment_status': payment_status,
                            'initial_payment': initial_payment
                        })

                if student_fee_data:
                    total_payments = sum(data['total_paid'] for data in student_fee_data)
                    total_expected_fees = sum(data['amount_required'] for data in student_fee_data)
                    complete_count = sum(1 for data in student_fee_data if data['status'] == 'Complete')
                    remain_count = sum(1 for data in student_fee_data if data['status'] == 'Remain')
                    students_exceeded = sum(1 for data in student_fee_data if data['status'] == 'Complete & Exceed')
                    total_complete_amount = sum(data['total_paid'] for data in student_fee_data if data['status'] == 'Complete')
                    total_remaining_amount = sum(data['balance'] for data in student_fee_data if data['status'] == 'Remain')
                    total_exceed = sum(-data['balance'] for data in student_fee_data if data['status'] == 'Complete & Exceed')
                    students_with_discounts = sum(1 for data in student_fee_data if data['has_discount'])
                    total_discount_amount = sum(data['discount_amount'] for data in student_fee_data if data['has_discount'])
                    total_initial_payments = sum(data['initial_payment'] for data in student_fee_data)
                    students_with_initial_payments = sum(1 for data in student_fee_data if data['initial_payment'] > 0)

                    summary = {
                        'total_payments': total_payments,
                        'total_expected_fees': total_expected_fees,
                        'complete_count': complete_count,
                        'remain_count': remain_count,
                        'students_exceeded': students_exceeded,
                        'total_complete_amount': total_complete_amount,
                        'total_remaining_amount': total_remaining_amount,
                        'total_exceed': total_exceed,
                        'students_with_discounts': students_with_discounts,
                        'total_discount_amount': total_discount_amount,
                        'total_initial_payments': total_initial_payments,
                        'students_with_initial_payments': students_with_initial_payments
                    }
        except Exception as e:
            logger.error(f"Error fetching student fee data: {e}")
            messages.error(request, "Error loading student fee data.")

    context = {
        'teacher_classes': teacher_classes,
        'fees': fees,
        'selected_class_id': selected_class_id,
        'selected_fee_id': selected_fee_id,
        'student_fee_data': student_fee_data,
        'selected_class': selected_class,
        'selected_fee': selected_fee,
        'summary': summary,
        'status_filter': status_filter,
        'focus_filter': focus_filter,
        'date_range_start': date_range_start,
        'date_range_end': date_range_end,
        'search_query': search_query
    }
    return render(request, 'accountant/fee_management.html', context)


@accountant_role_required
def apply_payment(request, student_id, fee_id, class_id):
    if request.method == 'POST':
        user = request.user
        creator = getattr(request, 'creator', user)
        amount_paid = request.POST.get('amount_paid')
        date_paid = request.POST.get('date_paid')
        payer_account_no = request.POST.get('payer_account_no')
        description = request.POST.get('description')
        try:
            amount_paid = Decimal(amount_paid)
            if amount_paid <= 0:
                raise ValueError("Payment amount must be positive.")
            student = get_object_or_404(Student, id=student_id, manager=creator)
            fee = get_object_or_404(Fee, id=fee_id, teacherclass__id=class_id, user=creator)
            teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator)
            student_fee = get_object_or_404(StudentFee, student=student, fee=fee, teacherclass_id=class_id)

            payment = PayFee(
                user=creator,
                student=student,
                fee=fee,
                amount_paid=amount_paid,
                date_paid=date_paid,
                payer_account_no=payer_account_no,
                description=description
            )
            payment.full_clean()
            payment.save()

            ChangeLog.objects.create(
                user=user,
                action='CREATE',
                model_name='PayFee',
                object_id=payment.id,
                description=f"Payment of {amount_paid} for student {student.fullName} on fee {fee.fee_name}"
            )
            messages.success(request, f"Payment of {amount_paid} recorded successfully.")
            logger.debug(f"Payment recorded: {amount_paid} for student {student.fullName} on fee {fee.fee_name}")
        except ValueError as e:
            messages.error(request, f"Invalid payment amount: {str(e)}")
            logger.error(f"Invalid payment amount: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error recording payment: {str(e)}")
            logger.error(f"Error recording payment: {str(e)}")

        # Preserve all query parameters
        query_params = request.GET.copy()
        query_params.update({'class_id': class_id, 'fee_id': fee_id})
        redirect_url = f"{reverse('finance:fee_management')}?{query_params.urlencode()}"
        return redirect(redirect_url)
    return redirect('finance:fee_management')

@accountant_role_required
def apply_discount(request, student_id, fee_id, class_id):
    if request.method == 'POST':
        user = request.user
        creator = getattr(request, 'creator', user)
        discount_amount = request.POST.get('discount_amount')
        try:
            discount_amount = Decimal(discount_amount)
            if discount_amount < 0:
                raise ValueError("Discount amount cannot be negative.")

            # Verify StudentFee exists to ensure the student is associated with the fee and class
            student_fee = get_object_or_404(
                StudentFee,
                student_id=student_id,
                fee_id=fee_id,
                teacherclass_id=class_id
            )
            student = student_fee.student
            fee = student_fee.fee
            teacherclass = student_fee.teacherclass

            # Verify Fee and TeacherClass for consistency
            fee = get_object_or_404(Fee, id=fee_id, teacherclass_id=class_id, user=creator)
            teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator)

            discount, created = Discount.objects.get_or_create(
                student=student,
                fee=fee,
                teacherclass=teacherclass,
                user=creator,
                defaults={'discount_amount': discount_amount}
            )
            if not created:
                discount.discount_amount = discount_amount
                discount.save()

            ChangeLog.objects.create(
                user=user,
                action='CREATE' if created else 'UPDATE',
                model_name='Discount',
                object_id=discount.id,
                description=f"{'Created' if created else 'Updated'} discount of {discount_amount} for student {student.fullName} on fee {fee.fee_name}"
            )
            messages.success(request, f"Discount of {discount_amount} {'applied' if created else 'updated'} successfully.")
            logger.debug(f"Discount {'applied' if created else 'updated'}: {discount_amount} for student {student.fullName} on fee {fee.fee_name}")
        except ValueError as e:
            messages.error(request, f"Invalid discount amount: {str(e)}")
            logger.error(f"Invalid discount amount: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error applying discount: {str(e)}")
            logger.error(f"Error applying discount: {str(e)}")

        # Preserve all query parameters
        query_params = request.GET.copy()
        query_params.update({'class_id': class_id, 'fee_id': fee_id})
        redirect_url = f"{reverse('finance:fee_management')}?{query_params.urlencode()}"
        return redirect(redirect_url)
    return redirect('finance:fee_management')

@accountant_role_required
def update_discount(request):
    if request.method == 'POST':
        user = request.user

        # Check if request.creator is set (for logging consistency)
        if not hasattr(request, 'creator') or not request.creator:
            logger.warning(f"Creator not set for user {user.username} in update_discount, defaulting to user")
            creator = request.user
        else:
            creator = request.creator
            logger.debug(f"Updating discount for user {user.username}, creator {creator.username}")

        student_id = request.POST.get('student_id')
        fee_id = request.POST.get('fee_id')
        class_id = request.POST.get('class_id')
        discount_amount = request.POST.get('discount_amount')

        if not all([student_id, fee_id, class_id, discount_amount]):
            error_message = 'Missing required parameters.'
            logger.error(f"Missing parameters: student_id={student_id}, fee_id={fee_id}, class_id={class_id}, discount_amount={discount_amount} for user {user.username}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message}, status=400)
            messages.error(request, error_message)
            return redirect('finance:fee_management')

        try:
            # Fetch Student (no manager restriction)
            student = get_object_or_404(Student, id=student_id)
            # Fetch Fee, ensuring it is associated with the given class
            fee = get_object_or_404(Fee, id=fee_id, teacherclasses__id=class_id)
            # Fetch TeacherClass, ensuring active academic year
            teacherclass = get_object_or_404(
                TeacherClass,
                id=class_id,
                academicclassyear__active_year=True
            )
            discount_amount = Decimal(discount_amount)

            if discount_amount <= 0:
                error_message = 'Discount amount must be positive.'
                logger.error(f"Invalid discount_amount {discount_amount} for student {student_id}, fee {fee_id}, class {class_id}, user {user.username}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': error_message}, status=400)
            messages.error(request, error_message)
            return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

            if discount_amount > fee.amount:
                error_message = f'Discount cannot exceed fee amount ({fee.amount}).'
                logger.error(f"Discount {discount_amount} exceeds fee amount {fee.amount} for student {student_id}, fee {fee_id}, user {user.username}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': error_message}, status=400)
                messages.error(request, error_message)
                return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

            # Find existing discount (no user restriction)
            discount = Discount.objects.filter(
                student=student,
                fee=fee,
                teacherclass=teacherclass
            ).first()

            if not discount:
                error_message = 'No discount found to update.'
                logger.error(f"No discount found for student {student_id}, fee {fee_id}, class {class_id}, user {user.username}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': error_message}, status=404)
                messages.error(request, error_message)
                return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

            with transaction.atomic():
                discount.discount_amount = discount_amount
                discount.save()

                ChangeLog.objects.create(
                    user=user,
                    action='UPDATE',
                    model_name='Discount',
                    object_id=str(discount.id),
                    description=f"Updated discount to {discount_amount} for student {student.fullName} on fee {fee.fee_name} in class {teacherclass.ClassName.class_name} by user {user.username}"
                )

            success_message = f'Discount updated to {discount_amount} for {student.fullName} in {teacherclass.ClassName.class_name}.'
            logger.debug(f"Discount updated to {discount_amount} for student {student.fullName}, fee {fee.fee_name}, class {teacherclass.ClassName.class_name} by user {user.username}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': success_message})
            messages.success(request, success_message)
            return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

        except (ValueError, TypeError) as e:
            error_message = 'Invalid input data.'
            logger.error(f"Invalid input: {str(e)} for student {student_id}, fee {fee_id}, class {class_id}, user {user.username}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message}, status=400)
            messages.error(request, error_message)
            return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error updating discount: {str(e)} for user {user.username}", exc_info=True)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message}, status=400)
            messages.error(request, error_message)
            return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

    error_message = 'Invalid request method.'
    logger.debug(f"Invalid request method for update_discount by user {request.user.username}")
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': error_message}, status=405)
    messages.error(request, error_message)
    return redirect('finance:fee_management')
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.contrib import messages
from urllib.parse import urlencode
from decimal import Decimal
import logging
from .forms import PayFeeForm
from .decorators import accountant_role_required
from .models import PayFee, WhatsAppMessage, WhatsAppSetting
from finance.services.whatsapp import DEFAULT_BASE_URL, delete_message, is_on_whatsapp, send_message, update_message

logger = logging.getLogger(__name__)


def _get_whatsapp_setting(request):
    try:
        setting = WhatsAppSetting.objects.filter(user=request.user, is_active=True).first()
    except (OperationalError, ProgrammingError):
        logger.warning('WhatsAppSetting.is_active is unavailable in the current database schema; falling back to user-only lookup.')
        setting = WhatsAppSetting.objects.filter(user=request.user).first()
    return setting


def format_phone(phone):
    phone = str(phone or '').strip()
    phone = phone.replace(' ', '')

    print("ORIGINAL PHONE:", phone)

    if not phone:
        print("FORMATTED PHONE:", '')
        return ''

    if phone.startswith("255"):
        phone = "+" + phone
    if phone.startswith("0"):
        phone = "+255" + phone[1:]
    if not phone.startswith("+"):
        phone = "+" + phone

    if phone.startswith("+"):
        phone = "+" + ''.join(ch for ch in phone[1:] if ch.isdigit())

    print("FORMATTED PHONE:", phone)
    return phone


def _get_student_whatsapp_contact(student):
    guardian = getattr(student, 'guardian_information', None)
    if guardian and guardian.phone_number:
        return guardian.guardian_name or 'Parent', guardian.phone_number

    sponsor = getattr(student, 'sponsor_information', None)
    if sponsor and sponsor.phone_number:
        return sponsor.contact_person or sponsor.sponsor_name or 'Parent', sponsor.phone_number

    return 'Parent', student.contact


def _get_whatsapp_base_url(setting):
    if setting and getattr(setting, 'base_url', None):
        return setting.base_url
    return DEFAULT_BASE_URL


def _build_payment_message(payment):
    parent_name, _ = _get_student_whatsapp_contact(payment.student)
    reference = payment.payment_reference or 'N/A'
    payment_method = payment.get_payment_method_display() if hasattr(payment, 'get_payment_method_display') else payment.payment_method
    payment_date = payment.date_paid.strftime('%Y-%m-%d') if payment.date_paid else 'N/A'
    return (
        f"Hello {parent_name},\n\n"
        "Payment received successfully.\n\n"
        f"Student: {payment.student.fullName}\n"
        f"Fee: {payment.fee.fee_name}\n"
        f"Amount Paid: TZS {payment.amount_paid}\n"
        f"Method: {payment_method}\n"
        f"Reference: {reference}\n"
        f"Date: {payment_date}\n\n"
        "Thank you."
    )


def _get_latest_whatsapp_message(payment):
    message_obj = payment.whatsapp_messages.order_by('created_at', 'id').last()
    if not message_obj:
        print('No record found')
        return None
    return message_obj


def _notify_payment_via_whatsapp(request, payment):
    message_obj = None
    try:
        setting = _get_whatsapp_setting(request)
        if not setting:
            print('ERROR: API KEY NOT FOUND')
            return False, 'API key missing'

        api_key = setting.api_key
        base_url = _get_whatsapp_base_url(setting)
        message_text = _build_payment_message(payment)
        _, phone = _get_student_whatsapp_contact(payment.student)

        print("========== WHATSAPP DEBUG START ==========")
        print("USER:", request.user)
        print("API KEY LENGTH:", len(api_key) if api_key else 0)
        print("RAW PHONE:", phone)
        print("BASE URL:", base_url)
        print("PAYMENT ID:", payment.id)

        normalized_phone = format_phone(phone)
        message_obj = WhatsAppMessage.objects.create(
            user=request.user,
            student=payment.student,
            payment=payment,
            phone_number=normalized_phone,
            message=message_text,
            status="pending",
        )

        if not api_key:
            print("ERROR: API KEY IS MISSING")
            message_obj.status = 'failed'
            message_obj.api_response = {'success': False, 'message': 'WhatsApp API key not configured'}
            message_obj.save(update_fields=['status', 'api_response', 'updated_at'])
            return False, 'WhatsApp API key not configured'

        if not normalized_phone:
            print("ERROR: FORMATTED PHONE IS EMPTY")
            message_obj.status = 'failed'
            message_obj.api_response = {'success': False, 'message': 'No parent phone number was found for WhatsApp notification.'}
            message_obj.save(update_fields=['status', 'api_response', 'updated_at'])
            return False, 'No parent phone number was found for WhatsApp notification.'

        try:
            check_response = is_on_whatsapp(normalized_phone, api_key, base_url)
            print("CHECK FULL RESPONSE:", check_response)
            print("CHECK SUCCESS:", check_response.get("success") if isinstance(check_response, dict) else None)
            print("CHECK EXISTS:", check_response.get("data", {}).get("exists") if isinstance(check_response, dict) else None)
            logger.info('Wasender check response for payment %s: %s', payment.id, check_response)
            if not check_response.get('success'):
                print("ERROR: WhatsApp check failed:", check_response)
                message_obj.status = 'failed'
                message_obj.api_response = check_response
                message_obj.save(update_fields=['status', 'api_response', 'updated_at'])
                return False, 'Failed to verify the number on WhatsApp.'

            if not check_response.get('data', {}).get('exists'):
                print("ERROR: NUMBER IS NOT ON WHATSAPP")
                message_obj.status = 'not_on_whatsapp'
                message_obj.api_response = check_response
                message_obj.save(update_fields=['status', 'api_response', 'updated_at'])
                return False, 'Number is not on WhatsApp'

            print("SENDING MESSAGE TO:", normalized_phone)
            print("MESSAGE TEXT:", message_text)
            response = send_message(normalized_phone, message_text, api_key, base_url)
            print("SEND RESPONSE:", response)
            logger.info('Wasender send response for payment %s: %s', payment.id, response)
            message_obj.api_response = response

            if response.get('success'):
                msg_id = response.get('data', {}).get('msgId')
                print("MESSAGE SENT SUCCESSFULLY, MSG ID:", msg_id)
                message_obj.msg_id = str(msg_id) if msg_id else None
                message_obj.status = 'sent'
                message_obj.save(update_fields=['api_response', 'msg_id', 'status', 'updated_at'])
                return True, 'Payment saved and WhatsApp notification sent successfully.'

            print("ERROR: WhatsApp API returned failure:", response)
            message_obj.status = 'failed'
            message_obj.save(update_fields=['api_response', 'status', 'updated_at'])
            return False, 'Payment saved, but WhatsApp notification failed.'
        except Exception as e:
            print("WHATSAPP ERROR:", str(e))
            message_obj.status = 'failed'
            message_obj.api_response = {'success': False, 'message': str(e)}
            message_obj.save(update_fields=['status', 'api_response', 'updated_at'])
            return False, f'WhatsApp notification crashed: {str(e)}'
    except Exception as e:
        print("WHATSAPP ERROR:", str(e))
        import traceback
        traceback.print_exc()
        if message_obj is not None:
            message_obj.status = 'failed'
            message_obj.api_response = {'success': False, 'message': str(e)}
            message_obj.save(update_fields=['status', 'api_response', 'updated_at'])
        return False, f'WhatsApp notification crashed: {str(e)}'


def _update_payment_whatsapp_message(request, payment):
    try:
        message_obj = _get_latest_whatsapp_message(payment)
        if not message_obj:
            print('No record found')
            return _notify_payment_via_whatsapp(request, payment)

        if not message_obj.msg_id:
            print('No WhatsApp msg_id found; falling back to send flow')
            return _notify_payment_via_whatsapp(request, payment)

        setting = _get_whatsapp_setting(request)
        if not setting:
            print('ERROR: API KEY NOT FOUND')
            return False, 'API key missing'

        api_key = setting.api_key
        base_url = _get_whatsapp_base_url(setting)
        if not api_key:
            print('ERROR: API KEY NOT FOUND')
            return False, 'WhatsApp API key not configured'

        new_text = _build_payment_message(payment)
        response = update_message(message_obj.msg_id, new_text, api_key, base_url)

        print("UPDATE RESPONSE:", response)
        logger.info('Wasender update response for payment %s: %s', payment.id, response)

        message_obj.message = new_text
        message_obj.api_response = response
        if response.get('success'):
            message_obj.status = 'updated'
            message_obj.save(update_fields=['message', 'status', 'api_response', 'updated_at'])
            return True, 'WhatsApp message updated successfully.'

        message_obj.status = 'update_failed'
        message_obj.save(update_fields=['message', 'status', 'api_response', 'updated_at'])
        return False, 'Payment updated, but WhatsApp message update failed.'
    except Exception as e:
        print("WHATSAPP ERROR:", str(e))
        logger.exception('WhatsApp update crashed for payment %s', payment.id)
        return False, f'Payment updated, but WhatsApp message update crashed: {str(e)}'


def _delete_payment_whatsapp_message(request, payment):
    try:
        message_obj = _get_latest_whatsapp_message(payment)
        if not message_obj:
            print('No record found')
            return False, 'No WhatsApp message is linked to this payment.'

        if not message_obj.msg_id:
            print('No WhatsApp msg_id found for delete flow')
            return False, 'No WhatsApp message is linked to this payment.'

        setting = _get_whatsapp_setting(request)
        if not setting:
            print('ERROR: API KEY NOT FOUND')
            return False, 'API key missing'

        api_key = setting.api_key
        base_url = _get_whatsapp_base_url(setting)
        if not api_key:
            print('ERROR: API KEY NOT FOUND')
            return False, 'WhatsApp API key not configured'

        response = delete_message(message_obj.msg_id, api_key, base_url)

        print("DELETE RESPONSE:", response)
        logger.info('Wasender delete response for payment %s: %s', payment.id, response)
        message_obj.api_response = response

        if response.get('success'):
            print('Message deleted successfully')
            message_obj.status = 'deleted'
            message_obj.save(update_fields=['status', 'api_response', 'updated_at'])
            return True, 'WhatsApp message deleted successfully.'

        message_obj.status = 'delete_failed'
        message_obj.save(update_fields=['status', 'api_response', 'updated_at'])
        return False, 'WhatsApp message could not be deleted.'
    except Exception as e:
        print("WHATSAPP ERROR:", str(e))
        logger.exception('WhatsApp delete crashed for payment %s', payment.id)
        return False, f'WhatsApp message delete crashed: {str(e)}'


@accountant_role_required
def view_payment_records(request, student_id, fee_id, class_id):
    user = request.user
    creator = getattr(request, 'creator', user)
    try:
        student = get_object_or_404(Student, id=student_id, manager=creator)
        fee = get_object_or_404(Fee, id=fee_id, teacherclass__id=class_id, user=creator)
        teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator)
        payments = list(
            PayFee.objects.filter(student=student, fee=fee).prefetch_related('whatsapp_messages')
        )
        sent_count = sum(1 for payment in payments if payment.whatsapp_status == 'sent')
        failed_count = sum(1 for payment in payments if payment.whatsapp_status in {'failed', 'update_failed', 'delete_failed'})
        not_on_whatsapp_count = sum(1 for payment in payments if payment.whatsapp_status == 'not_on_whatsapp')

        context = {
            'payments': payments,
            'student': student,
            'fee': fee,
            'selected_class': teacherclass,
            'selected_fee': fee,
            'query_params': request.GET.urlencode(),
            'sent_count': sent_count,
            'failed_count': failed_count,
            'not_on_whatsapp_count': not_on_whatsapp_count,
        }
        return render(request, 'accountant/payment_records.html', context)
    except Exception as e:
        logger.error(f"Error fetching payment records: {str(e)}")
        messages.error(request, f"Error fetching payment records: {str(e)}")
        redirect_url = f"{reverse('finance:fee_management')}?{urlencode({'class_id': class_id, 'fee_id': fee_id})}"
        return redirect(redirect_url)

@accountant_role_required
def delete_payment(request, student_id, class_id, fee_id):
    user = request.user
    creator = getattr(request, 'creator', user)

    payments = PayFee.objects.filter(
        student__id=student_id,
        student__teacherclass__id=class_id,
        fee__id=fee_id,
        student__manager=creator
    )

    redirect_url = f"{reverse('finance:fee_management')}?{urlencode({'class_id': class_id, 'fee_id': fee_id})}"

    if request.method == 'POST':
        if not payments.exists():
            messages.error(request, "No payments found for this student.")
            logger.debug(f"No payments found for student_id {student_id}, class_id {class_id}, fee_id {fee_id} by user {user.username}")
            return redirect(redirect_url)

        try:
            student_full_name = payments.first().student.fullName
            fee_name = payments.first().fee.fee_name
            deleted_count = payments.delete()[0]
            
            ChangeLog.objects.create(
                user=user,
                action='DELETE',
                model_name='PayFee',
                object_id=f"student_{student_id}_fee_{fee_id}",
                description=f"Deleted {deleted_count} payment(s) for student {student_full_name}, fee {fee_name}"
            )
            messages.success(request, f"Successfully deleted {deleted_count} payment(s)!")
            logger.debug(f"Deleted {deleted_count} payment(s) for student {student_full_name}, fee {fee_name} by user {user.username} for creator {creator.username}")
        except Exception as e:
            messages.error(request, f"Error deleting payments: {str(e)}")
            logger.error(f"Error deleting payments for student_id {student_id}, class_id {class_id}, fee_id {fee_id}: {str(e)}", exc_info=True)
        
        return redirect(redirect_url)

    messages.warning(request, "Deletion must be done via the confirmation button.")
    logger.debug(f"Invalid request method for deleting payments for student_id {student_id}, class_id {class_id}, fee_id {fee_id} by user {user.username}")
    return redirect(redirect_url)

@accountant_role_required
def delete_single_payment(request, payment_id, class_id, fee_id):
    user = request.user
    creator = getattr(request, 'creator', user)

    payment = get_object_or_404(PayFee, id=payment_id, student__manager=creator, fee__id=fee_id, student__teacherclass__id=class_id)
    redirect_url = f"{reverse('finance:fee_management')}?{urlencode({'class_id': class_id, 'fee_id': fee_id})}"

    if request.method == 'POST':
        try:
            student_full_name = payment.student.fullName
            fee_name = payment.fee.fee_name
            payment_amount = payment.amount_paid

            latest_message = _get_latest_whatsapp_message(payment)
            if latest_message and latest_message.msg_id:
                whatsapp_deleted, whatsapp_message = _delete_payment_whatsapp_message(request, payment)
                if whatsapp_deleted:
                    messages.success(request, whatsapp_message)
                else:
                    logger.warning('WhatsApp delete skipped/failed for payment %s: %s', payment.id, whatsapp_message)

            payment.delete()
            ChangeLog.objects.create(
                user=user,
                action='DELETE',
                model_name='PayFee',
                object_id=payment_id,
                description=f"Deleted payment of {payment_amount} for student {student_full_name}, fee {fee_name}"
            )
            messages.success(request, "Payment deleted successfully!")
            logger.debug(f"Payment {payment_id} deleted for student {student_full_name}, fee {fee_name} by user {user.username} for creator {creator.username}")
        except Exception as e:
            messages.error(request, f"Error deleting payment: {str(e)}")
            logger.error(f"Error deleting payment {payment_id}: {str(e)}", exc_info=True)
        
        return redirect(redirect_url)

    messages.warning(request, "Deletion must be done via the confirmation button.")
    logger.debug(f"Invalid request method for payment {payment_id} by user {user.username}")
    return redirect(redirect_url)

@accountant_role_required
def edit_payment(request, payment_id, class_id, fee_id):
    user = request.user
    creator = getattr(request, 'creator', user)

    payment = get_object_or_404(PayFee, id=payment_id, student__manager=creator, fee__id=fee_id, student__teacherclass__id=class_id)
    student = payment.student
    fee = payment.fee

    if request.method == 'POST':
        form = PayFeeForm(request.POST, instance=payment)
        if form.is_valid():
            try:
                payment = form.save()
                ChangeLog.objects.create(
                    user=user,
                    action='UPDATE',
                    model_name='PayFee',
                    object_id=payment.id,
                    description=f"Updated payment of {payment.amount_paid} for {student.fullName}, fee {fee.fee_name}"
                )
                messages.success(request, f"Payment for {student.fullName} updated successfully!")
                logger.debug(f"Payment {payment_id} updated for student {student.fullName}, fee {fee.fee_name} by user {user.username} for creator {creator.username}")
                
                query_params = {'class_id': class_id, 'fee_id': fee_id}
                redirect_url = f"{reverse('finance:fee_management')}?{urlencode(query_params)}"
                return redirect(redirect_url)
            except Exception as e:
                messages.error(request, f"Error updating payment: {str(e)}")
                logger.error(f"Error updating payment {payment_id}: {str(e)}", exc_info=True)
        else:
            messages.error(request, "Please correct the errors below.")
            logger.error(f"Form errors: {form.errors.as_json()} for payment {payment_id}")
    else:
        form = PayFeeForm(instance=payment)

    context = {
        'form': form,
        'student': student,
        'fee': fee,
        'payment': payment,
        'class_id': class_id,
        'fee_id': fee.id,
        'active_tab': 'accountant'
    }
    return render(request, 'accountant/edit_payment.html', context)
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)


@accountant_role_required
def pay_fee(request, student_id, fee_id):
    user = request.user
    creator = request.creator  # Set by accountant_role_required: request.user for superusers, Teacher.created_by otherwise

    student = get_object_or_404(Student, id=student_id, manager=creator)
    fee = get_object_or_404(Fee, id=fee_id, teacherclass__user=creator)
    class_id = student.teacherclass.id

    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        payer_account_no = request.POST.get('payer_account_no', '').strip()
        description = request.POST.get('description', '').strip()
        amount_paid_str = request.POST.get('amount_paid')
        payment_method = request.POST.get('payment_method', PayFee.PAYMENT_METHOD_CASH)
        payment_reference = request.POST.get('payment_reference', '').strip()
        date_paid_str = request.POST.get('date_paid')

        redirect_url = reverse('finance:pay_fee', kwargs={'student_id': student_id, 'fee_id': fee_id})

        try:
            if not amount_paid_str:
                messages.error(request, "Amount paid is required.")
                logger.error(f"Missing amount_paid for student {student_id}, fee {fee_id} by user {user.username}")
                return redirect(redirect_url)

            amount_paid = Decimal(amount_paid_str)
            if amount_paid <= 0:
                messages.error(request, "Amount paid must be a positive number.")
                logger.error(f"Invalid amount_paid {amount_paid_str} for student {student_id}, fee {fee_id}")
                return redirect(redirect_url)

            if not date_paid_str:
                messages.error(request, "Payment date is required.")
                logger.error(f"Missing date_paid for student {student_id}, fee {fee_id}")
                return redirect(redirect_url)

            date_paid = timezone.datetime.strptime(date_paid_str, '%Y-%m-%d').date()
            today = timezone.localdate()

            if date_paid > today:
                messages.error(request, "Payment date cannot be in the future.")
                logger.error(f"Future date_paid {date_paid} for student {student_id}, fee {fee_id}")
                return redirect(redirect_url)

            pay_fee_obj = PayFee.objects.create(
                user=user,
                student=student,
                fee=fee,
                payer_account_no=payer_account_no,
                description=description,
                amount_paid=amount_paid,
                payment_method=payment_method,
                payment_reference=payment_reference,
                date_paid=date_paid
            )

            ChangeLog.objects.create(
                user=user,
                action='CREATE',
                model_name='PayFee',
                object_id=pay_fee_obj.id,
                description=f"Payment of {amount_paid} for {student.fullName}, fee {fee.fee_name}"
            )

            print("ACTION:", action)
            if action == 'save_notify':
                print("TRIGGERING WHATSAPP...")
                notify_success, notify_message = _notify_payment_via_whatsapp(request, pay_fee_obj)
                print("WHATSAPP FUNCTION RESULT:", notify_success, notify_message)
                if notify_success:
                    messages.success(request, notify_message)
                else:
                    if pay_fee_obj.whatsapp_status == 'not_on_whatsapp':
                        messages.warning(request, notify_message)
                    else:
                        messages.warning(request, notify_message)
            else:
                print("WHATSAPP FUNCTION SKIPPED FOR ACTION:", action)
                messages.success(request, "Payment recorded successfully!")

            logger.debug(f"Payment of {amount_paid} recorded for student {student.fullName}, fee {fee.fee_name} by user {user.username} for creator {creator.username}")
            return redirect(f"{reverse('finance:fee_management')}?class_id={class_id}&fee_id={fee.id}")

        except (InvalidOperation, ValueError) as e:
            messages.error(request, "Invalid number or date format. Please check your input.")
            logger.error(f"Invalid input: {str(e)} for student {student_id}, fee {fee_id}")
            return redirect(redirect_url)
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            logger.error(f"Unexpected error: {str(e)} for student {student_id}, fee {fee_id}", exc_info=True)
            return redirect(redirect_url)

    context = {
        'student': student,
        'fee': fee,
        'class_id': class_id,
        'active_tab': 'accountant'
    }
    return render(request, 'accountant/pay_fee.html', context)
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

@accountant_role_required
def add_student_fee(request, student_id, class_id):
    user = request.user
    creator = request.creator  # Set by accountant_role_required: request.user for superusers, Teacher.created_by otherwise

    teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator,academicclassyear__active_year=True)
    student = get_object_or_404(Student, id=student_id, manager=creator, teacherclass=teacherclass)

    if request.method == 'POST':
        form = StudentFeeForm(request.POST, user=user, creator=creator, teacherclass=teacherclass)
        if form.is_valid():
            fee_to_assign = form.cleaned_data['fee']
            
            if not StudentFee.objects.filter(student=student, fee=fee_to_assign).exists():
                student_fee = StudentFee.objects.create(
                    user=user, student=student, teacherclass=teacherclass, fee=fee_to_assign
                )
                ChangeLog.objects.create(
                    user=user, action='CREATE', model_name='StudentFee', object_id=student_fee.id,
                    description=f"Assigned fee {student_fee.fee.fee_name} to student {student.fullName}"
                )
                messages.success(request, f"Fee assigned to {student.fullName} successfully!")
                logger.debug(f"Assigned fee {student_fee.fee.fee_name} to student {student.fullName} by user {user.username} for creator {creator.username}")
            else:
                messages.warning(request, f"{student.fullName} is already assigned this fee.")
                logger.debug(f"Fee {fee_to_assign.fee_name} already assigned to student {student.fullName}")
            
            return redirect(f"{reverse('finance:fee_management')}?class_id={class_id}")
        else:
            messages.error(request, "Error assigning fee. Please correct the errors below.")
            logger.error(f"Form errors: {form.errors.as_json()} for student {student_id}, class {class_id}")
    else:
        form = StudentFeeForm(user=user, creator=creator, teacherclass=teacherclass)

    context = {
        'form': form,
        'student': student,
        'teacherclass': teacherclass,
        'active_tab': 'accountant'
    }
    return render(request, 'accountant/add_student_fee.html', context)

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from .models import PayFee, ChangeLog
from .forms import PayFeeForm
from urllib.parse import urlencode

from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.contrib import messages
from urllib.parse import urlencode
from decimal import Decimal
import logging

from .forms import PayFeeForm
from .decorators import accountant_role_required

logger = logging.getLogger(__name__)

@accountant_role_required
def delete_payment(request, student_id, class_id, fee_id):
    user = request.user
    creator = getattr(request, 'creator', user)  # Set by accountant_role_required

    # Filter PayFee records for the student, class, and fee
    payments = PayFee.objects.filter(
        student__id=student_id,
        student__teacherclass__id=class_id,
        fee__id=fee_id,
        student__manager=creator
    )

    redirect_url = f"{reverse('finance:fee_management')}?{urlencode({'class_id': class_id, 'fee_id': fee_id})}"

    if request.method == 'POST':
        if not payments.exists():
            messages.error(request, "No payments found for this student.")
            logger.debug(f"No payments found for student_id {student_id}, class_id {class_id}, fee_id {fee_id} by user {user.username}")
            return redirect(redirect_url)

        try:
            # Get student and fee details for logging
            student_full_name = payments.first().student.fullName
            fee_name = payments.first().fee.fee_name

            for payment in payments.prefetch_related('whatsapp_messages'):
                latest_message = _get_latest_whatsapp_message(payment)
                if latest_message and latest_message.msg_id:
                    whatsapp_deleted, whatsapp_message = _delete_payment_whatsapp_message(request, payment)
                    if whatsapp_deleted:
                        messages.success(request, f"Payment {payment.id}: {whatsapp_message}")
                    else:
                        logger.warning('WhatsApp delete skipped/failed for payment %s: %s', payment.id, whatsapp_message)

            # Delete all matching payments
            deleted_count = payments.delete()[0]
            
            # Log the deletion
            ChangeLog.objects.create(
                user=user,
                action='DELETE',
                model_name='PayFee',
                object_id=f"student_{student_id}_fee_{fee_id}",
                description=f"Deleted {deleted_count} payment(s) for student {student_full_name}, fee {fee_name}"
            )
            messages.success(request, f"Successfully deleted {deleted_count} payment(s)!")
            logger.debug(f"Deleted {deleted_count} payment(s) for student {student_full_name}, fee {fee_name} by user {user.username} for creator {creator.username}")
        except Exception as e:
            messages.error(request, f"Error deleting payments: {str(e)}")
            logger.error(f"Error deleting payments for student_id {student_id}, class_id {class_id}, fee_id {fee_id}: {str(e)}", exc_info=True)
        
        return redirect(redirect_url)

    messages.warning(request, "Deletion must be done via the confirmation button.")
    logger.debug(f"Invalid request method for deleting payments for student_id {student_id}, class_id {class_id}, fee_id {fee_id} by user {user.username}")
    return redirect(redirect_url)

@accountant_role_required
def edit_payment(request, payment_id, class_id, fee_id):
    user = request.user
    creator = getattr(request, 'creator', user)

    try:
        # Fetch Fee and TeacherClass to ensure authorization
        fee = get_object_or_404(Fee, id=fee_id, teacherclass__id=class_id, user=creator)
        teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator)
        # Fetch PayFee without student__manager restriction
        payment = get_object_or_404(PayFee, id=payment_id, fee__id=fee_id, student__teacherclass__id=class_id)
        student = payment.student
    except Exception as e:
        messages.error(request, f"Error retrieving payment: {str(e)}")
        logger.error(f"Error retrieving payment {payment_id}: {str(e)}", exc_info=True)
        query_params = {'class_id': class_id, 'fee_id': fee_id}
        redirect_url = f"{reverse('finance:fee_management')}?{urlencode(query_params)}"
        return redirect(redirect_url)

    if request.method == 'POST':
        action = request.POST.get('action', 'update')
        form = PayFeeForm(request.POST, instance=payment)
        if form.is_valid():
            try:
                payment = form.save()

                whatsapp_message = None
                if action == 'update_notify':
                    whatsapp_updated, whatsapp_message = _update_payment_whatsapp_message(request, payment)
                    if whatsapp_updated:
                        messages.success(request, whatsapp_message)
                    else:
                        messages.warning(request, whatsapp_message)

                ChangeLog.objects.create(
                    user=user,
                    action='UPDATE',
                    model_name='PayFee',
                    object_id=payment.id,
                    description=f"Updated payment of {payment.amount_paid} for {student.fullName}, fee {fee.fee_name}"
                )
                if action == 'update_notify':
                    messages.success(request, f"Payment for {student.fullName} updated successfully with WhatsApp handling!")
                else:
                    messages.success(request, f"Payment for {student.fullName} updated successfully!")
                logger.debug(f"Payment {payment_id} updated for student {student.fullName}, fee {fee.fee_name} by user {user.username} for creator {creator.username}")

                query_params = {'class_id': class_id, 'fee_id': fee_id}
                redirect_url = f"{reverse('finance:fee_management')}?{urlencode(query_params)}"
                return redirect(redirect_url)
            except Exception as e:
                messages.error(request, f"Error updating payment: {str(e)}")
                logger.error(f"Error updating payment {payment_id}: {str(e)}", exc_info=True)
        else:
            messages.error(request, "Please correct the errors below.")
            logger.error(f"Form errors: {form.errors.as_json()} for payment {payment_id}")
    else:
        form = PayFeeForm(instance=payment)

    context = {
        'form': form,
        'student': student,
        'fee': fee,
        'payment': payment,
        'class_id': class_id,
        'fee_id': fee.id,
        'active_tab': 'accountant'
    }
    return render(request, 'accountant/edit_payment.html', context)
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

# @accountant_role_required
# def delete_payment(request, student_id, class_id, fee_id):
#     user = request.user
#     creator = request.creator  # Set by accountant_role_required

#     # Filter PayFee records for the student, class, and fee
#     payments = PayFee.objects.filter(
#         student__id=student_id,
#         student__teacherclass__id=class_id,
#         fee__id=fee_id,
#         student__manager=creator
#     )

#     redirect_url = f"{reverse('finance:fee_management')}?{urlencode({'class_id': class_id, 'fee_id': fee_id})}"

#     if request.method == 'POST':
#         if not payments.exists():
#             messages.error(request, "No payments found for this student.")
#             logger.debug(f"No payments found for student_id {student_id}, class_id {class_id}, fee_id {fee_id} by user {user.username}")
#             return redirect(redirect_url)

#         try:
#             # Get student and fee details for logging
#             student_full_name = payments.first().student.fullName
#             fee_name = payments.first().fee.fee_name

#             # Delete all matching payments
#             deleted_count = payments.delete()[0]
            
#             # Log the deletion
#             ChangeLog.objects.create(
#                 user=user,
#                 action='DELETE',
#                 model_name='PayFee',
#                 object_id=f"student_{student_id}_fee_{fee_id}",
#                 description=f"Deleted {deleted_count} payment(s) for student {student_full_name}, fee {fee_name}"
#             )
#             messages.success(request, f"Successfully deleted {deleted_count} payment(s)!")
#             logger.debug(f"Deleted {deleted_count} payment(s) for student {student_full_name}, fee {fee_name} by user {user.username} for creator {creator.username}")
#         except Exception as e:
#             messages.error(request, f"Error deleting payments: {str(e)}")
#             logger.error(f"Error deleting payments for student_id {student_id}, class_id {class_id}, fee_id {fee_id}: {str(e)}", exc_info=True)
        
#         return redirect(redirect_url)

    # messages.warning(request, "Deletion must be done via the confirmation button.")
    # logger.debug(f"Invalid request method for deleting payments for student_id {student_id}, class_id {class_id}, fee_id {fee_id} by user {user.username}")
    # return redirect(redirect_url)

from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)


    
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
import pandas as pd
import logging
from .models import  Fee,  PayFee, ChangeLog

from django.urls import reverse

# Set up logging
logger = logging.getLogger(__name__)

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
import pandas as pd
import logging
from .models import Fee, PayFee, ChangeLog

from django.urls import reverse

# Set up logging
logger = logging.getLogger(__name__)
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
import pandas as pd
import logging
from .models import Fee,PayFee, ChangeLog, StudentFee
from django.utils.dateparse import parse_date
from django.urls import reverse

import pandas as pd
from decimal import Decimal, InvalidOperation
# from .utils import parse_date # Assuming you have a utility function for parsing dates

# Ensure you have a logger configured at the top of your views.py
import logging
logger = logging.getLogger(__name__)
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal
from django.db.models import Sum
from datetime import datetime
import pandas as pd
from dateutil.parser import parse as parse_date
import logging
from .models import StudentFee, PayFee, Discount, Fee
from rps_app.models import Teacher, Student, TeacherClass, DisplayModel
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
import pandas as pd
import logging

logger = logging.getLogger(__name__)

@accountant_role_required
def upload_payments(request):
    user = request.user
    creator = request.creator  # Set by accountant_role_required: request.user for superusers, Teacher.created_by otherwise

    if request.method != 'POST' or 'file' not in request.FILES:
        messages.error(request, "Invalid request. Please select a file to upload.")
        logger.error(f"Invalid request: No file uploaded by user {user.username}")
        return redirect('finance:fee_management')

    selected_class_id = request.POST.get('class_id')
    selected_fee_id = request.POST.get('fee_id')

    if not selected_class_id or not selected_fee_id:
        messages.error(request, "A class and a specific fee must be selected for the upload.")
        logger.error(f"Missing class_id={selected_class_id} or fee_id={selected_fee_id} for user {user.username}")
        return redirect('finance:fee_management')

    redirect_url = f"{reverse('finance:fee_management')}?class_id={selected_class_id}&fee_id={selected_fee_id}"

    try:
        teacherclass = get_object_or_404(TeacherClass, id=selected_class_id, user=creator,academicclassyear__active_year=True)
        fee = get_object_or_404(Fee, id=selected_fee_id, teacherclasses__user=creator)

        logger.info(f"Processing upload for class: {teacherclass.ClassName}, fee: {fee.fee_name}, user: {user.username}, creator: {creator.username}")

        file = request.FILES['file']
        file_extension = file.name.split('.')[-1].lower()

        if file_extension == 'csv':
            df = pd.read_csv(file, encoding='utf-8-sig', dtype=str)
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(file, dtype=str)
        else:
            messages.error(request, "Unsupported file format. Please upload a CSV or Excel file.")
            logger.error(f"Unsupported file format: {file_extension} for user {user.username}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': "Unsupported file format. Please upload a CSV or Excel file."
                })
            return redirect(redirect_url)

        required_columns = ['indexNumber', 'amount_paid']
        if not all(col in df.columns for col in required_columns):
            messages.error(request, "File must contain 'indexNumber' and 'amount_paid' columns.")
            logger.error(f"Missing required columns: {required_columns} for user {user.username}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': "File must contain 'indexNumber' and 'amount_paid' columns."
                })
            return redirect(redirect_url)

        messages_list = []
        success_count = 0

        for index, row in df.iterrows():
            index_number = row.get('indexNumber', '').strip()
            amount_paid_str = row.get('amount_paid', '').strip()
            
            if not index_number or not amount_paid_str:
                warning_msg = f"Skipping row {index + 2}: Missing indexNumber or amount_paid."
                messages.warning(request, warning_msg)
                messages_list.append({'type': 'warning', 'message': warning_msg})
                logger.debug(warning_msg)
                continue

            try:
                amount_paid = Decimal(amount_paid_str)
                if amount_paid <= 0:
                    warning_msg = f"Skipping row {index + 2} ({index_number}): Amount paid must be positive."
                    messages.warning(request, warning_msg)
                    messages_list.append({'type': 'warning', 'message': warning_msg})
                    logger.debug(warning_msg)
                    continue
            except InvalidOperation:
                warning_msg = f"Skipping row {index + 2} ({index_number}): Invalid amount format."
                messages.warning(request, warning_msg)
                messages_list.append({'type': 'warning', 'message': warning_msg})
                logger.debug(warning_msg)
                continue

            try:
                student = Student.objects.get(indexNumber=index_number, teacherclass=teacherclass)
            except Student.DoesNotExist:
                warning_msg = f"Skipping row {index + 2}: Student with index '{index_number}' not found in class '{teacherclass.ClassName}'."
                messages.warning(request, warning_msg)
                messages_list.append({'type': 'warning', 'message': warning_msg})
                logger.debug(warning_msg)
                continue

            if not StudentFee.objects.filter(student=student, fee=fee).exists():
                warning_msg = f"Skipping row {index + 2}: Student '{student.fullName}' is not assigned the fee '{fee.fee_name}'."
                messages.warning(request, warning_msg)
                messages_list.append({'type': 'warning', 'message': warning_msg})
                logger.debug(warning_msg)
                continue
            
            payer_account_no = row.get('payer_account_no', '').strip()
            description = row.get('description', '').strip()
            date_paid_str = row.get('date_paid', '').strip()
            try:
                date_paid = timezone.datetime.strptime(date_paid_str, '%Y-%m-%d').date() if date_paid_str else timezone.localdate()
                if date_paid > timezone.localdate():
                    warning_msg = f"Skipping row {index + 2} ({index_number}): Payment date {date_paid} is in the future."
                    messages.warning(request, warning_msg)
                    messages_list.append({'type': 'warning', 'message': warning_msg})
                    logger.debug(warning_msg)
                    continue
            except ValueError:
                warning_msg = f"Skipping row {index + 2} ({index_number}): Invalid date format for date_paid."
                messages.warning(request, warning_msg)
                messages_list.append({'type': 'warning', 'message': warning_msg})
                logger.debug(warning_msg)
                continue
            
            pay_fee = PayFee.objects.create(
                user=user,
                student=student,
                fee=fee,
                payer_account_no=payer_account_no,
                description=description,
                amount_paid=amount_paid,
                date_paid=date_paid
            )
            ChangeLog.objects.create(
                user=user,
                action='CREATE',
                model_name='PayFee',
                object_id=pay_fee.id,
                description=f"Payment of {amount_paid} for {student.fullName}, fee {fee.fee_name} via file upload"
            )
            success_msg = f"Successfully processed payment for {student.fullName} ({index_number})."
            messages.success(request, success_msg)
            messages_list.append({'type': 'success', 'message': success_msg})
            success_count += 1
            logger.debug(f"Payment of {amount_paid} processed for student {student.fullName} ({index_number}), fee {fee.fee_name} by user {user.username} for creator {creator.username}")

        if success_count > 0:
            success_message = f"Successfully processed {success_count} payment(s)."
            messages.success(request, success_message)
            messages_list.append({'type': 'success', 'message': success_message})
            logger.debug(success_message)
        else:
            warning_msg = "No payments were processed successfully."
            messages.warning(request, warning_msg)
            messages_list.append({'type': 'warning', 'message': warning_msg})
            logger.debug(warning_msg)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': success_count > 0,
                'messages': messages_list
            })

    except Exception as e:
        error_msg = f"A critical error occurred during file processing: {str(e)}"
        messages.error(request, error_msg)
        logger.error(f"Critical error in upload_payments: {str(e)} for user {user.username}", exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': error_msg
            })

    return redirect(redirect_url)
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from django.utils import timezone


@accountant_role_required
def download_student_financial_pdf(request):
    if not request.user.is_student:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('login_view')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Your student profile could not be found.")
        return redirect('student_dashboard')

    teacherclass = student.teacherclass
    student_fees = StudentFee.objects.filter(
        student=student
    ).select_related('fee', 'fee__installment', 'fee__installment__academic_year')

    response = HttpResponse(content_type='application/pdf')
    filename = f"financial_report_{student.fullName}.pdf".replace(" ", "_")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        name='Header',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Center alignment
        spaceAfter=10,
        textColor=colors.darkblue,
        leading=20
    )
    subheader_style = ParagraphStyle(
        name='Subheader',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=1,  # Center alignment for student details and subtitles
        spaceAfter=8,
        textColor=colors.black
    )
    body_style = ParagraphStyle(name='Body', parent=styles['BodyText'], fontSize=10, alignment=0, spaceAfter=6)
    bold_body_style = ParagraphStyle(name='BoldBody', parent=body_style, fontName='Helvetica-Bold')
    footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=1, textColor=colors.grey)
    discount_style = ParagraphStyle(name='Discount', parent=styles['BodyText'], fontSize=10, textColor=colors.red, spaceAfter=6)

    # Get DisplayModel image for icon
    try:
        display_image = DisplayModel.objects.filter(user__in=[request.user, student.manager]).first()
        if display_image and display_image.image:
            icon = Image(display_image.image.path, width=2*cm, height=2*cm)
            icon.hAlign = 'CENTER'
            # Note: ReportLab doesn't support rounded corners; use preprocessed circular image
    except Exception as e:
        print(f"Error loading DisplayModel image: {e}")
        icon = None

    # PDF Content
    elements.append(Paragraph("Student Financial Report", header_style))
    if icon:
        elements.append(icon)
        elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"{student.fullName} - {teacherclass.ClassName}", subheader_style))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"<b>Student:</b> {student.fullName}", subheader_style))
    elements.append(Paragraph(f"<b>Index Number:</b> {student.indexNumber}", subheader_style))
    elements.append(Paragraph(f"<b>Class:</b> {teacherclass.ClassName}", subheader_style))
    elements.append(Spacer(1, 0.3*cm))

    # Fee Summary Table
    fee_table_data = [['#', 'Fee Name', 'Required', 'Paid', 'Installment', 'Date Paid']]
    total_required = Decimal('0.00')
    total_paid_all = Decimal('0.00')
    total_discounted = Decimal('0.00')

    for idx, sf in enumerate(student_fees, 1):
        fee, installment = sf.fee, sf.fee.installment
        discount = Discount.objects.filter(student=student, fee=fee).first()
        discount_amount = discount.discount_amount if discount else Decimal('0.00')
        adjusted_required = fee.amount - discount_amount
        total_discounted += discount_amount

        payments = PayFee.objects.filter(student=student, fee=fee)
        total_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
        latest_payment = payments.order_by('-date_paid').first()
        date_paid = latest_payment.date_paid.strftime('%Y-%m-%d') if latest_payment else '-'
        total_required += adjusted_required
        total_paid_all += total_paid

        fee_name = f"{fee.fee_name} (Discounted: {discount_amount:.2f})" if discount else fee.fee_name
        fee_table_data.append([
            str(idx), fee_name, f"{adjusted_required:.2f}", f"{total_paid:.2f}",
            installment.installment_name, date_paid
        ])

    elements.append(Paragraph("<b>Fee Summary</b>", subheader_style))
    fee_table = Table(fee_table_data, colWidths=[1*cm, 4*cm, 3*cm, 3*cm, 4*cm, 3*cm])
    fee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(fee_table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"<b>Total Required Amount:</b> {total_required:.2f}", body_style))
    elements.append(Paragraph(f"<b>Total Amount Paid:</b> {total_paid_all:.2f}", body_style))
    elements.append(Paragraph(f"<b>Outstanding Balance:</b> {total_required - total_paid_all:.2f}", bold_body_style))
    if total_discounted > 0:
        elements.append(Paragraph(f"<b>Total Discount Applied:</b> {total_discounted:.2f}", discount_style))
    elements.append(PageBreak())

    # Detailed Payment History Table
    payment_table_data = [['Fee Name', 'Amount Paid', 'Date Paid', 'Description']]
    for sf in student_fees:
        for payment in PayFee.objects.filter(student=student, fee=sf.fee):
            payment_table_data.append([
                sf.fee.fee_name, f"{payment.amount_paid:.2f}",
                payment.date_paid.strftime('%Y-%m-%d'), payment.description or '-'
            ])

    elements.append(Paragraph("<b>Detailed Payment History</b>", subheader_style))
    if icon:
        elements.append(icon)
        elements.append(Spacer(1, 0.5*cm))
    payment_table = Table(payment_table_data, colWidths=[4*cm, 3*cm, 3*cm, 8*cm])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))

    doc.build(elements)
    messages.success(request, 'You successfully generated the PDF, kindly check your downloads!')
    return response


@accountant_role_required
def view_change_logs(request):
    # --- START: THE FIX ---
    try:
        # Get the creator of the currently logged-in accountant
        teacher_profile = Teacher.objects.get(user=request.user)
        creator = teacher_profile.created_by
    except Teacher.DoesNotExist:
        messages.error(request, "Your account is not linked to a valid teacher profile.")
        return redirect('teacher_dashboard')

    if not creator:
        # If the accountant has no creator, show only their own logs
        logs = ChangeLog.objects.filter(user=request.user).order_by('-created_at')
    else:
        # Find all other accountants (users with a teacher profile) created by the same creator
        accountant_users = Teacher.objects.filter(created_by=creator).values_list('user', flat=True)
        # Fetch logs created by any of these accountants
        logs = ChangeLog.objects.filter(user_id__in=accountant_users).order_by('-created_at')
    # --- END: THE FIX ---
    
    return render(request, 'accountant/change_logs.html', {'logs': logs})

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from decimal import Decimal
from rps_app.models import TeacherClass, Student, Teacher, DisplayModel
from .models import Fee, StudentFee, PayFee, Discount
from .decorators import accountant_role_required
import logging

logger = logging.getLogger(__name__)
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .decorators import accountant_role_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from decimal import Decimal
from .decorators import accountant_role_required
import logging

logger = logging.getLogger(__name__)

@accountant_role_required
def download_student_fee_pdf(request, class_id, fee_id):
    user = request.user
    creator = getattr(request, 'creator', user)

    teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator, academicclassyear__active_year=True)
    fee = get_object_or_404(Fee, id=fee_id, teacherclass=teacherclass, user=creator)

    student_fees = StudentFee.objects.filter(
        fee=fee,
        teacherclass=teacherclass
    ).select_related('student', 'fee')

    response = HttpResponse(content_type='application/pdf')
    filename = f"fee_report_{teacherclass.ClassName.class_name}_{fee.fee_name}.pdf".replace(" ", "_")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4), topMargin=1.5*cm, bottomMargin=1.5*cm)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        name='Header',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=10,
        textColor=colors.darkblue,
        leading=20
    )
    subheader_style = ParagraphStyle(
        name='Subheader',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=1,
        spaceAfter=8,
        textColor=colors.black
    )
    body_style = ParagraphStyle(
        name='Body',
        parent=styles['BodyText'],
        fontSize=9,
        alignment=0,
        spaceAfter=6,
        leading=10
    )
    footer_style = ParagraphStyle(
        name='Footer',
        parent=styles['BodyText'],
        fontSize=8,
        alignment=1,
        textColor=colors.grey
    )
    discount_style = ParagraphStyle(
        name='Discount',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.red,
        spaceAfter=6
    )

    # Get DisplayModel image for icon
    try:
        display_image = DisplayModel.objects.filter(user=creator).first()
        if display_image and display_image.image:
            icon = Image(display_image.image.path, width=2*cm, height=2*cm)
            icon.hAlign = 'CENTER'
        else:
            icon = None
    except Exception as e:
        logger.warning(f"Error loading DisplayModel image: {e}")
        icon = None

    # PDF Content
    elements.append(Paragraph(f"Payment Report for {fee.fee_name}", header_style))
    if icon:
        elements.append(icon)
        elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(
        f"<b>Class:</b> {teacherclass.ClassName.class_name} | <b>Academic Year:</b> {teacherclass.academicclassyear.academic_year_name}",
        subheader_style
    ))
    elements.append(Paragraph(f"Generated by: {user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M')}", footer_style))
    elements.append(Spacer(1, 1*cm))

    # Calculate responsive column widths based on landscape A4
    page_width = landscape(A4)[0] - 2 * 1.5*cm
    col_widths = [
        0.05 * page_width,  # #
        0.12 * page_width,  # Index No.
        0.22 * page_width,  # Student Name
        0.10 * page_width,  # Required
        0.10 * page_width,  # Total Paid
        0.10 * page_width,  # Balance
        0.10 * page_width,  # Status
        0.11 * page_width,  # Bill Pay
        0.10 * page_width   # Payment Timing
    ]

    # Table Data
    table_data = [['#', 'Index No.', 'Student Name', 'Required', 'Total Paid', 'Balance', 'Status', 'Bill Pay Number', 'Payment Timing']]
    total_discounted = Decimal('0.00')
    completed_count = 0
    pending_count = 0

    student_ids = [sf.student_id for sf in student_fees]
    student_payment_map = {
        payment.student_id: payment
        for payment in StudentPayment.objects.filter(
            teacherclass=teacherclass,
            fee=fee,
            student_id__in=student_ids,
        ).prefetch_related("transactions")
    }
    all_payments = PayFee.objects.filter(
        student_id__in=student_ids,
        fee=fee
    ).select_related('student', 'fee')
    all_discounts = Discount.objects.filter(
        student_id__in=student_ids,
        fee=fee
    ).select_related('student')
    # Fetch initial payments
    student_registrations = StudentRegistration.objects.filter(
        studentfocus__student__in=student_ids,
        user=creator
    ).select_related('studentfocus__student')

    payments_map = {}
    for payment in all_payments:
        payments_map.setdefault(payment.student_id, []).append(payment)

    discounts_map = {}
    for discount in all_discounts:
        discounts_map[discount.student_id] = discount

    registrations_map = {}
    for reg in student_registrations:
        registrations_map[reg.studentfocus.student_id] = reg

    for idx, sf in enumerate(student_fees, 1):
        student = sf.student
        discount = discounts_map.get(student.id)
        discount_amount = discount.discount_amount if discount else Decimal('0.00')
        adjusted_required = sf.amount_required - discount_amount
        total_discounted += discount_amount

        student_payments = payments_map.get(student.id, [])
        manual_paid = sum(p.amount_paid for p in student_payments) if student_payments else Decimal('0.00')
        total_paid = manual_paid
        balance = adjusted_required - total_paid

        # Fetch initial payment
        registration = registrations_map.get(student.id)
        initial_payment = registration.initial_payment if registration and registration.initial_payment is not None else Decimal('0.00')

        status = "Complete" if balance <= 0 else "Remain"
        status_detail = ""
        if balance < 0:
            status_detail = f" (Overpaid: {abs(balance):.2f})"
        elif balance > 0:
            status_detail = f" (Remain: {balance:.2f})"
        if status == "Complete":
            completed_count += 1
        else:
            pending_count += 1

        payment_record = student_payment_map.get(student.id)
        latest_billpay = (
            payment_record.transactions.filter(method=PaymentTransaction.METHOD_BILLPAY).order_by("-created_at").first()
            if payment_record
            else None
        )
        bill_pay_number = ""
        if latest_billpay:
            bill_pay_number = latest_billpay.bill_pay_number or latest_billpay.payment_token or ""

        payment_timing = "No Payment"
        if student_payments:
            latest_payment = max(student_payments, key=lambda p: p.date_paid, default=None)
            if latest_payment:
                if latest_payment.date_paid < sf.start_date:
                    payment_timing = "In Advance"
                elif sf.start_date <= latest_payment.date_paid <= sf.end_date:
                    payment_timing = "On Time"
                else:
                    payment_timing = "After Deadline"

        student_name = f"{student.fullName} (Initial Payment: {initial_payment:.2f})"
        if discount:
            student_name += f" (Discounted: {discount_amount:.2f})"
        paid_display = f"{total_paid:.2f}"

        table_data.append([
            Paragraph(str(idx), body_style),
            Paragraph(student.indexNumber or '-', body_style),
            Paragraph(student_name, body_style),
            Paragraph(f"{adjusted_required:.2f}", body_style),
            Paragraph(paid_display, body_style),
            Paragraph(f"{balance:.2f}", body_style),
            Paragraph(f"{status}{status_detail}", body_style),
            Paragraph(bill_pay_number or "-", body_style),
            Paragraph(payment_timing, body_style)
        ])

    if not student_fees.exists():
        elements.append(Paragraph("No students found for this fee in the selected class.", body_style))
    else:
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
        ]))
        elements.append(table)
        if total_discounted > 0:
            elements.append(Spacer(1, 0.5*cm))
            elements.append(Paragraph(f"Total Discount Applied: {total_discounted:.2f}", discount_style))
        elements.append(Spacer(1, 0.4*cm))
        elements.append(Paragraph(f"Completed Payments: {completed_count} | Pending Payments: {pending_count}", body_style))

    doc.build(elements)
    messages.success(request, 'You successfully generated the PDF, kindly check your downloads!')
    return response

@accountant_role_required
def download_general_student_fee_pdf(request, class_id):
    user = request.user
    creator = getattr(request, 'creator', user)

    teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator, academicclassyear__active_year=True)
    students = Student.objects.filter(teacherclass=teacherclass)

    response = HttpResponse(content_type='application/pdf')
    filename = f"general_fee_report_{teacherclass.ClassName.class_name}.pdf".replace(" ", "_")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        name='Header',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=10,
        textColor=colors.darkblue,
        leading=20
    )
    subheader_style = ParagraphStyle(
        name='Subheader',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=1,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        name='Body',
        parent=styles['BodyText'],
        fontSize=9,
        alignment=0,
        spaceAfter=6,
        leading=10
    )
    footer_style = ParagraphStyle(
        name='Footer',
        parent=styles['BodyText'],
        fontSize=8,
        alignment=1,
        textColor=colors.grey
    )
    bold_style = ParagraphStyle(
        name='Bold',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',
        fontSize=9
    )
    discount_style = ParagraphStyle(
        name='Discount',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.red,
        spaceAfter=6
    )

    # Get DisplayModel image for icon
    try:
        display_image = DisplayModel.objects.filter(user=creator).first()
        if display_image and display_image.image:
            icon = Image(display_image.image.path, width=2*cm, height=2*cm)
            icon.hAlign = 'CENTER'
        else:
            icon = None
    except Exception as e:
        logger.warning(f"Error loading DisplayModel image: {e}")
        icon = None

    # PDF Content
    elements.append(Paragraph("General Student Fee Report", header_style))
    if icon:
        elements.append(icon)
        elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(
        f"<b>Class:</b> {teacherclass.ClassName.class_name} | <b>Academic Year:</b> {teacherclass.academicclassyear.academic_year_name}",
        subheader_style
    ))
    elements.append(Spacer(1, 1*cm))

    # Calculate responsive column widths based on A4 portrait
    page_width = A4[0] - 2 * 1.5*cm
    col_widths = [
        0.28 * page_width,  # Fee Name
        0.15 * page_width,  # Required
        0.15 * page_width,  # Paid
        0.15 * page_width,  # Balance
        0.12 * page_width,  # Status
        0.15 * page_width,  # Bill Pay
    ]

    # Fetch all student registrations for the class
    student_ids = [student.id for student in students]
    student_registrations = StudentRegistration.objects.filter(
        studentfocus__student__in=student_ids,
        user=creator
    ).select_related('studentfocus__student')
    registrations_map = {reg.studentfocus.student_id: reg for reg in student_registrations}

    for student in students:
        # Fetch initial payment
        registration = registrations_map.get(student.id)
        initial_payment = registration.initial_payment if registration and registration.initial_payment is not None else Decimal('0.00')

        has_discount = Discount.objects.filter(student=student, fee__teacherclass=teacherclass).exists()
        student_label = f"<b>Student:</b> {student.fullName} (Initial Payment: {initial_payment:.2f})" + (f" <font color='red'>*Discounted*</font>" if has_discount else "")

        elements.append(Paragraph(student_label, subheader_style))

        student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
        if not student_fees.exists():
            elements.append(Paragraph("No fees assigned.", body_style))
            elements.append(PageBreak())
            continue

        table_data = [['Fee Name', 'Required', 'Paid', 'Balance', 'Status', 'Bill Pay Number']]
        total_required = Decimal('0.00')
        total_paid_all = Decimal('0.00')
        total_discounted = Decimal('0.00')
        completed_count = 0
        pending_count = 0

        student_payment_map = {
            payment.fee_id: payment
            for payment in StudentPayment.objects.filter(
                student=student,
                teacherclass=teacherclass,
                fee__in=student_fees.values("fee_id"),
            ).prefetch_related("transactions")
        }
        for sf in student_fees:
            fee = sf.fee
            discount = Discount.objects.filter(student=student, fee=fee).first()
            discount_amount = discount.discount_amount if discount else Decimal('0.00')
            adjusted_required = sf.amount_required - discount_amount
            total_discounted += discount_amount

            total_paid_result = PayFee.objects.filter(student=student, fee=fee).aggregate(total=Sum('amount_paid'))
            manual_paid = total_paid_result['total'] if total_paid_result['total'] is not None else Decimal('0.00')
            total_paid = manual_paid
            balance = adjusted_required - total_paid
            total_required += adjusted_required
            total_paid_all += total_paid

            status = "Complete" if balance <= 0 else "Remain"
            if status == "Complete":
                completed_count += 1
            else:
                pending_count += 1

            payment_record = student_payment_map.get(fee.id)
            latest_billpay = (
                payment_record.transactions.filter(method=PaymentTransaction.METHOD_BILLPAY).order_by("-created_at").first()
                if payment_record
                else None
            )
            bill_pay_number = ""
            if latest_billpay:
                bill_pay_number = latest_billpay.bill_pay_number or latest_billpay.payment_token or ""

            fee_display = f"{fee.fee_name} (Discounted: {discount_amount:.2f})" if discount else fee.fee_name
            paid_display = f"{total_paid:.2f}"

            table_data.append([
                Paragraph(fee_display, body_style),
                Paragraph(f"{adjusted_required:.2f}", body_style),
                Paragraph(paid_display, body_style),
                Paragraph(f"{balance:.2f}", body_style),
                Paragraph(status, body_style),
                Paragraph(bill_pay_number or "-", body_style)
            ])

        table_data.append([
            Paragraph('TOTAL', bold_style),
            Paragraph(f"{total_required:.2f}", bold_style),
            Paragraph(f"{total_paid_all:.2f}", bold_style),
            Paragraph(f"{total_required - total_paid_all:.2f}", bold_style),
            Paragraph("-", bold_style),
            Paragraph("-", bold_style)
        ])

        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0f4f8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d0d9e5')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
        ]))
        elements.append(table)
        if total_discounted > 0:
            elements.append(Spacer(1, 0.5*cm))
            elements.append(Paragraph(f"Total Discount Applied: {total_discounted:.2f}", discount_style))
        elements.append(Spacer(1, 0.4*cm))
        elements.append(Paragraph(f"Completed Fees: {completed_count} | Pending Fees: {pending_count}", body_style))
        elements.append(Spacer(1, 0.5*cm))

        if student != students.last():
            elements.append(PageBreak())

    elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))

    # Debug: Log table data
    logger.debug(f"Class: {teacherclass.ClassName.class_name}, Students: {students.count()}")
    logger.debug(f"Student fees processed: {StudentFee.objects.filter(teacherclass=teacherclass).count()}")
    for student in students:
        logger.debug(f"Student: {student.fullName}, Table Data: {table_data}")

    doc.build(elements)
    messages.success(request, 'You successfully generated the PDF, kindly check your downloads!')
    return response
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
import requests
from requests.auth import HTTPBasicAuth
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
from decimal import Decimal
import requests
from django.contrib.auth.decorators import login_required
from django.conf import settings
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum, Q
from django.conf import settings
from decimal import Decimal
import json
import requests
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)

# Custom decorator for accountant role




from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
import json
import requests
from requests.auth import HTTPBasicAuth
import logging
from .decorators import accountant_role_required

logger = logging.getLogger(__name__)

# @accountant_role_required
# def send_remaining_fee_sms(request):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

#     # Determine creator based on superuser status
#     if request.user.is_superuser:
#         creator = request.user
#     else:
#         try:
#             teacher_profile = Teacher.objects.get(user=request.user)
#             creator = teacher_profile.created_by
#         except Teacher.DoesNotExist:
#             return JsonResponse({'success': False, 'message': 'Not authorized: User has no teacher profile.'}, status=403)

#     if not creator:
#         return JsonResponse({'success': False, 'message': 'Not authorized: No creator assigned.'}, status=403)
    
#     try:
#         data = json.loads(request.body)
#         class_id = data.get('class_id')
#         student_ids = data.get('student_ids', '').split(',') if data.get('student_ids') else []
#         student_ids = [id.strip() for id in student_ids if id.strip()]
#         if not class_id:
#             return JsonResponse({'success': False, 'message': 'Class ID is required.'}, status=400)
#         if not student_ids:
#             return JsonResponse({'success': False, 'message': 'Please select at least one student.'}, status=400)
#     except json.JSONDecodeError:
#         return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator, academicclassyear__active_year=True)
    
#     # Fetch selected students with prefetch_related for efficiency
#     students = Student.objects.filter(
#         Q(id__in=student_ids) & Q(teacherclass=teacherclass)
#     ).prefetch_related('assigned_fees__fee', 'payfee', 'discount_set')

#     if not students.exists():
#         return JsonResponse({'success': False, 'message': f"No valid students selected for {teacherclass.ClassName}."}, status=400)

#     # Fetch SMS configuration
#     try:
#         sms_config = SmsConfiguration.objects.get(user=creator)
#         url = sms_config.url_required
#         api_key = sms_config.username
#         secret_key = sms_config.pswd
#         source_addr = sms_config.source_addr
#     except SmsConfiguration.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'SMS configuration not found.'}, status=500)
    
#     success_count = 0
#     error_messages = []
#     students_with_remaining = []

#     for student in students:
#         student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#         total_required = sum(sf.amount_required for sf in student_fees)
#         # Use prefetched discount_set for efficiency
#         discounts = student.discount_set.filter(teacherclass=teacherclass, fee__in=[sf.fee for sf in student_fees])
#         total_discount = sum(d.discount_amount for d in discounts) or Decimal('0.00')
#         adjusted_required = total_required - total_discount
#         total_paid = PayFee.objects.filter(student=student, fee__in=[sf.fee for sf in student_fees]).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
#         balance = adjusted_required - total_paid

#         # Only process students with a positive balance
#         if balance > 0:
#             if not student.contact or not str(student.contact).startswith('255') or len(str(student.contact)) != 12:
#                 error_messages.append(f"Invalid contact for {student.fullName}: {student.contact}")
#                 logger.warning(f"Invalid contact for {student.fullName}: {student.contact}")
#                 continue
            
#             students_with_remaining.append(student)
            
#             sms_content = (
#                 f"Fee Reminder for {student.fullName} ({teacherclass.ClassName}):\n"
#                 f"Total Required: {total_required:.2f}\n"
#                 f"Total Discount: {total_discount:.2f}\n"
#                 f"Adjusted Required: {adjusted_required:.2f}\n"
#                 f"Total Paid: {total_paid:.2f}\n"
#                 f"Outstanding Balance: {balance:.2f}\n"
#                 f"Please settle the balance.\n"
#                 f"Powered By InnoBanks."
#             )

#             payload = {
#                 "source_addr": source_addr,
#                 "encoding": 0,
#                 "message": sms_content,
#                 "recipients": [{"recipient_id": student.id, "dest_addr": str(student.contact)}]
#             }

#             try:
#                 response = requests.post(url, json=payload, auth=HTTPBasicAuth(api_key, secret_key), timeout=10)
#                 if response.status_code == 200:
#                     success_count += 1
#                     messages.success(request, f"Fee reminder SMS sent successfully to {student.fullName}!")
#                 else:
#                     error_messages.append(f"SMS to {student.fullName} failed: {response.text}")
#                     logger.error(f"API response for {student.fullName}: {response.text}")
#                     messages.error(request, f"Failed to send SMS to {student.fullName}. Error: {response.text}")
#             except requests.RequestException as e:
#                 error_messages.append(f"SMS to {student.fullName} failed: {str(e)}")
#                 logger.error(f"Exception for {student.fullName}: {str(e)}")
#                 messages.error(request, f"Failed to send SMS to {student.fullName}. Exception: {str(e)}")
    
#     if not students_with_remaining:
#         messages.success(request, f"No selected students with outstanding fees found in {teacherclass.ClassName}.")
#         return JsonResponse({
#             'success': True,
#             'message': f"No selected students with outstanding fees found in {teacherclass.ClassName}.",
#             'messages': [{'message': f"No selected students with outstanding fees found in {teacherclass.ClassName}.", 'tags': 'success'}]
#         })

#     # Prepare response
#     if success_count == len(students_with_remaining):
#         messages.success(request, "Fee reminder SMS sent successfully to all selected students with balances!")
#     elif success_count > 0:
#         messages.warning(request, f"Fee reminder SMS sent to {success_count} of {len(students_with_remaining)} selected students.")
#     else:
#         messages.error(request, "No fee reminder SMS were sent due to errors.")

#     # Return JSON response for AJAX
#     message_list = []
#     for message in messages.get_messages(request):
#         message_list.append({
#             'message': str(message),
#             'tags': message.tags
#         })

#     return JsonResponse({
#         'success': success_count > 0,
#         'message': f"Sent reminders to {success_count} of {len(students_with_remaining)} selected students.",
#         'messages': message_list
#     })

# @accountant_role_required
# def send_student_fee_sms(request):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

#     # Determine creator based on superuser status
#     if request.user.is_superuser:
#         creator = request.user
#     else:
#         try:
#             teacher_profile = Teacher.objects.get(user=request.user)
#             creator = teacher_profile.created_by
#         except Teacher.DoesNotExist:
#             return JsonResponse({'success': False, 'message': 'Not authorized: User has no teacher profile.'}, status=403)

#     if not creator:
#         return JsonResponse({'success': False, 'message': 'Not authorized: No creator assigned.'}, status=403)

#     try:
#         data = json.loads(request.body)
#         class_id = data.get('class_id')
#         student_ids = data.get('student_ids', '').split(',') if data.get('student_ids') else []
#         student_ids = [id.strip() for id in student_ids if id.strip()]
#         if not class_id:
#             return JsonResponse({'success': False, 'message': 'Class ID is required.'}, status=400)
#         if not student_ids:
#             return JsonResponse({'success': False, 'message': 'Please select at least one student.'}, status=400)
#     except json.JSONDecodeError:
#         return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

#     # Correctly authorize the teacher class against the creator
#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator, academicclassyear__active_year=True)
    
#     # Fetch selected students with corrected prefetch_related
#     students = Student.objects.filter(
#         Q(id__in=student_ids) & Q(teacherclass=teacherclass)
#     ).prefetch_related('assigned_fees__fee', 'payfee', 'discount_set')
    
#     if not students.exists():
#         return JsonResponse({'success': False, 'message': f"No valid students selected for {teacherclass.ClassName}."}, status=400)

#     # Fetch SMS configuration
#     try:
#         sms_config = SmsConfiguration.objects.get(user=creator)
#         url = sms_config.url_required
#         api_key = sms_config.username
#         secret_key = sms_config.pswd
#         source_addr = sms_config.source_addr
#     except SmsConfiguration.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'SMS configuration not found.'}, status=500)

#     success_count = 0
#     error_messages = []

#     for student in students:
#         if not student.contact or not str(student.contact).startswith('255') or len(str(student.contact)) != 12:
#             error_messages.append(f"Invalid contact for {student.fullName}: {student.contact}")
#             logger.warning(f"Invalid contact for {student.fullName}: {student.contact}")
#             continue

#         student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#         total_required = sum(sf.amount_required for sf in student_fees)
#         # Use prefetched discount_set for efficiency
#         discounts = student.discount_set.filter(teacherclass=teacherclass, fee__in=[sf.fee for sf in student_fees])
#         total_discount = sum(d.discount_amount for d in discounts) or Decimal('0.00')
#         adjusted_required = total_required - total_discount
#         total_paid = PayFee.objects.filter(student=student, fee__in=[sf.fee for sf in student_fees]).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
#         balance = adjusted_required - total_paid
        
#         status = "Paid" if balance <= 0 else f"Balance: {balance:.2f}"
#         if balance < 0:
#             status = f"Overpaid by {abs(balance):.2f}"

#         sms_content = (
#             f"Fee Status for {student.fullName} ({teacherclass.ClassName}):\n"
#             f"Total Required: {total_required:.2f}\n"
#             f"Total Discount: {total_discount:.2f}\n"
#             f"Adjusted Required: {adjusted_required:.2f}\n"
#             f"Total Paid: {total_paid:.2f}\n"
#             f"Status: {status}\n"
#             f"Powered By InnoBanks."
#         )

#         payload = {
#             "source_addr": source_addr,
#             "encoding": 0,
#             "message": sms_content,
#             "recipients": [{"recipient_id": student.id, "dest_addr": str(student.contact)}]
#         }

#         try:
#             response = requests.post(url, json=payload, auth=HTTPBasicAuth(api_key, secret_key), timeout=10)
#             if response.status_code == 200:
#                 success_count += 1
#                 messages.success(request, f"Fee SMS sent successfully to {student.fullName}!")
#             else:
#                 error_messages.append(f"SMS to {student.fullName} failed: {response.text}")
#                 logger.error(f"API response for {student.fullName}: {response.text}")
#                 messages.error(request, f"Failed to send SMS to {student.fullName}. Error: {response.text}")
#         except requests.RequestException as e:
#             error_messages.append(f"SMS to {student.fullName} failed: {str(e)}")
#             logger.error(f"Exception for {student.fullName}: {str(e)}")
#             messages.error(request, f"Failed to send SMS to {student.fullName}. Exception: {str(e)}")

#     # Prepare response
#     if success_count == len(students):
#         messages.success(request, "Fee SMS sent successfully to all selected students!")
#     elif success_count > 0:
#         messages.warning(request, f"Fee SMS sent to {success_count} of {len(students)} selected students.")
#     else:
#         messages.error(request, "No fee SMS were sent due to errors.")

#     # Return JSON response for AJAX
#     message_list = []
#     for message in messages.get_messages(request):
#         message_list.append({
#             'message': str(message),
#             'tags': message.tags
#         })

#     return JsonResponse({
#         'success': success_count > 0,
#         'message': f"Sent SMS to {success_count} of {len(students)} students.",
#         'messages': message_list
#     })

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Avg
from django.conf import settings
from django.core.mail import EmailMessage
import json
import requests
from requests.auth import HTTPBasicAuth
import logging
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from django.db.models import Q as models_Q
import datetime
from rps_app.models import ExaminationName,GradingModel,Subject
# Set up logging
logger = logging.getLogger(__name__)
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q, Avg
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.conf import settings


from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import json
import logging
from decimal import Decimal
import base64
from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Sum, Avg, Q
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import json
import base64
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Sum, Avg, Q
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import json
import base64
import logging
from decimal import Decimal
from rps_app.models import EmailConfiguration
logger = logging.getLogger(__name__)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Avg
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
import json
import logging
import base64
from io import BytesIO
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Avg
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
import json
import logging
import base64
from io import BytesIO
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

@accountant_role_required
def send_remaining_fee_sms(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    # Determine creator based on superuser status
    if request.user.is_superuser:
        creator = request.user
    else:
        try:
            teacher_profile = Teacher.objects.get(user=request.user)
            creator = teacher_profile.created_by
        except Teacher.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Not authorized: User has no teacher profile.'}, status=403)

    if not creator:
        return JsonResponse({'success': False, 'message': 'Not authorized: No creator assigned.'}, status=403)
    
    try:
        data = json.loads(request.body)
        class_id = data.get('class_id')
        student_ids = data.get('student_ids', '').split(',') if data.get('student_ids') else []
        student_ids = [id.strip() for id in student_ids if id.strip()]
        if not class_id:
            return JsonResponse({'success': False, 'message': 'Class ID is required.'}, status=400)
        if not student_ids:
            return JsonResponse({'success': False, 'message': 'Please select at least one student.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

    teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator, academicclassyear__active_year=True)
    
    # Fetch selected students with prefetch_related for efficiency
    students = Student.objects.filter(
        Q(id__in=student_ids) & Q(teacherclass=teacherclass)
    ).prefetch_related('assigned_fees__fee', 'payfee', 'discount_set', 'student_focus__student_fcs')

    if not students.exists():
        return JsonResponse({'success': False, 'message': f"No valid students selected for {teacherclass.ClassName}."}, status=400)

    # Fetch SMS configuration
    try:
        sms_config = SmsConfiguration.objects.get(user=creator)
        url = sms_config.url_required
        api_key = sms_config.username
        secret_key = sms_config.pswd
        source_addr = sms_config.source_addr
    except SmsConfiguration.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'SMS configuration not found.'}, status=500)
    
    success_count = 0
    error_messages = []
    students_with_remaining = []

    # Fetch initial payments
    registrations_map = {
        reg.studentfocus.student_id: reg.initial_payment or Decimal('0.00')
        for reg in StudentRegistration.objects.filter(
            studentfocus__student__in=student_ids,
            user=creator
        ).select_related('studentfocus__student')
    }

    for student in students:
        student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
        total_required = sum(sf.amount_required for sf in student_fees)
        discounts = student.discount_set.filter(teacherclass=teacherclass, fee__in=[sf.fee for sf in student_fees])
        total_discount = sum(d.discount_amount for d in discounts) or Decimal('0.00')
        adjusted_required = total_required - total_discount
        total_paid = PayFee.objects.filter(student=student, fee__in=[sf.fee for sf in student_fees]).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
        balance = adjusted_required - total_paid

        # Only process students with a positive balance
        if balance > 0:
            if not student.contact or not str(student.contact).startswith('255') or len(str(student.contact)) != 12:
                error_messages.append(f"Invalid contact for {student.fullName}: {student.contact}")
                logger.warning(f"Invalid contact for {student.fullName}: {student.contact}")
                continue
            
            students_with_remaining.append(student)
            
            # Get initial payment
            initial_payment = registrations_map.get(student.id, Decimal('0.00'))

            sms_content = (
                f"Fee Reminder for {student.fullName} (Initial Payment: {initial_payment:.2f}) ({teacherclass.ClassName}):\n"
                f"Total Required: {total_required:.2f}\n"
                f"Total Discount: {total_discount:.2f}\n"
                f"Adjusted Required: {adjusted_required:.2f}\n"
                f"Total Paid: {total_paid:.2f}\n"
                f"Outstanding Balance: {balance:.2f}\n"
                f"Please settle the balance.\n"
                f"Powered By InnoBanks."
            )

            payload = {
                "source_addr": source_addr,
                "encoding": 0,
                "message": sms_content,
                "recipients": [{"recipient_id": student.id, "dest_addr": str(student.contact)}]
            }

            try:
                response = requests.post(url, json=payload, auth=HTTPBasicAuth(api_key, secret_key), timeout=10)
                if response.status_code == 200:
                    success_count += 1
                    messages.success(request, f"Fee reminder SMS sent successfully to {student.fullName}!")
                else:
                    error_messages.append(f"SMS to {student.fullName} failed: {response.text}")
                    logger.error(f"API response for {student.fullName}: {response.text}")
                    messages.error(request, f"Failed to send SMS to {student.fullName}. Error: {response.text}")
            except requests.RequestException as e:
                error_messages.append(f"SMS to {student.fullName} failed: {str(e)}")
                logger.error(f"Exception for {student.fullName}: {str(e)}")
                messages.error(request, f"Failed to send SMS to {student.fullName}. Exception: {str(e)}")
    
    if not students_with_remaining:
        messages.success(request, f"No selected students with outstanding fees found in {teacherclass.ClassName}.")
        return JsonResponse({
            'success': True,
            'message': f"No selected students with outstanding fees found in {teacherclass.ClassName}.",
            'messages': [{'message': f"No selected students with outstanding fees found in {teacherclass.ClassName}.", 'tags': 'success'}]
        })

    # Prepare response
    if success_count == len(students_with_remaining):
        messages.success(request, "Fee reminder SMS sent successfully to all selected students with balances!")
    elif success_count > 0:
        messages.warning(request, f"Fee reminder SMS sent to {success_count} of {len(students_with_remaining)} selected students.")
    else:
        messages.error(request, "No fee reminder SMS were sent due to errors.")

    message_list = []
    for message in messages.get_messages(request):
        message_list.append({
            'message': str(message),
            'tags': message.tags
        })

    return JsonResponse({
        'success': success_count > 0,
        'message': f"Sent reminders to {success_count} of {len(students_with_remaining)} selected students.",
        'messages': message_list
    })

@accountant_role_required
def send_student_fee_sms(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    # Determine creator based on superuser status
    if request.user.is_superuser:
        creator = request.user
    else:
        try:
            teacher_profile = Teacher.objects.get(user=request.user)
            creator = teacher_profile.created_by
        except Teacher.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Not authorized: User has no teacher profile.'}, status=403)

    if not creator:
        return JsonResponse({'success': False, 'message': 'Not authorized: No creator assigned.'}, status=403)

    try:
        data = json.loads(request.body)
        class_id = data.get('class_id')
        student_ids = data.get('student_ids', '').split(',') if data.get('student_ids') else []
        student_ids = [id.strip() for id in student_ids if id.strip()]
        if not class_id:
            return JsonResponse({'success': False, 'message': 'Class ID is required.'}, status=400)
        if not student_ids:
            return JsonResponse({'success': False, 'message': 'Please select at least one student.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

    teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator, academicclassyear__active_year=True)
    
    students = Student.objects.filter(
        Q(id__in=student_ids) & Q(teacherclass=teacherclass)
    ).prefetch_related('assigned_fees__fee', 'payfee', 'discount_set', 'student_focus__student_fcs')
    
    if not students.exists():
        return JsonResponse({'success': False, 'message': f"No valid students selected for {teacherclass.ClassName}."}, status=400)

    try:
        sms_config = SmsConfiguration.objects.get(user=creator)
        url = sms_config.url_required
        api_key = sms_config.username
        secret_key = sms_config.pswd
        source_addr = sms_config.source_addr
    except SmsConfiguration.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'SMS configuration not found.'}, status=500)

    success_count = 0
    error_messages = []

    # Fetch initial payments
    registrations_map = {
        reg.studentfocus.student_id: reg.initial_payment or Decimal('0.00')
        for reg in StudentRegistration.objects.filter(
            studentfocus__student__in=student_ids,
            user=creator
        ).select_related('studentfocus__student')
    }

    for student in students:
        if not student.contact or not str(student.contact).startswith('255') or len(str(student.contact)) != 12:
            error_messages.append(f"Invalid contact for {student.fullName}: {student.contact}")
            logger.warning(f"Invalid contact for {student.fullName}: {student.contact}")
            continue

        student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
        total_required = sum(sf.amount_required for sf in student_fees)
        discounts = student.discount_set.filter(teacherclass=teacherclass, fee__in=[sf.fee for sf in student_fees])
        total_discount = sum(d.discount_amount for d in discounts) or Decimal('0.00')
        adjusted_required = total_required - total_discount
        total_paid = PayFee.objects.filter(student=student, fee__in=[sf.fee for sf in student_fees]).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
        balance = adjusted_required - total_paid
        
        # Get initial payment
        initial_payment = registrations_map.get(student.id, Decimal('0.00'))

        status = "Paid" if balance <= 0 else f"Balance: {balance:.2f}"
        if balance < 0:
            status = f"Overpaid by {abs(balance):.2f}"

        sms_content = (
            f"Fee Status for {student.fullName} (Initial Payment: {initial_payment:.2f}) ({teacherclass.ClassName}):\n"
            f"Total Required: {total_required:.2f}\n"
            f"Total Discount: {total_discount:.2f}\n"
            f"Adjusted Required: {adjusted_required:.2f}\n"
            f"Total Paid: {total_paid:.2f}\n"
            f"Status: {status}\n"
            f"Powered By InnoBanks."
        )

        payload = {
            "source_addr": source_addr,
            "encoding": 0,
            "message": sms_content,
            "recipients": [{"recipient_id": student.id, "dest_addr": str(student.contact)}]
        }

        try:
            response = requests.post(url, json=payload, auth=HTTPBasicAuth(api_key, secret_key), timeout=10)
            if response.status_code == 200:
                success_count += 1
                messages.success(request, f"Fee SMS sent successfully to {student.fullName}!")
            else:
                error_messages.append(f"SMS to {student.fullName} failed: {response.text}")
                logger.error(f"API response for {student.fullName}: {response.text}")
                messages.error(request, f"Failed to send SMS to {student.fullName}. Error: {response.text}")
        except requests.RequestException as e:
            error_messages.append(f"SMS to {student.fullName} failed: {str(e)}")
            logger.error(f"Exception for {student.fullName}: {str(e)}")
            messages.error(request, f"Failed to send SMS to {student.fullName}. Exception: {str(e)}")

    if success_count == len(students):
        messages.success(request, "Fee SMS sent successfully to all selected students!")
    elif success_count > 0:
        messages.warning(request, f"Fee SMS sent to {success_count} of {len(students)} selected students.")
    else:
        messages.error(request, "No fee SMS were sent due to errors.")

    message_list = []
    for message in messages.get_messages(request):
        message_list.append({
            'message': str(message),
            'tags': message.tags
        })

    return JsonResponse({
        'success': success_count > 0,
        'message': f"Sent SMS to {success_count} of {len(students)} students.",
        'messages': message_list
    })

@login_required
@accountant_role_required
def send_student_fee_email(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    # Determine creator based on superuser status
    if request.user.is_superuser:
        creator = request.user
    else:
        try:
            teacher_profile = Teacher.objects.get(user=request.user)
            creator = teacher_profile.created_by
        except Teacher.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Not authorized: User has no teacher profile.'}, status=403)

    if not creator:
        return JsonResponse({'success': False, 'message': 'Not authorized: No creator assigned.'}, status=403)

    try:
        data = json.loads(request.body)
        class_id = data.get('class_id')
        student_ids = data.get('student_ids', '').split(',') if data.get('student_ids') else []
        student_ids = [id.strip() for id in student_ids if id.strip()]
        custom_message = data.get('custom_message', '')
        if not class_id:
            return JsonResponse({'success': False, 'message': 'Class ID is required.', 'messages': [{'message': 'Class ID is required.', 'tags': 'error'}]}, status=400)
        if not student_ids:
            return JsonResponse({'success': False, 'message': 'Please select at least one student.', 'messages': [{'message': 'Please select at least one student.', 'tags': 'error'}]}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

    teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator)
    
    students = Student.objects.filter(
        Q(id__in=student_ids) & Q(teacherclass=teacherclass)
    ).prefetch_related('assigned_fees__fee', 'payfee', 'discount_set', 'marks__subject', 'marks__examinationname', 'student_focus__student_fcs')

    if not students.exists():
        return JsonResponse({
            'success': False,
            'message': f"No valid students selected for {teacherclass.ClassName}.",
            'messages': [{'message': f"No valid students selected for {teacherclass.ClassName}.", 'tags': 'error'}]
        }, status=400)

    try:
        email_config = EmailConfiguration.objects.get(user=creator)
    except EmailConfiguration.DoesNotExist:
        ChangeLog.objects.create(
            user=request.user,
            action='CREATE',
            model_name='Email',
            object_id=f"FeeEmail_{class_id}",
            description=f"Failed to send fee emails for class {class_id}: Email configuration not found."
        )
        return JsonResponse({
            'success': False,
            'message': 'Email configuration not found.',
            'messages': [{'message': 'Email configuration not found.', 'tags': 'error'}]
        }, status=500)

    success_count = 0
    error_messages = []

    display = DisplayModel.objects.filter(user=creator).first()

    # Fetch initial payments
    registrations_map = {
        reg.studentfocus.student_id: reg.initial_payment or Decimal('0.00')
        for reg in StudentRegistration.objects.filter(
            studentfocus__student__in=student_ids,
            user=creator
        ).select_related('studentfocus__student')
    }

    for student in students:
        if not student.user.email:
            error_messages.append(f"No email address for {student.fullName}")
            logger.warning(f"No email address for {student.fullName}")
            ChangeLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Email',
                object_id=f"FeeEmail_{student.id}_{class_id}",
                description=f"Failed to send fee email to {student.fullName}: No email address."
            )
            continue

        student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
        if not student_fees.exists():
            error_messages.append(f"No fee records for {student.fullName}")
            logger.warning(f"No fee records for {student.fullName}")
            continue

        total_required = sum(sf.amount_required for sf in student_fees)
        discounts = Discount.objects.filter(student=student, teacherclass=teacherclass, fee__in=[sf.fee for sf in student_fees])
        total_discount = sum(d.discount_amount for d in discounts) or Decimal('0.00')
        adjusted_required = total_required - total_discount
        total_paid = PayFee.objects.filter(student=student, fee__in=[sf.fee for sf in student_fees]).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
        balance = adjusted_required - total_paid
        
        status = "Paid" if balance <= 0 else f"Balance: {balance:.2f}"
        if balance < 0:
            status = f"Overpaid by {abs(balance):.2f}"

        # Get initial payment
        initial_payment = registrations_map.get(student.id, Decimal('0.00'))

        try:
            student_focus = StudentFocus.objects.get(student=student)
            focus = student_focus.focus
            registration = StudentRegistration.objects.get(studentfocus=student_focus)
            joined_date = registration.joined_date.strftime('%B %d, %Y')
        except (StudentFocus.DoesNotExist, StudentRegistration.DoesNotExist):
            focus = "Not specified"
            joined_date = "Not registered"

        icon_base64 = ''
        if display and display.image:
            try:
                with open(display.image.path, 'rb') as img_file:
                    icon_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            except Exception as e:
                logger.warning(f"Error loading DisplayModel image for {student.fullName}: {e}")

        plain_message = (
            f"Dear {student.fullName} (Initial Payment: {initial_payment:.2f}),\n\n"
            f"Subject: Fee Status Update for {teacherclass.ClassName}\n\n"
            f"We hope this message finds you well. This email provides an update on your fee status for {teacherclass.ClassName}.\n\n"
        )
        if custom_message:
            plain_message += f"{custom_message}\n\n"
        plain_message += (
            f"Fee Summary:\n"
            f"- Total Required: {total_required:.2f}\n"
            f"- Total Discount: {total_discount:.2f}\n"
            f"- Adjusted Amount: {adjusted_required:.2f}\n"
            f"- Total Paid: {total_paid:.2f}\n"
            f"- Balance: {balance:.2f}\n"
            f"- Status: {status}\n\n"
            f"Please find attached a detailed report including your financial and academic information.\n\n"
            f"For any inquiries, contact the school administration.\n\n"
            f"Best regards,\n"
            f"{request.user.username}\n"
            f"InnoBanks\n"
            f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        )

        html_message = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Fee Status Update</title>
        </head>
        <body style="margin: 0; padding: 20px; font-family: Arial, Helvetica, sans-serif; background-color: #f4f4f4; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; padding: 20px; background-color: #007bff; color: #ffffff; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                    {f'<img src="data:image/png;base64,{icon_base64}" alt="School Logo" style="max-width: 80px; height: auto; margin-bottom: 10px;" />' if icon_base64 else ''}
                    <h1 style="margin: 0; font-size: 24px;">Fee Status for {student.fullName} (Initial Payment: {initial_payment:.2f})</h1>
                </div>
                <div style="padding: 20px;">
                    <p style="font-size: 16px; margin: 0 0 10px;">Dear {student.fullName} (Initial Payment: {initial_payment:.2f}),</p>
                    {f'<p style="font-size: 16px; margin: 0 0 20px; color: #555;">{custom_message}</p>' if custom_message else ''}
                    <p style="font-size: 16px; margin: 0 0 20px;">Below is your fee status for <strong>{teacherclass.ClassName}</strong>:</p>
                    <div style="margin: 20px 0;">
                        <h2 style="color: #4a69bd; font-size: 18px; margin-bottom: 10px;">Student Information</h2>
                        <p style="font-size: 14px; margin: 5px 0;"><strong>Index Number:</strong> {student.indexNumber or '-'}</p>
                        <p style="font-size: 14px; margin: 5px 0;"><strong>Focus:</strong> {focus}</p>
                        <p style="font-size: 14px; margin: 5px 0;"><strong>Joined Date:</strong> {joined_date}</p>
                    </div>
                    <div style="margin: 20px 0;">
                        <h2 style="color: #4a69bd; font-size: 18px; margin-bottom: 10px;">Financial Information</h2>
                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; background-color: #f9f9f9; border-radius: 8px;">
                            <tr>
                                <th style="padding: 8px; text-align: left; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Fee Name</th>
                                <th style="padding: 8px; text-align: left; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Amount</th>
                                <th style="padding: 8px; text-align: left; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Discount</th>
                                <th style="padding: 8px; text-align: left; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Adjusted Amount</th>
                                <th style="padding: 8px; text-align: left; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Paid</th>
                                <th style="padding: 8px; text-align: left; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Balance</th>
                                <th style="padding: 8px; text-align: left; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Remark</th>
                                <th style="padding: 8px; text-align: left; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Status</th>
                            </tr>
        """
        financial_data = []
        for fee_assignment in student_fees:
            fee = fee_assignment.fee
            discount = discounts.filter(fee=fee).first()
            discount_amount = discount.discount_amount if discount else Decimal('0.00')
            adjusted_amount = fee_assignment.amount_required - discount_amount
            payments = PayFee.objects.filter(student=student, fee=fee, user=creator)
            paid_amount = payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
            balance = adjusted_amount - paid_amount
            status = 'Paid' if balance <= 0 else f'Pending ({balance:.2f})'
            payment_status = 'No Payment'
            if payments.exists():
                payment_dates = payments.values_list('date_paid', flat=True)
                if any(fee_assignment.start_date <= date_paid <= fee_assignment.end_date for date_paid in payment_dates):
                    payment_status = 'On Time'
                elif all(date_paid < fee_assignment.start_date for date_paid in payment_dates):
                    payment_status = 'In Advance'
                elif all(date_paid > fee_assignment.end_date for date_paid in payment_dates):
                    payment_status = 'After Deadline'
            financial_data.append({
                'fee_name': fee.fee_name,
                'amount': fee_assignment.amount_required,
                'discount': discount_amount,
                'adjusted_amount': adjusted_amount,
                'paid': paid_amount,
                'balance': balance,
                'status': status,
                'payment_timing': payment_status,
                'payments': [{
                    'date': p.date_paid.strftime('%Y-%m-%d'),
                    'amount': p.amount_paid,
                    'description': p.description or '-',
                    'payer_account_no': p.payer_account_no or '-'
                } for p in payments]
            })
            html_message += f"""
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{fee.fee_name}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{fee_assignment.amount_required:.2f}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{discount_amount:.2f}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{adjusted_amount:.2f}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{paid_amount:.2f}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; color: {'#dc3545' if balance > 0 else '#28a745'};">{balance:.2f}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{status}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{payment_status}</td>
                            </tr>
            """
        html_message += f"""
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;">Total</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;">{total_required:.2f}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;">{total_discount:.2f}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;">{adjusted_required:.2f}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;">{total_paid:.2f}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold; color: {'#dc3545' if balance > 0 else '#28a745'};">{balance:.2f}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;">{status}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;"></td>
                            </tr>
                        </table>
                        {f'<p style="font-size: 14px; color: #e74c3c; font-style: italic; margin: 10px 0;">Total Discount Applied: {total_discount:.2f}</p>' if total_discount > 0 else ''}
                    </div>
                    <div style="margin: 20px 0;">
                        <h2 style="color: #4a69bd; font-size: 18px; margin-bottom: 10px;">Academic Performance</h2>
        """
        manager = student.manager
        examination_names = ExaminationName.objects.filter(user=manager)
        grading_required = GradingModel.objects.filter(user=manager).first()
        subjects = Subject.objects.filter(teacherclass=teacherclass, user=manager)
        academic_data = []
        for exam in examination_names:
            marks = student.marks.filter(examinationname=exam, teacherclass=teacherclass)
            exam_data = {
                'exam_name': exam.exam_name,
                'subjects': [],
                'total_marks': 0,
                'average_marks': 0,
                'position': None,
                'total_students': Student.objects.filter(teacherclass=teacherclass).count()
            }
            for subject in subjects:
                mark_obj = marks.filter(subject=subject).first()
                mark_value = mark_obj.marks if mark_obj else None
                grade = '-'
                if mark_value is not None and grading_required:
                    grade_thresholds = {
                        grading_required.grade_a: 'A',
                        grading_required.grade_b: 'B',
                        grading_required.grade_c: 'C',
                        grading_required.grade_d: 'D',
                        grading_required.grade_e: 'E',
                        grading_required.grade_s: 'S',
                        grading_required.grade_f: 'F'
                    } if grading_required.is_advance else {
                        grading_required.grade_a: 'A',
                        grading_required.grade_b: 'B',
                        grading_required.grade_c: 'C',
                        grading_required.grade_d: 'D',
                        grading_required.grade_f: 'F'
                    }
                    for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
                        if mark_value >= threshold:
                            grade = letter_grade
                            break
                exam_data['subjects'].append({
                    'name': subject.nameSubject if subject else 'Unknown Subject',
                    'mark': mark_value if mark_value is not None else 'N/A',
                    'grade': grade
                })
            exam_marks = marks.aggregate(total=Sum('marks'), average=Avg('marks'))
            exam_data['total_marks'] = exam_marks['total'] or 0
            exam_data['average_marks'] = round(exam_marks['average'] or 0, 2) if exam_marks['average'] else 0
            students_ranked = Student.objects.filter(teacherclass=teacherclass).annotate(
                total_marks=Sum('marks__marks', filter=Q(marks__examinationname=exam, marks__teacherclass=teacherclass))
            ).order_by('-total_marks')
            for idx, s in enumerate(students_ranked, 1):
                if s.id == student.id:
                    exam_data['position'] = idx
                    break
            academic_data.append(exam_data)

        for exam in academic_data:
            html_message += f"""
                        <h3 style="font-size: 16px; margin: 10px 0;">{exam['exam_name']}</h3>
                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; background-color: #f9f9f9;">
                            <tr>
                                <th style="padding: 8px; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Subject</th>
                                <th style="padding: 8px; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Mark</th>
                                <th style="padding: 8px; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Grade</th>
                                <th style="padding: 8px; border: 1px solid #ddd; background-color: #4a69bd; color: #fff; font-size: 14px;">Performance (%)</th>
                            </tr>
            """
            for subject in exam['subjects']:
                html_message += f"""
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{subject['name']}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{subject['mark']}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{subject['grade']}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px;">{subject['mark'] if subject['mark'] != 'N/A' else '0'}</td>
                            </tr>
                """
            html_message += f"""
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;">Total</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;">{exam['total_marks']}</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;">-</td>
                                <td style="padding: 8px; border: 1px solid #ddd; font-size: 14px; font-weight: bold;">{exam['average_marks']:.2f}</td>
                            </tr>
                        </table>
                        <p style="font-size: 14px; margin: 10px 0;">Position: {exam['position'] or '-'}/{exam['total_students'] or '-'}</p>
            """
        html_message += f"""
                    </div>
                    <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #666;">
                        <p style="margin: 5px 0;">{custom_message if custom_message else 'Please find attached a detailed report of your academic and financial information.'}</p>
                        <p style="margin: 5px 0;">Contact the school administration for any queries.</p>
                        <p style="margin: 5px 0;">Generated by {request.user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M')} | Powered by InnoBanks</p>
                    </div>
                </div>
            </body>
            </html>
        """

        # Generate PDF report
        accountants = Teacher.objects.filter(created_by=manager).values_list('user', flat=True)
        all_payments = PayFee.objects.filter(student=student, user__in=accountants).select_related('fee').order_by('-date_paid')
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
        elements = []

        styles = getSampleStyleSheet()
        header_style = ParagraphStyle(name='Header', parent=styles['Heading1'], fontSize=16, alignment=1, spaceAfter=10, textColor=colors.darkblue, leading=20)
        subheader_style = ParagraphStyle(name='Subheader', parent=styles['Heading2'], fontSize=12, alignment=1, spaceAfter=8, textColor=colors.black)
        body_style = ParagraphStyle(name='Body', parent=styles['BodyText'], fontSize=9, alignment=0, spaceAfter=6, leading=10)
        footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=1, textColor=colors.grey)
        discount_style = ParagraphStyle(name='Discount', parent=styles['BodyText'], fontSize=10, textColor=colors.red, spaceAfter=6)

        elements.append(Paragraph(f"Student Report for {student.fullName} (Initial Payment: {initial_payment:.2f})", header_style))
        if display and display.image:
            try:
                icon = Image(display.image.path, width=2*cm, height=2*cm)
                icon.hAlign = 'CENTER'
                elements.append(icon)
                elements.append(Spacer(1, 0.5*cm))
            except Exception as e:
                logger.warning(f"Error loading DisplayModel image for {student.fullName}: {e}")
        elements.append(Paragraph(
            f"<b>Index:</b> {student.indexNumber} | <b>Class:</b> {teacherclass.ClassName} | <b>Grading:</b> {'Advanced' if grading_required and grading_required.is_advance else 'Ordinary'}",
            subheader_style
        ))
        elements.append(Paragraph(
            f"Generated by: {request.user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            footer_style
        ))
        elements.append(Spacer(1, 1*cm))

        elements.append(Paragraph("Academic Performance", subheader_style))
        if not academic_data:
            elements.append(Paragraph("No examination data available.", body_style))
        else:
            for exam in academic_data:
                elements.append(Paragraph(f"Examination: {exam['exam_name']}", subheader_style))
                page_width = A4[0] - 2 * 1.5*cm
                col_widths = [0.35 * page_width, 0.15 * page_width, 0.15 * page_width, 0.35 * page_width]
                table_data = [['Subject', 'Marks', 'Grade', 'Performance (%)']]
                for subject in exam['subjects']:
                    table_data.append([
                        Paragraph(subject['name'], body_style),
                        Paragraph(str(subject['mark']), body_style),
                        Paragraph(subject['grade'], body_style),
                        Paragraph(str(subject['mark']) if subject['mark'] != 'N/A' else '0', body_style)
                    ])
                if not exam['subjects']:
                    table_data.append(['No subjects available', '-', '-', '-'])
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
                ]))
                elements.append(table)
                summary = f"Total Marks: {exam['total_marks']} | Average: {exam['average_marks']:.2f}% | Position: {exam['position'] or '-'}/{exam['total_students'] or '-'}"
                elements.append(Spacer(1, 0.5*cm))
                elements.append(Paragraph(summary, body_style))
                elements.append(Spacer(1, 1*cm))

        elements.append(Paragraph("Financial Information", subheader_style))
        if not financial_data:
            elements.append(Paragraph("No financial data available.", body_style))
        else:
            page_width = A4[0] - 2 * 1.5*cm
            col_widths = [0.20 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width]
            table_data = [['Fee', 'Orig. Amt.', 'Discount', 'Adj. Amt.', 'Paid', 'Balance', 'Status', 'Payment Timing']]
            for fee in financial_data:
                table_data.append([
                    Paragraph(fee['fee_name'], body_style),
                    Paragraph(f"{fee['amount']:.2f}", body_style),
                    Paragraph(f"{fee['discount']:.2f}", body_style),
                    Paragraph(f"{fee['adjusted_amount']:.2f}", body_style),
                    Paragraph(f"{fee['paid']:.2f}", body_style),
                    Paragraph(f"{fee['balance']:.2f}", body_style),
                    Paragraph(fee['status'], body_style),
                    Paragraph(fee['payment_timing'], body_style)
                ])
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
            ]))
            elements.append(table)
            summary = f"Total Required: {total_required:.2f} | Total Paid: {total_paid:.2f} | Total Balance: {balance:.2f} | Total Discount: {total_discount:.2f}"
            elements.append(Spacer(1, 0.5*cm))
            elements.append(Paragraph(summary, discount_style if total_discount > 0 else body_style))

            elements.append(Spacer(1, 1*cm))
            elements.append(Paragraph("Payment Records", subheader_style))
            col_widths = [0.20 * page_width, 0.15 * page_width, 0.15 * page_width, 0.25 * page_width, 0.25 * page_width]
            table_data = [['Fee', 'Date', 'Amount', 'Payer Account', 'Description']]
            for fee in financial_data:
                for payment in fee['payments']:
                    table_data.append([
                        Paragraph(fee['fee_name'], body_style),
                        Paragraph(payment['date'], body_style),
                        Paragraph(f"{payment['amount']:.2f}", body_style),
                        Paragraph(payment['payer_account_no'], body_style),
                        Paragraph(payment['description'], body_style)
                    ])
            if not any(fee['payments'] for fee in financial_data):
                table_data.append(['No payment records found', '-', '-', '-', '-'])
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
            ]))
            elements.append(table)

        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()

        subject = f"Fee Status for {student.fullName} (Initial Payment: {initial_payment:.2f}) ({teacherclass.ClassName})"
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=email_config.default_from_email,
            to=[student.user.email],
        )
        email.content_subtype = 'html'
        email.attach(f"student_report_{student.indexNumber}.pdf".replace(" ", "_"), pdf_content, 'application/pdf')

        original_settings = {
            'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', None),
            'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', None),
            'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', None),
            'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', None),
            'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', None),
            'EMAIL_HOST_PASSWORD': getattr(settings, 'EMAIL_HOST_PASSWORD', None),
            'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        }
        settings.EMAIL_BACKEND = email_config.email_backend
        settings.EMAIL_HOST = email_config.email_host
        settings.EMAIL_PORT = email_config.email_port
        settings.EMAIL_USE_TLS = email_config.email_use_tls
        settings.EMAIL_HOST_USER = email_config.email_host_user
        settings.EMAIL_HOST_PASSWORD = email_config.email_host_password
        settings.DEFAULT_FROM_EMAIL = email_config.default_from_email

        try:
            email.send(fail_silently=False)
            success_count += 1
            messages.success(request, f"Fee email with report sent successfully to {student.fullName}!")
            ChangeLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Email',
                object_id=f"FeeEmail_{student.id}_{class_id}",
                description=f"Sent fee status email with report to {student.fullName} for class {class_id}"
            )
        except Exception as e:
            error_messages.append(f"Email to {student.fullName} failed: {str(e)}")
            logger.error(f"Exception for {student.fullName}: {str(e)}")
            messages.error(request, f"Failed to send email to {student.fullName}. Exception: {str(e)}")
            ChangeLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Email',
                object_id=f"FeeEmail_{student.id}_{class_id}",
                description=f"Failed to send fee email to {student.fullName}: {str(e)}"
            )

        for key, value in original_settings.items():
            if value is not None:
                setattr(settings, key, value)
            else:
                delattr(settings, key) if hasattr(settings, key) else None

    if success_count == len(students):
        messages.success(request, "Fee emails with reports sent successfully to all selected students!")
        ChangeLog.objects.create(
            user=request.user,
            action='CREATE',
            model_name='Email',
            object_id=f"FeeEmail_{class_id}",
            description=f"Sent fee status emails with reports to {success_count} students for class {class_id}"
        )
    elif success_count > 0:
        messages.warning(request, f"Fee emails with reports sent to {success_count} of {len(students)} selected students.")
        ChangeLog.objects.create(
            user=request.user,
            action='CREATE',
            model_name='Email',
            object_id=f"FeeEmail_{class_id}",
            description=f"Sent fee status emails with reports to {success_count} of {len(students)} students for class {class_id}"
        )
    else:
        messages.error(request, "No fee emails were sent due to errors.")
        ChangeLog.objects.create(
            user=request.user,
            action='CREATE',
            model_name='Email',
            object_id=f"FeeEmail_{class_id}",
            description=f"Failed to send fee emails for class {class_id}: {', '.join(error_messages) if error_messages else 'No valid emails or fee records.'}"
        )

    message_list = []
    for message in messages.get_messages(request):
        message_list.append({
            'message': str(message),
            'tags': message.tags
        })

    return JsonResponse({
        'success': success_count > 0,
        'message': f"Sent emails with reports to {success_count} of {len(students)} students.",
        'messages': message_list
    })
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import logging
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
import logging
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
import logging
from django.contrib.auth.decorators import login_required
from .models import Discount, Fee, StudentFee,  ChangeLog
from rps_app.models import Student, Teacher
from django.shortcuts import redirect, reverse, get_object_or_404
from django.contrib import messages

from .decorators import accountant_role_required
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# @accountant_role_required
# def apply_discount(request, student_id, fee_id, class_id):
#     if request.method == 'POST':
#         user = request.user
#         creator = getattr(request, 'creator', user)
#         discount_amount = request.POST.get('discount_amount')
#         try:
#             discount_amount = Decimal(discount_amount)
#             if discount_amount < 0:
#                 raise ValueError("Discount amount cannot be negative.")

#             # Verify StudentFee exists to ensure the student is associated with the fee and class
#             student_fee = get_object_or_404(
#                 StudentFee,
#                 student_id=student_id,
#                 fee_id=fee_id,
#                 teacherclass_id=class_id,
#                 user=creator
#             )
#             student = student_fee.student
#             fee = student_fee.fee
#             teacherclass = student_fee.teacherclass

#             # Verify Fee and TeacherClass for consistency
#             fee = get_object_or_404(Fee, id=fee_id, teacherclass_id=class_id, user=creator)
#             teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator)

#             discount, created = Discount.objects.get_or_create(
#                 student=student,
#                 fee=fee,
#                 teacherclass=teacherclass,
#                 user=creator,
#                 defaults={'discount_amount': discount_amount}
#             )
#             if not created:
#                 discount.discount_amount = discount_amount
#                 discount.save()

#             ChangeLog.objects.create(
#                 user=user,
#                 action='CREATE' if created else 'UPDATE',
#                 model_name='Discount',
#                 object_id=discount.id,
#                 description=f"{'Created' if created else 'Updated'} discount of {discount_amount} for student {student.fullName} on fee {fee.fee_name}"
#             )
#             messages.success(request, f"Discount of {discount_amount} {'applied' if created else 'updated'} successfully.")
#             logger.debug(f"Discount {'applied' if created else 'updated'}: {discount_amount} for student {student.fullName} on fee {fee.fee_name}")
#         except ValueError as e:
#             messages.error(request, f"Invalid discount amount: {str(e)}")
#             logger.error(f"Invalid discount amount: {str(e)}")
#         except Exception as e:
#             messages.error(request, f"Error applying discount: {str(e)}")
#             logger.error(f"Error applying discount: {str(e)}")

#         # Preserve all query parameters
#         query_params = request.GET.copy()
#         query_params.update({'class_id': class_id, 'fee_id': fee_id})
#         redirect_url = f"{reverse('finance:fee_management')}?{query_params.urlencode()}"
#         return redirect(redirect_url)
#     return redirect('finance:fee_management')


# @accountant_role_required
# def update_discount(request):
#     if request.method == 'POST':
#         user = request.user

#         # Check if request.creator is set (for logging consistency)
#         if not hasattr(request, 'creator') or not request.creator:
#             logger.warning(f"Creator not set for user {user.username} in update_discount, defaulting to user")
#             creator = request.user
#         else:
#             creator = request.creator
#             logger.debug(f"Updating discount for user {user.username}, creator {creator.username}")

#         student_id = request.POST.get('student_id')
#         fee_id = request.POST.get('fee_id')
#         class_id = request.POST.get('class_id')
#         discount_amount = request.POST.get('discount_amount')

#         if not all([student_id, fee_id, class_id, discount_amount]):
#             error_message = 'Missing required parameters.'
#             logger.error(f"Missing parameters: student_id={student_id}, fee_id={fee_id}, class_id={class_id}, discount_amount={discount_amount} for user {user.username}")
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({'success': False, 'message': error_message}, status=400)
#             messages.error(request, error_message)
#             return redirect('finance:fee_management')

#         try:
#             # Fetch Student (no manager restriction)
#             student = get_object_or_404(Student, id=student_id)
#             # Fetch Fee, ensuring it is associated with the given class
#             fee = get_object_or_404(Fee, id=fee_id, teacherclasses__id=class_id)
#             # Fetch TeacherClass, ensuring active academic year
#             teacherclass = get_object_or_404(
#                 TeacherClass,
#                 id=class_id,
#                 academicclassyear__active_year=True
#             )
#             discount_amount = Decimal(discount_amount)

#             if discount_amount <= 0:
#                 error_message = 'Discount amount must be positive.'
#                 logger.error(f"Invalid discount_amount {discount_amount} for student {student_id}, fee {fee_id}, class {class_id}, user {user.username}")
#                 if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                     return JsonResponse({'success': False, 'message': error_message}, status=400)
#                 messages.error(request, error_message)
#                 return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

#             if discount_amount > fee.amount:
#                 error_message = f'Discount cannot exceed fee amount ({fee.amount}).'
#                 logger.error(f"Discount {discount_amount} exceeds fee amount {fee.amount} for student {student_id}, fee {fee_id}, user {user.username}")
#                 if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                     return JsonResponse({'success': False, 'message': error_message}, status=400)
#                 messages.error(request, error_message)
#                 return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

#             # Find existing discount (no user restriction)
#             discount = Discount.objects.filter(
#                 student=student,
#                 fee=fee,
#                 teacherclass=teacherclass
#             ).first()

#             if not discount:
#                 error_message = 'No discount found to update.'
#                 logger.error(f"No discount found for student {student_id}, fee {fee_id}, class {class_id}, user {user.username}")
#                 if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                     return JsonResponse({'success': False, 'message': error_message}, status=404)
#                 messages.error(request, error_message)
#                 return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

#             with transaction.atomic():
#                 discount.discount_amount = discount_amount
#                 discount.save()

#                 ChangeLog.objects.create(
#                     user=user,
#                     action='UPDATE',
#                     model_name='Discount',
#                     object_id=str(discount.id),
#                     description=f"Updated discount to {discount_amount} for student {student.fullName} on fee {fee.fee_name} in class {teacherclass.ClassName.class_name} by user {user.username}"
#                 )

#             success_message = f'Discount updated to {discount_amount} for {student.fullName} in {teacherclass.ClassName.class_name}.'
#             logger.debug(f"Discount updated to {discount_amount} for student {student.fullName}, fee {fee.fee_name}, class {teacherclass.ClassName.class_name} by user {user.username}")
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({'success': True, 'message': success_message})
#             messages.success(request, success_message)
#             return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

#         except (ValueError, TypeError) as e:
#             error_message = 'Invalid input data.'
#             logger.error(f"Invalid input: {str(e)} for student {student_id}, fee {fee_id}, class {class_id}, user {user.username}")
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({'success': False, 'message': error_message}, status=400)
#             messages.error(request, error_message)
#             return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')
#         except Exception as e:
#             error_message = str(e)
#             logger.error(f"Error updating discount: {str(e)} for user {user.username}", exc_info=True)
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({'success': False, 'message': error_message}, status=400)
#             messages.error(request, error_message)
#             return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

#     error_message = 'Invalid request method.'
#     logger.debug(f"Invalid request method for update_discount by user {request.user.username}")
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return JsonResponse({'success': False, 'message': error_message}, status=405)
#     messages.error(request, error_message)
#     return redirect('finance:fee_management')

@accountant_role_required
def delete_discount(request, discount_id):
    if request.method == 'POST':
        user = request.user

        # Check if request.creator is set (for logging consistency)
        if not hasattr(request, 'creator') or not request.creator:
            logger.warning(f"Creator not set for user {user.username} in delete_discount, defaulting to user")
            creator = request.user
        else:
            creator = request.creator
            logger.debug(f"Deleting discount for user {user.username}, creator {creator.username}")

        class_id = request.POST.get('class_id')
        fee_id = request.POST.get('fee_id')

        if not all([class_id, fee_id]):
            error_message = 'Missing required parameters.'
            logger.error(f"Missing parameters: class_id={class_id}, fee_id={fee_id} for user {user.username}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message}, status=400)
            messages.error(request, error_message)
            return redirect('finance:fee_management')

        try:
            # Fetch Discount
            discount = get_object_or_404(Discount, id=discount_id)
            student = discount.student
            fee = discount.fee
            teacherclass = discount.teacherclass

            # Verify related objects (no creator restrictions)
            get_object_or_404(Student, id=student.id)
            get_object_or_404(Fee, id=fee_id, teacherclasses__id=class_id)
            get_object_or_404(TeacherClass, id=class_id, academicclassyear__active_year=True)

            with transaction.atomic():
                ChangeLog.objects.create(
                    user=user,
                    action='DELETE',
                    model_name='Discount',
                    object_id=str(discount.id),
                    description=f"Deleted discount of {discount.discount_amount} for student {student.fullName} on fee {fee.fee_name} in class {teacherclass.ClassName.class_name} by user {user.username}"
                )
                discount.delete()

            success_message = f'Discount deleted for {student.fullName} in {teacherclass.ClassName.class_name}.'
            logger.debug(f"Discount deleted for student {student.fullName}, fee {fee.fee_name}, class {teacherclass.ClassName.class_name} by user {user.username}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': success_message})
            messages.success(request, success_message)
            return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

        except (Discount.DoesNotExist, Student.DoesNotExist, Fee.DoesNotExist, TeacherClass.DoesNotExist) as e:
            error_message = 'Discount or related objects not found.'
            logger.error(f"Error deleting discount {discount_id}: {str(e)} for user {user.username}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message}, status=404)
            messages.error(request, error_message)
            return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error deleting discount: {str(e)} for user {user.username}", exc_info=True)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message}, status=400)
            messages.error(request, error_message)
            return redirect(f'/finance/fee-management/?class_id={class_id}&fee_id={fee_id}')

    error_message = 'Invalid request method.'
    logger.debug(f"Invalid request method for delete_discount by user {request.user.username}")
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': error_message}, status=405)
    messages.error(request, error_message)
    return redirect('finance:fee_management')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from rps_app.models import Student, TeacherClass
from finance.models import StudentFocus, ChangeLog
from finance.forms import StudentFocusAssignmentForm
from finance.decorators import accountant_role_required  # Ensure decorator is imported
import logging

logger = logging.getLogger(__name__)



@accountant_role_required
def assign_student_focus(request, class_id=0):
    creator = getattr(request, 'creator', request.user)
    teacher_classes = TeacherClass.objects.filter(user=creator, academicclassyear__active_year=True).order_by('ClassName')
    
    if request.method == 'POST':
        form = StudentFocusAssignmentForm(request.POST, creator=creator, class_id=class_id)
        if form.is_valid():
            focus = form.cleaned_data['focus']
            students = form.cleaned_data['student']
            class_id = form.cleaned_data.get('class_id', class_id)
            
            for student in students:
                student_focus, created = StudentFocus.objects.get_or_create(
                    student=student,
                    user=creator,
                    defaults={'focus': focus}
                )
                if not created and student_focus.focus != focus:
                    student_focus.focus = focus
                    student_focus.save()
                
                ChangeLog.objects.create(
                    user=request.user,
                    action='CREATE' if created else 'UPDATE',
                    model_name='StudentFocus',
                    object_id=f"{student.id}-{focus}",
                    description=f"{'Assigned' if created else 'Updated'} focus {focus} for student {student.fullName}"
                )
                logger.debug(f"{'Assigned' if created else 'Updated'} focus {focus} for student {student.fullName} by user {request.user.username}")
            
            messages.success(request, f"Focus {focus} successfully assigned to {len(students)} student(s).")
            return HttpResponseRedirect(reverse('finance:assign_student_focus_with_class', kwargs={'class_id': class_id}))
        else:
            messages.error(request, "Error assigning focus. Please check the form.")
    else:
        form = StudentFocusAssignmentForm(creator=creator, class_id=class_id)
    
    all_students_data = []
    if class_id:
        try:
            # Query students in the given class who have a StudentFocus entry
            students = Student.objects.filter(
                manager=creator,
                teacherclass__id=class_id,
                academicclassyear__active_year=True
            ).distinct()
            for student in students:
                student_focus = StudentFocus.objects.filter(student=student, user=creator).first()
                joined_date = student.student_fcs.filter(teacher_class_id=class_id).first().joined_date if hasattr(student, 'student_fcs') and student.student_fcs.filter(teacher_class_id=class_id).exists() else None
                all_students_data.append({
                    'student_id': student.id,
                    'student_name': student.fullName,
                    'focus': student_focus.focus if student_focus else 'Not assigned',
                    'joined_date': joined_date
                })
        except Exception as e:
            logger.error(f"Error querying student focus data: {str(e)}")
            messages.error(request, "Error loading student focus data. Please try again.")
    
    context = {
        'form': form,
        'teacher_classes': teacher_classes,
        'class_id': class_id,
        'all_students_data': all_students_data,
    }
    return render(request, 'accountant/assign_student_focus.html', context)

@accountant_role_required
def get_student_focus_for_class(request, class_id):
    creator = getattr(request, 'creator', request.user)  # Fallback to request.user
    try:
        teacherclass = TeacherClass.objects.filter(id=class_id, user=creator).first()
        if not teacherclass:
            logger.error(f"TeacherClass with id {class_id} not found for creator {creator.username}")
            return JsonResponse({'success': False, 'error': 'Class not found'}, status=404)

        # Fetch students and their focuses
        students = Student.objects.filter(teacherclass=teacherclass, manager=creator).select_related('teacherclass')
        student_focus_data = []
        for student in students:
            focus = StudentFocus.objects.filter(student=student).first()
            student_focus_data.append({
                'student_id': student.id,
                'student_name': student.fullName or 'Unnamed Student',
                'class_name': teacherclass.ClassName.class_name if teacherclass.ClassName else 'Unnamed Class',  # Serialize class_name
                'focus': focus.focus if focus else 'Not assigned'
            })

        logger.debug(f"Fetched {len(students)} students for class_id={class_id}")
        return JsonResponse({'success': True, 'student_focus_data': student_focus_data})
    except Exception as e:
        logger.error(f"Error fetching student focuses for class_id={class_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import accountant_role_required
from .models import StudentFocus, ChangeLog
import logging

logger = logging.getLogger(__name__)

@accountant_role_required
def delete_student_focus(request, student_id):
    if request.method == 'POST':
        creator = getattr(request, 'creator', request.user)
        try:
            student_focus = get_object_or_404(StudentFocus, student_id=student_id, user=creator)
            focus_name = student_focus.focus
            student_name = student_focus.student.fullName
            student_focus.delete()
            
            ChangeLog.objects.create(
                user=request.user,
                action='DELETE',
                model_name='StudentFocus',
                object_id=f"{student_id}-{focus_name}",
                description=f"Deleted focus {focus_name} for student {student_name}"
            )
            logger.debug(f"Deleted focus {focus_name} for student {student_name} by user {request.user.username}")
            return JsonResponse({'success': True, 'message': f"Focus {focus_name} deleted successfully for {student_name}."})
        except Exception as e:
            logger.error(f"Error deleting focus for student_id={student_id}: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .decorators import accountant_role_required
from .models import StudentFocus, ChangeLog
import logging

logger = logging.getLogger(__name__)

@accountant_role_required
def update_student_focus(request, student_id):
    if request.method == 'POST':
        creator = getattr(request, 'creator', request.user)
        try:
            student_focus = get_object_or_404(StudentFocus, student_id=student_id, user=creator)
            new_focus = request.POST.get('focus')
            class_id = request.POST.get('class_id', 0)  # Get class_id from form to redirect back
            if not new_focus or new_focus not in dict(StudentFocus.FIELD_CHOICES).keys():
                messages.error(request, 'Invalid focus selected.')
                return HttpResponseRedirect(reverse('finance:assign_student_focus_with_class', kwargs={'class_id': class_id}))
            
            old_focus = student_focus.focus
            student_name = student_focus.student.fullName
            student_focus.focus = new_focus
            student_focus.save()
            
            ChangeLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='StudentFocus',
                object_id=f"{student_id}-{new_focus}",
                description=f"Updated focus from {old_focus} to {new_focus} for student {student_name}"
            )
            logger.debug(f"Updated focus from {old_focus} to {new_focus} for student {student_name} by user {request.user.username}")
            messages.success(request, f"Focus updated to {new_focus} for {student_name}.")
            return HttpResponseRedirect(reverse('finance:assign_student_focus_with_class', kwargs={'class_id': class_id}))
        except Exception as e:
            logger.error(f"Error updating focus for student_id={student_id}: {str(e)}")
            messages.error(request, f"Error updating focus: {str(e)}")
            return HttpResponseRedirect(reverse('finance:assign_student_focus_with_class', kwargs={'class_id': class_id}))
    return HttpResponseRedirect(reverse('finance:assign_student_focus_with_class', kwargs={'class_id': 0}))


from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from rps_app.models import Student, TeacherClass
from finance.models import StudentFocus, StudentRegistration, ChangeLog
from finance.forms import StudentRegistrationForm
from finance.decorators import accountant_role_required
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from rps_app.models import Student, TeacherClass
from finance.models import StudentFocus, StudentRegistration, ChangeLog
from finance.forms import StudentRegistrationForm
from finance.decorators import accountant_role_required
import logging

logger = logging.getLogger(__name__)

@accountant_role_required
def assign_student_registration(request, class_id=None):
    creator = getattr(request, 'creator', request.user)
    teacher_classes = TeacherClass.objects.filter(
        user=creator, 
        academicclassyear__active_year=True
    )
    form = StudentRegistrationForm(creator=creator, class_id=class_id)
    registration_data = []

    if class_id:
        try:
            teacherclass = TeacherClass.objects.get(
                id=class_id, 
                user=creator, 
                academicclassyear__active_year=True
            )
            registrations = StudentRegistration.objects.filter(
                studentfocus__student__teacherclass=teacherclass,
                studentfocus__student__manager=creator
            ).select_related('studentfocus__student__user')
            for registration in registrations:
                sf = registration.studentfocus
                student_name = sf.student.fullName or sf.student.user.username or 'Unnamed Student'
                focus_display = sf.focus or 'Unknown Focus'
                registration_data.append({
                    'student_name': f"{student_name} ({focus_display})",
                    'joined_date': registration.joined_date.strftime('%B %d, %Y'),
                    'initial_payment': registration.initial_payment if registration.initial_payment is not None else 'N/A',
                    'class_name': teacherclass.ClassName.class_name or 'Unnamed Class',
                    'registration_id': registration.id
                })
        except TeacherClass.DoesNotExist:
            messages.warning(request, "Selected class does not exist or is not active.")
            registration_data = []
        except Exception as e:
            logger.error(f"Error fetching registration data for class_id={class_id}: {str(e)}")
            messages.error(request, "Error loading student data. Please try again.")

    if request.method == 'POST':
        form = StudentRegistrationForm(
            request.POST,
            creator=creator,
            class_id=class_id
        )
        if form.is_valid():
            for studentfocus in form.cleaned_data['studentfocus']:
                initial_payment = form.cleaned_data.get('initial_payment')
                registration = StudentRegistration.objects.create(
                    user=creator,
                    studentfocus=studentfocus,
                    joined_date=form.cleaned_data['joined_date'],
                    initial_payment=initial_payment
                )
                ChangeLog.objects.create(
                    user=creator,
                    action='CREATE',
                    model_name='StudentRegistration',
                    object_id=str(registration.id),
                    description=f"Created registration for {studentfocus.student.fullName} in class {teacherclass.ClassName.class_name} with initial payment {initial_payment or 'None'}"
                )
            messages.success(request, 'Student registrations assigned successfully.')
            logger.info(f"User {creator.username} assigned registrations for class_id={class_id}")
            return redirect('finance:assign_student_registration_with_class', class_id=class_id)
        else:
            messages.error(request, 'Please correct the errors below.')
            logger.error(f"Form errors for class_id={class_id}: {form.errors}")
    elif request.GET.get('class_id'):
        new_class_id = request.GET.get('class_id')
        if new_class_id:
            return redirect('finance:assign_student_registration_with_class', class_id=new_class_id)
    
    return render(request, 'accountant/assign_student_registration.html', {
        'form': form,
        'teacher_classes': teacher_classes,
        'class_id': class_id,
        'registration_data': registration_data
    })

@accountant_role_required
def update_student_registration(request, registration_id):
    creator = getattr(request, 'creator', request.user)
    try:
        registration = StudentRegistration.objects.get(id=registration_id, user=creator)
    except StudentRegistration.DoesNotExist:
        messages.error(request, "Registration not found or you do not have permission to update it.")
        logger.warning(f"User {creator.username} attempted to update non-existent registration ID {registration_id}")
        return redirect('finance:assign_student_registration')

    if request.method == 'POST':
        joined_date = request.POST.get('joined_date')
        initial_payment = request.POST.get('initial_payment')
        try:
            if joined_date:
                registration.joined_date = joined_date
            if initial_payment:
                registration.initial_payment = float(initial_payment) if initial_payment else None
            registration.save()
            ChangeLog.objects.create(
                user=creator,
                action='UPDATE',
                model_name='StudentRegistration',
                object_id=str(registration.id),
                description=f"Updated registration for {registration.studentfocus.student.fullName} (Joined Date: {joined_date}, Initial Payment: {initial_payment or 'None'})"
            )
            messages.success(request, "Registration updated successfully.")
            logger.info(f"User {creator.username} updated registration ID {registration_id}")
        except Exception as e:
            messages.error(request, "Error updating registration. Please try again.")
            logger.error(f"Error updating registration ID {registration_id} by user {creator.username}: {str(e)}")
        return redirect('finance:assign_student_registration_with_class', class_id=registration.studentfocus.student.teacherclass.id)
    
    return redirect('finance:assign_student_registration')

@accountant_role_required
def delete_student_registration(request, registration_id):
    creator = getattr(request, 'creator', request.user)
    try:
        registration = StudentRegistration.objects.get(id=registration_id, user=creator)
    except StudentRegistration.DoesNotExist:
        messages.error(request, "Registration not found or you do not have permission to delete it.")
        logger.warning(f"User {creator.username} attempted to delete non-existent registration ID {registration_id}")
        return redirect('finance:assign_student_registration')

    if request.method == 'POST':
        class_id = registration.studentfocus.student.teacherclass.id
        try:
            ChangeLog.objects.create(
                user=creator,
                action='DELETE',
                model_name='StudentRegistration',
                object_id=str(registration.id),
                description=f"Deleted registration for {registration.studentfocus.student.fullName}"
            )
            registration.delete()
            messages.success(request, "Registration deleted successfully.")
            logger.info(f"User {creator.username} deleted registration ID {registration_id}")
        except Exception as e:
            messages.error(request, "Error deleting registration. Please try again.")
            logger.error(f"Error deleting registration ID {registration_id} by user {creator.username}: {str(e)}")
        return redirect('finance:assign_student_registration_with_class', class_id=class_id)
    
    return redirect('finance:assign_student_registration')

# @accountant_role_required
# def delete_student_registration(request, registration_id):
#     creator = getattr(request, 'creator', request.user)
#     try:
#         registration = StudentRegistration.objects.get(id=registration_id, user=creator)
#     except StudentRegistration.DoesNotExist:
#         messages.error(request, "Registration not found or you do not have permission to delete it.")
#         logger.warning(f"User {creator.username} attempted to delete non-existent registration ID {registration_id}")
#         return redirect('finance:assign_student_registration')

#     if request.method == 'POST':
#         class_id = registration.studentfocus.student.teacherclass.id
#         try:
#             ChangeLog.objects.create(
#                 user=creator,
#                 action='DELETE',
#                 model_name='StudentRegistration',
#                 object_id=str(registration.id),
#                 description=f"Deleted registration for {registration.studentfocus.student.fullName}"
#             )
#             registration.delete()
#             messages.success(request, "Registration deleted successfully.")
#             logger.info(f"User {creator.username} deleted registration ID {registration_id}")
#         except Exception as e:
#             messages.error(request, "Error deleting registration. Please try again.")
#             logger.error(f"Error deleting registration ID {registration_id} by user {creator.username}: {str(e)}")
#         return redirect('finance:assign_student_registration_with_class', class_id=class_id)
    
#     return redirect('finance:assign_student_registration')

# @login_required
# def get_student_registration_for_class(request, class_id):
#     creator = getattr(request, 'creator', request.user)
#     try:
#         teacherclass = TeacherClass.objects.filter(
#             id=class_id, 
#             user=creator, 
#             academicclassyear__active_year=True
#         ).first()
#         if not teacherclass:
#             logger.error(f"TeacherClass with id {class_id} not found for creator {creator.username}")
#             return JsonResponse({'success': False, 'error': 'Class not found'}, status=404)

#         student_focuses = StudentFocus.objects.filter(
#             student__teacherclass=teacherclass,
#             student__manager=creator
#         ).select_related('student__user')
#         student_registration_data = []
#         for sf in student_focuses:
#             registration = StudentRegistration.objects.filter(studentfocus=sf).first()
#             # Use fullName or fallback to username
#             student_name = sf.student.fullName or sf.student.user.username or 'Unnamed Student'
#             # Handle focus field
#             focus_display = sf.focus or 'Unknown Focus'
#             student_registration_data.append({
#                 'student_id': sf.id,  # Use StudentFocus ID
#                 'student_name': f"{student_name} ({focus_display})",
#                 'class_name': teacherclass.ClassName.class_name or 'Unnamed Class',
#                 'joined_date': registration.joined_date.strftime('%B %d, %Y') if registration else 'Not assigned'
#             })

#         logger.debug(f"Fetched {len(student_focuses)} student focuses for class_id={class_id}")
#         return JsonResponse({'success': True, 'student_registration_data': student_registration_data})
#     except Exception as e:
#         logger.error(f"Error fetching student registrations for class_id={class_id}: {str(e)}")
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import StudentFee
from .forms import StudentFeeUpdateForm
from rps_app.models import Student, TeacherClass
from .decorators import accountant_role_required
import logging

logger = logging.getLogger(__name__)
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import StudentFee
from .forms import StudentFeeUpdateForm
from rps_app.models import Student, TeacherClass
from .decorators import accountant_role_required
from .models import ChangeLog
import logging

logger = logging.getLogger(__name__)


@accountant_role_required
def delete_student_fee_specific(request, student_id, fee_id):
    """Delete a specific StudentFee assignment."""
    user = request.user
    creator = getattr(request, 'creator', request.user)
    
    # Retrieve the StudentFee object
    student_fee = get_object_or_404(
        StudentFee,
        id=fee_id,
        student_id=student_id,
        teacherclass__user=creator
    )
    
    class_id = student_fee.teacherclass.id
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                student_name = student_fee.student.fullName or student_fee.student.user.username
                fee_name = student_fee.fee.fee_name
                class_name = student_fee.teacherclass.ClassName.class_name if student_fee.teacherclass.ClassName else 'Unnamed Class'
                
                # Delete the StudentFee object
                student_fee.delete()
                
                # Create ChangeLog entry
                ChangeLog.objects.create(
                    user=user,
                    action='DELETE',
                    model_name='StudentFee',
                    object_id=str(fee_id),
                    description=f"Deleted fee '{fee_name}' for student '{student_name}' in class '{class_name}'"
                )
                
                logger.info(f"User {user.username} deleted fee '{fee_name}' for student '{student_name}' in class '{class_name}'")
                
                # Return JSON response for AJAX
                return JsonResponse({
                    'success': True,
                    'message': f"Fee '{fee_name}' for student '{student_name}' deleted successfully.",
                    'class_id': class_id
                })
                
        except Exception as e:
            logger.error(f"Error deleting fee {fee_id} for student {student_id} by user {user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f"Error deleting fee: {str(e)}"
            }, status=400)
    
    # For non-POST requests, redirect to avoid unintended deletions
    messages.info(request, "Please use the form to delete the fee.")
    return redirect('finance:assign_fees_to_students', class_id=class_id)

@accountant_role_required
def update_student_fee_specific(request, student_id, fee_id):
    """Update a specific StudentFee assignment."""
    user = request.user
    creator = getattr(request, 'creator', request.user)
    student_fee = get_object_or_404(
        StudentFee,
        id=fee_id,
        student_id=student_id,
        teacherclass__user=creator
    )
    
    if request.method == 'POST':
        form = StudentFeeUpdateForm(request.POST)
        if form.is_valid():
            try:
                student_fee.amount_required = form.cleaned_data['amount_required']
                student_fee.start_date = form.cleaned_data['start_date']
                student_fee.end_date = form.cleaned_data['end_date']
                student_fee.save()
                ChangeLog.objects.create(
                    user=user,
                    action='UPDATE',
                    model_name='StudentFee',
                    object_id=fee_id,
                    description=f"Updated fee {student_fee.fee.fee_name} for student {student_fee.student.fullName} in {student_fee.teacherclass.ClassName.class_name}"
                )
                messages.success(request, f"Fee '{student_fee.fee.fee_name}' for student '{student_fee.student.fullName}' updated successfully.")
                logger.info(f"User {user.username} updated fee {student_fee.fee.fee_name} for student {student_fee.student.fullName}")
            except Exception as e:
                messages.error(request, f"Error updating fee: {str(e)}")
                logger.error(f"Error updating fee {fee_id} for student {student_id} by user {user.username}: {str(e)}")
        else:
            messages.error(request, "Please correct the errors in the form.")
            logger.error(f"Form errors in update_student_fee: {form.errors.as_json()}")
        
        return redirect('finance:assign_fees_to_students', class_id=student_fee.teacherclass.id)
    
    return redirect('finance:assign_fees_to_students', class_id=student_fee.teacherclass.id)

@accountant_role_required
def fee_account_management(request):
    creator = getattr(request, 'creator', request.user)
    selected_class_id = request.GET.get('class_id')

    # Filter TeacherClass by creator, including only active academic years
    teacher_classes = TeacherClass.objects.filter(
        user=creator, 
        academicclassyear__active_year=True
    ).select_related('ClassName', 'academicclassyear').distinct()

    # Filter Fees by selected class and creator
    fees = Fee.objects.filter(
        teacherclass__in=teacher_classes, 
        user=creator
    ).distinct() if teacher_classes.exists() else Fee.objects.none()

    if selected_class_id:
        fees = fees.filter(teacherclass__id=selected_class_id)
        try:
            selected_class = get_object_or_404(
                TeacherClass, 
                id=selected_class_id, 
                user=creator
            )
        except Exception as e:
            logger.error(f"Error fetching selected class {selected_class_id}: {e}")
            messages.error(request, "Invalid class selected.")
            selected_class = None
    else:
        selected_class = None

    # Fetch FeeAccountNumber entries
    fee_accounts = FeeAccountNumber.objects.filter(
        user=creator, 
        teacherclass__in=teacher_classes
    ).select_related('fee', 'teacherclass')

    context = {
        'teacher_classes': teacher_classes,
        'fees': fees,
        'selected_class_id': selected_class_id,
        'selected_class': selected_class,
        'fee_accounts': fee_accounts,
    }
    return render(request, 'accountant/fee_account_management.html', context)

@accountant_role_required
def create_fee_account(request):
    creator = getattr(request, 'creator', request.user)
    if request.method == 'POST':
        try:
            teacherclass_id = request.POST.get('teacherclass')
            fee_id = request.POST.get('fee')
            account_number = request.POST.get('account_number')
            account_name = request.POST.get('account_name')
            is_active = request.POST.get('is_active') == 'true'

            teacherclass = get_object_or_404(
                TeacherClass, 
                id=teacherclass_id, 
                user=creator
            )
            fee = get_object_or_404(
                Fee, 
                id=fee_id, 
                teacherclass=teacherclass, 
                user=creator
            )

            fee_account = FeeAccountNumber(
                user=creator,
                teacherclass=teacherclass,
                fee=fee,
                account_number=account_number,
                account_name=account_name,
                is_active=is_active
            )
            fee_account.save()
            messages.success(request, f"Fee account {account_number} created successfully.")
            logger.info(f"Fee account {account_number} created by {creator.username}")
        except Exception as e:
            logger.error(f"Error creating fee account: {e}")
            messages.error(request, "Error creating fee account.")
        return redirect(reverse('finance:fee_account_management') + f'?class_id={teacherclass_id}')
    return redirect('finance:fee_account_management')

@accountant_role_required
def update_fee_account(request, fee_account_id):
    creator = getattr(request, 'creator', request.user)
    fee_account = get_object_or_404(
        FeeAccountNumber, 
        id=fee_account_id, 
        user=creator
    )
    if request.method == 'POST':
        try:
            teacherclass_id = request.POST.get('teacherclass')
            fee_id = request.POST.get('fee')
            account_number = request.POST.get('account_number')
            account_name = request.POST.get('account_name')
            is_active = request.POST.get('is_active') == 'true'

            teacherclass = get_object_or_404(
                TeacherClass, 
                id=teacherclass_id, 
                user=creator
            )
            fee = get_object_or_404(
                Fee, 
                id=fee_id, 
                teacherclass=teacherclass, 
                user=creator
            )

            fee_account.teacherclass = teacherclass
            fee_account.fee = fee
            fee_account.account_number = account_number
            fee_account.account_name = account_name
            fee_account.is_active = is_active
            fee_account.save()
            messages.success(request, f"Fee account {account_number} updated successfully.")
            logger.info(f"Fee account {account_number} updated by {creator.username}")
        except Exception as e:
            logger.error(f"Error updating fee account {fee_account_id}: {e}")
            messages.error(request, "Error updating fee account.")
        return redirect(reverse('finance:fee_account_management') + f'?class_id={teacherclass_id}')
    return render(request, 'accountant/edit_fee_account.html', {
        'fee_account': fee_account,
        'teacher_classes': TeacherClass.objects.filter(
            user=creator, 
            academicclassyear__active_year=True
        ).select_related('ClassName', 'academicclassyear'),
        'fees': Fee.objects.filter(
            teacherclass=fee_account.teacherclass, 
            user=creator
        ) if fee_account.teacherclass else Fee.objects.none(),
    })

@accountant_role_required
def delete_fee_account(request, fee_account_id):
    creator = getattr(request, 'creator', request.user)
    fee_account = get_object_or_404(
        FeeAccountNumber, 
        id=fee_account_id, 
        user=creator
    )
    teacherclass_id = fee_account.teacherclass.id if fee_account.teacherclass else ''
    try:
        account_number = fee_account.account_number
        fee_account.delete()
        messages.success(request, f"Fee account {account_number} deleted successfully.")
        logger.info(f"Fee account {account_number} deleted by {creator.username}")
    except Exception as e:
        logger.error(f"Error deleting fee account {fee_account_id}: {e}")
        messages.error(request, "Error deleting fee account.")
    return redirect(reverse('finance:fee_account_management') + (f'?class_id={teacherclass_id}' if teacherclass_id else ''))



# finance/dashboard_views.py
import io, base64, logging
import matplotlib.pyplot as plt
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from rps_app.models import TeacherClass
from .models import Fee, StudentFee, PayFee, Discount

logger = logging.getLogger(__name__)

def _plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f'data:image/png;base64,{img}'

@login_required
def finance_dashboard(request):
    user = request.user
    classes = TeacherClass.objects.filter(user=user, academicclassyear__active_year=True)
    fees = Fee.objects.filter(teacherclass__in=classes, user=user).distinct()

    selected_class_ids = request.GET.getlist('class_id')
    fee_id = request.GET.get('fee_id')

    charts = {}
    context = {
        'classes': classes,
        'fees': fees,
        'selected_class_ids': selected_class_ids,
        'fee_id': fee_id,
    }

    if selected_class_ids and fee_id:
        tclasses = TeacherClass.objects.filter(id__in=selected_class_ids, user=user)
        fee = get_object_or_404(Fee, id=fee_id, teacherclass__in=tclasses, user=user)

        # StudentFee records
        sfees = StudentFee.objects.filter(
            teacherclass__in=tclasses, fee=fee
        ).select_related('student')

        # Payments + Discounts
        data = []
        for sf in sfees:
            paid = PayFee.objects.filter(student=sf.student, fee=fee).aggregate(t=Sum('amount_paid'))['t'] or 0
            disc = Discount.objects.filter(student=sf.student, fee=fee, teacherclass__in=tclasses).aggregate(d=Sum('discount_amount'))['d'] or 0
            balance = sf.amount_required - paid - disc
            status = 'Complete' if balance <= 0 else 'Remain'
            data.append({'paid': paid, 'balance': balance, 'status': status})

        # 1. Payment Status Pie
        status_counts = {}
        for d in data:
            status_counts[d['status']] = status_counts.get(d['status'], 0) + 1
        if status_counts:
            fig, ax = plt.subplots()
            ax.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
            ax.set_title(f'Payment Status – {fee.fee_name}')
            charts['payment_pie'] = _plot_to_base64(fig)

        # 2. Total Paid vs Expected (Bar)
        total_paid = sum(d['paid'] for d in data)
        total_expected = sum(sf.amount_required for sf in sfees)
        fig, ax = plt.subplots()
        ax.bar(['Paid', 'Expected'], [total_paid, total_expected], color=['green', 'orange'])
        ax.set_ylabel('Amount')
        ax.set_title('Total Paid vs Expected')
        charts['paid_vs_expected'] = _plot_to_base64(fig)

        # 3. Top 5 Payers
        payers = PayFee.objects.filter(
            fee=fee, student__teacherclass__in=tclasses
        ).values('student__fullName').annotate(total=Sum('amount_paid')).order_by('-total')[:5]
        if payers:
            names = [p['student__fullName'] for p in payers]
            amounts = [p['total'] for p in payers]
            fig, ax = plt.subplots()
            ax.barh(names[::-1], amounts[::-1], color='lightcoral')
            ax.set_xlabel('Amount Paid')
            ax.set_title('Top 5 Payers')
            charts['top_payers'] = _plot_to_base64(fig)

    context['charts'] = charts
    return render(request, 'dashboards/finance_dashboard.html', context)


def _student_phone_number(student):
    if hasattr(student, "phone_number") and student.phone_number:
        return str(student.phone_number)
    if getattr(student, "contact", None):
        return str(student.contact)
    return ""


def _split_student_name(student):
    full_name = (student.fullName or student.user.username or "Student").strip()
    parts = full_name.split()
    if not parts:
        return "Student", "User"
    if len(parts) == 1:
        return parts[0], "Student"
    return parts[0], " ".join(parts[1:])


def _parse_request_data(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
    return request.POST


def _map_tx_status(status_value):
    if not status_value:
        return PaymentTransaction.TX_PENDING
    status_value = str(status_value).lower()
    if status_value in {"success", "paid", "completed"}:
        return PaymentTransaction.TX_SUCCESS
    if status_value in {"failed", "error", "declined"}:
        return PaymentTransaction.TX_FAILED
    if status_value in {"expired"}:
        return PaymentTransaction.TX_EXPIRED
    return PaymentTransaction.TX_PENDING


def _normalize_snippe_status(status_value):
    return str(status_value or "").strip().lower()


def _default_webhook_url(request):
    webhook_url = request.build_absolute_uri(reverse("finance:snippe_webhook"))
    if webhook_url.startswith("http://"):
        webhook_url = f"https://{request.get_host()}{reverse('finance:snippe_webhook')}"
    return webhook_url


def _configured_webhook_url():
    config = WebhookConfiguration.objects.first()
    if config and config.webhook_url:
        return config.webhook_url.strip()
    return ""


def _resolve_webhook_url(request, override_url=""):
    webhook_url = _default_webhook_url(request)
    configured_url = _configured_webhook_url()
    if configured_url:
        validator = URLValidator()
        try:
            validator(configured_url)
            if configured_url.lower().startswith("https://"):
                webhook_url = configured_url
        except ValidationError:
            pass
    if override_url:
        validator = URLValidator()
        validator(override_url)
        if not override_url.lower().startswith("https://"):
            raise ValidationError("Webhook URL must use HTTPS.")
        webhook_url = override_url
    return webhook_url


def _notify_student_payment_completion(transaction, amount_value, amount_currency):
    _notify_student_payment_status(
        transaction,
        status_value=PaymentTransaction.TX_COMPLETED,
        amount_value=amount_value,
        amount_currency=amount_currency,
    )


def _notify_student_payment_status(transaction, status_value, amount_value, amount_currency, failure_reason=None):
    if not transaction:
        return
    payment = transaction.payment
    student = payment.student if payment else None
    if not payment or not student:
        return
    creator = payment.user or (payment.teacherclass.user if payment.teacherclass else None)
    if not creator:
        return

    amount_value = amount_value if amount_value is not None else transaction.amount
    amount_currency = amount_currency or transaction.currency
    student_name = student.fullName or student.user.username
    fee_name = payment.fee.fee_name if payment.fee else "fee payment"
    normalized_status = _normalize_snippe_status(status_value)
    if normalized_status in {PaymentTransaction.TX_FAILED, "failed", "error", "declined"}:
        message = (
            f"Hello {student_name}, your payment of {amount_value} {amount_currency} "
            f"for {fee_name} was not completed successfully."
        )
        if failure_reason:
            message = f"{message} Reason: {failure_reason}"
        subject = "Payment Failed"
    else:
        message = (
            f"Hello {student_name}, your payment of {amount_value} {amount_currency} "
            f"for {fee_name} has been completed successfully."
        )
        subject = "Payment Completed"

    raw_response = transaction.raw_response or {}
    if not isinstance(raw_response, dict):
        raw_response = {}
    notified_statuses = raw_response.get("notification_sent_statuses", [])
    if not isinstance(notified_statuses, list):
        notified_statuses = []
    if normalized_status in notified_statuses:
        return

    phone_number = _student_phone_number(student)
    sms_sent = _send_sms_message(creator, phone_number, message) if phone_number else False
    email_address = student.user.email if student.user else ""
    email_sent = _send_email_message(
        creator,
        email_address,
        subject,
        message,
        template_name="emails/payment_success.html",
        context={
            "recipient_name": student_name,
            "payment": {
                "amount": amount_value,
                "currency": amount_currency,
                "name": fee_name,
                "order_id": transaction.order_id,
                "method": transaction.get_method_display() if hasattr(transaction, "get_method_display") else transaction.method,
            },
        },
    )
    if phone_number:
        _record_communication(
            creator=creator,
            student=student,
            channel="sms",
            recipient=phone_number,
            subject=subject,
            message=message,
            status="sent" if sms_sent else "failed",
            metadata={"order_id": transaction.order_id, "transaction_id": transaction.id},
        )
    if email_address:
        _record_communication(
            creator=creator,
            student=student,
            channel="email",
            recipient=email_address,
            subject=subject,
            message=message,
            status="sent" if email_sent else "failed",
            metadata={"order_id": transaction.order_id, "transaction_id": transaction.id},
        )
    if sms_sent or email_sent:
        notified_statuses.append(normalized_status)
        raw_response["notification_sent_statuses"] = notified_statuses
        transaction.raw_response = raw_response
        transaction.notification_sent = True
        transaction.save(update_fields=["notification_sent", "raw_response", "updated_at"])


@csrf_exempt
@require_POST
def snippe_webhook(request):
    payload = {}
    try:
        if request.body:
            payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        payload = {}

    if not isinstance(payload, dict):
        payload = {}

    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    order_id = metadata.get("order_id") or data.get("external_reference") or data.get("order_id")
    status_value = _normalize_snippe_status(data.get("status") or payload.get("status"))
    reference = data.get("reference") or payload.get("reference") or ""
    amount_data = data.get("amount") if isinstance(data.get("amount"), dict) else {}
    amount_value = amount_data.get("value")
    amount_currency = amount_data.get("currency") or "TZS"
    failure_reason = data.get("failure_reason") or payload.get("failure_reason") or ""

    if order_id:
        create_payment = CreatePayment.objects.filter(order_id=order_id).first()
        if create_payment:
            if status_value in {"completed", "success", "paid"}:
                create_payment.payment_status = CreatePayment.STATUS_COMPLETED
            elif status_value in {"failed", "error", "declined"}:
                create_payment.payment_status = CreatePayment.STATUS_FAILED
            else:
                create_payment.payment_status = CreatePayment.STATUS_PENDING

            if data.get("payment_token"):
                create_payment.payment_token = data.get("payment_token")
            create_payment.save(update_fields=["payment_status", "payment_token", "updated_at"])

            _notify_create_payment_status(create_payment, create_payment.payment_status, failure_reason=failure_reason)

        transaction = PaymentTransaction.objects.filter(order_id=order_id).first()
        if transaction:
            transaction.tx_status = _map_tx_status(status_value)
            if reference:
                transaction.snippe_reference = reference
            if data.get("payment_token"):
                transaction.payment_token = data.get("payment_token")
            transaction.raw_response = payload
            transaction.save(update_fields=["tx_status", "snippe_reference", "payment_token", "raw_response", "updated_at"])

            payment = transaction.payment
            if payment:
                if amount_value is not None:
                    payment.amount_paid = max(payment.amount_paid or 0, Decimal(amount_value))
                if transaction.tx_status == PaymentTransaction.TX_COMPLETED:
                    payment.status = StudentPayment.STATUS_PAID
                elif transaction.tx_status == PaymentTransaction.TX_FAILED:
                    payment.status = StudentPayment.STATUS_FAILED
                else:
                    payment.status = StudentPayment.STATUS_PENDING
                payment.save(update_fields=["amount_paid", "status", "updated_at"])
                if transaction.tx_status in {PaymentTransaction.TX_COMPLETED, PaymentTransaction.TX_SUCCESS}:
                    _sync_online_payfee(payment, completed_total=transaction.amount)

            if status_value in {"completed", "success", "paid", "failed", "error", "declined"}:
                _notify_student_payment_status(
                    transaction,
                    status_value=status_value,
                    amount_value=amount_value,
                    amount_currency=amount_currency,
                    failure_reason=failure_reason,
                )

        segment_tx = PaymentSegmentTransaction.objects.filter(order_id=order_id).select_related("payment_segment", "payment_segment__student", "payment_segment__fee_name").first()
        if segment_tx:
            segment_tx.tx_status = _map_tx_status(status_value)
            if reference:
                segment_tx.snippe_reference = reference
            if data.get("payment_token"):
                segment_tx.payment_token = data.get("payment_token")
                segment_tx.bill_pay_number = data.get("payment_token")
            segment_tx.raw_response = payload
            update_fields = ["tx_status", "snippe_reference", "payment_token", "bill_pay_number", "raw_response", "updated_at"]
            if segment_tx.tx_status in {PaymentSegmentTransaction.TX_COMPLETED, PaymentSegmentTransaction.TX_SUCCESS}:
                segment_tx.completed_at = timezone.now()
                update_fields.append("completed_at")
            segment_tx.save(update_fields=update_fields)
            segment = _sync_payment_segment_status(segment_tx.payment_segment)
            if segment_tx.tx_status in {PaymentSegmentTransaction.TX_COMPLETED, PaymentSegmentTransaction.TX_SUCCESS}:
                _send_segment_success_notifications(segment, segment_tx)

    return JsonResponse({"received": True})


def _sync_online_payfee(payment, completed_total=None):
    if not payment or not payment.student or not payment.fee:
        return None

    completed_statuses = [PaymentTransaction.TX_COMPLETED, PaymentTransaction.TX_SUCCESS]
    if completed_total is None:
        completed_total = (
            payment.transactions.filter(tx_status__in=completed_statuses).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
    total_paid = completed_total
    if payment.status == StudentPayment.STATUS_PAID and payment.amount_paid and payment.amount_paid > completed_total:
        total_paid += payment.amount_paid - completed_total

    if total_paid <= 0:
        return None

    latest_completed_tx = (
        payment.transactions.filter(tx_status__in=completed_statuses).order_by("-created_at").first()
    )
    latest_billpay = (
        payment.transactions.filter(method=PaymentTransaction.METHOD_BILLPAY).order_by("-created_at").first()
    )
    date_paid = timezone.localdate()
    if latest_completed_tx and latest_completed_tx.created_at:
        date_paid = latest_completed_tx.created_at.date()
    elif payment.updated_at:
        date_paid = payment.updated_at.date()

    payer_account_no = ""
    if latest_completed_tx:
        payer_account_no = latest_completed_tx.bill_pay_number or latest_completed_tx.payment_token or ""
    elif latest_billpay:
        payer_account_no = latest_billpay.bill_pay_number or latest_billpay.payment_token or ""

    user = payment.user or payment.student.manager or payment.student.user
    return PayFee.objects.update_or_create(
        student=payment.student,
        fee=payment.fee,
        description=f"Online payment ({payment.id})",
        defaults={
            "user": user,
            "amount_paid": total_paid,
            "date_paid": date_paid,
            "payer_account_no": payer_account_no or None,
        },
    )


def _extract_snippe_data(response):
    """Normalize Snippe payload so fields can be read consistently."""
    payload = response.get("data") if isinstance(response, dict) else {}
    if not isinstance(payload, dict):
        return {}
    nested = payload.get("data")
    if isinstance(nested, dict):
        return nested
    return payload


def _gateway_payment_payload(raw_response):
    """Return payment object from Snippe response regardless of nesting style."""
    if not isinstance(raw_response, dict):
        return {}
    data = raw_response.get("data")
    if isinstance(data, dict):
        nested = data.get("data")
        if isinstance(nested, dict):
            items = nested.get("items")
            if isinstance(items, list) and items:
                return items[0] if isinstance(items[0], dict) else {}
            return nested
        items = data.get("items")
        if isinstance(items, list) and items:
            return items[0] if isinstance(items[0], dict) else {}
        return data
    return {}


def _extract_gateway_payment_items(response):
    """Return list of gateway payment items from Snippe list-payments response."""
    if not isinstance(response, dict):
        return []

    payload = response.get("data")
    if not isinstance(payload, dict):
        return []

    candidates = []
    direct_items = payload.get("items")
    if isinstance(direct_items, list):
        candidates = direct_items
    nested = payload.get("data")
    if isinstance(nested, dict):
        nested_items = nested.get("items")
        if isinstance(nested_items, list):
            candidates = nested_items

    return [item for item in candidates if isinstance(item, dict)]


def _fetch_gateway_payments_by_order_id(limit=200):
    """Fetch latest gateway payments and index them by metadata.order_id."""
    try:
        response = SnippePaymentClient().list_payments(limit=limit, offset=0)
    except Exception:
        return {}

    if not isinstance(response, dict) or not response.get("success"):
        return {}

    indexed = {}
    for item in _extract_gateway_payment_items(response):
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        order_id = metadata.get("order_id")
        if order_id:
            indexed[order_id] = item
    return indexed


def _fetch_gateway_payments_by_token(limit=200):
    """Fetch latest gateway payments and index them by payment token."""
    try:
        response = SnippePaymentClient().list_payments(limit=limit, offset=0)
    except Exception:
        return {}

    if not isinstance(response, dict) or not response.get("success"):
        return {}

    indexed = {}
    for item in _extract_gateway_payment_items(response):
        payment_token = str(item.get("payment_token") or "").strip()
        if payment_token:
            indexed[payment_token] = item
    return indexed


def _resolve_payment_tracking(payment, gateway_by_token):
    latest_transaction = payment.transactions.order_by("-created_at").first() if payment else None
    latest_billpay = (
        payment.transactions.filter(method=PaymentTransaction.METHOD_BILLPAY).order_by("-created_at").first()
        if payment
        else None
    )

    request_status = ""
    transaction_status = PaymentTransaction.TX_PENDING
    payment_status = _display_payment_status(payment)
    transaction_completed_at = None

    if latest_transaction:
        request_status = _extract_request_status(latest_transaction.raw_response)
        transaction_status = _display_transaction_status(latest_transaction)

    token = ""
    if latest_billpay:
        token = str(latest_billpay.payment_token or latest_billpay.bill_pay_number or "").strip()

    gateway_item = gateway_by_token.get(token) if token else None
    if gateway_item:
        gateway_status = _normalize_gateway_status(gateway_item.get("status"))
        if gateway_status:
            transaction_status = gateway_status
            payment_status = (
                StudentPayment.STATUS_PAID
                if gateway_status == PaymentTransaction.TX_COMPLETED
                else StudentPayment.STATUS_PENDING
            )

        completed_at_raw = gateway_item.get("completed_at")
        if completed_at_raw:
            transaction_completed_at = parse_datetime(completed_at_raw)

    return {
        "latest_billpay": latest_billpay,
        "request_status": request_status,
        "transaction_status": transaction_status,
        "payment_status": payment_status,
        "transaction_completed_at": transaction_completed_at,
    }


def _build_transaction(payment, method, amount, phone_number, order_id, idempotency_key, response):
    data = _extract_snippe_data(response)
    response_data = response.get("data") if isinstance(response, dict) else {}
    payment_token = (
        data.get("payment_token")
        or data.get("token")
        or data.get("bill_pay_number")
        or data.get("control_number")
        or ""
    )
    # Snippe may return request status at top-level and payment status inside `data`.
    # Use payment status from data payload for transaction status mapping.
    tx_status = _map_tx_status(data.get("status"))
    expires_at = None
    expires_value = data.get("expires_at") or data.get("expiry")
    if expires_value:
        expires_at = parse_datetime(expires_value)
        if expires_at is None:
            try:
                expires_at = timezone.datetime.fromisoformat(expires_value)
            except (ValueError, TypeError):
                expires_at = None

    return PaymentTransaction.objects.create(
        payment=payment,
        order_id=order_id,
        method=method,
        currency=(data.get("amount") or {}).get("currency") if isinstance(data.get("amount"), dict) else data.get("currency") or "TZS",
        amount=amount,
        phone_number=phone_number,
        bill_pay_number=payment_token,
        snippe_reference=data.get("reference") or data.get("snippe_reference") or "",
        payment_token=payment_token,
        payment_url=data.get("payment_url") or "",
        payment_qr_code=data.get("payment_qr_code") or data.get("qr_code") or "",
        idempotency_key=idempotency_key,
        tx_status=tx_status,
        raw_response=response,
        expires_at=expires_at,
    )


def _get_payment_context(request, creator, student_id, fee_id, class_id):
    teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator)
    fee = get_object_or_404(Fee, id=fee_id, teacherclass=teacherclass)
    student = get_object_or_404(Student, id=student_id, manager=creator, teacherclass=teacherclass)
    assignment = StudentFee.objects.filter(student=student, fee=fee, teacherclass=teacherclass).first()
    if not assignment:
        return None, None, None, None, JsonResponse(
            {"success": False, "error": "Student fee assignment not found."}, status=404
        )

    payment, created = StudentPayment.objects.get_or_create(
        student=student,
        fee=fee,
        teacherclass=teacherclass,
        defaults={
            "user": request.user,
            "amount_due": assignment.amount_required or 0,
            "status": StudentPayment.STATUS_PENDING,
        },
    )
    amount_due = assignment.amount_required or 0
    if payment.amount_due != amount_due:
        payment.amount_due = amount_due
        if payment.user is None:
            payment.user = request.user
        payment.save(update_fields=["amount_due", "user", "updated_at"])

    return teacherclass, fee, student, payment, None


def _is_ajax_or_json_request(request):
    requested_with = request.headers.get("X-Requested-With")
    if requested_with == "XMLHttpRequest":
        return True
    if request.content_type == "application/json":
        return True
    accepts = request.headers.get("Accept", "")
    return "application/json" in accepts


def _manage_online_payment_redirect(class_id=None, fee_id=None):
    base_url = reverse("finance:manage_online_payment")
    params = {}
    if class_id:
        params["class_id"] = class_id
    if fee_id:
        params["fee_id"] = fee_id
    if not params:
        return redirect(base_url)
    return redirect(f"{base_url}?{urlencode(params)}")


def _unique_order_reference(prefix, payment_id):
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}-{payment_id}-{timestamp}-{uuid.uuid4().hex[:6]}"


def _extract_request_status(response):
    if not isinstance(response, dict):
        return ""
    return str(response.get("status") or "").lower()


def _normalize_gateway_status(status_value):
    if not status_value:
        return ""
    normalized = str(status_value).strip().lower()
    if normalized in {"success", "paid"}:
        return "completed"
    return normalized


def _display_transaction_status(transaction):
    if not transaction:
        return PaymentTransaction.TX_PENDING
    gateway_status = _normalize_gateway_status(
        _gateway_payment_payload(transaction.raw_response).get("status")
    )
    if gateway_status:
        return gateway_status
    return _normalize_gateway_status(transaction.tx_status) or PaymentTransaction.TX_PENDING


def _display_payment_status(payment):
    if not payment:
        return StudentPayment.STATUS_PENDING
    status = str(payment.status or "").strip().lower()
    if status in {PaymentTransaction.TX_SUCCESS, PaymentTransaction.TX_COMPLETED}:
        return StudentPayment.STATUS_PAID
    if status == PaymentTransaction.TX_FAILED:
        return StudentPayment.STATUS_FAILED
    return status or StudentPayment.STATUS_PENDING




def _normalize_status_filter_value(status_value):
    normalized = (status_value or "").strip().lower()
    if not normalized:
        return ""
    if normalized in {"success", "completed", "paid"}:
        return PaymentTransaction.TX_COMPLETED
    if normalized in {"pending"}:
        return PaymentTransaction.TX_PENDING
    if normalized in {"failed", "fail", "error"}:
        return PaymentTransaction.TX_FAILED
    if normalized == PaymentTransaction.TX_EXPIRED:
        return PaymentTransaction.TX_EXPIRED
    return ""


def _transaction_matches_status_filter(transaction, gateway_data, normalized_filter):
    if not normalized_filter:
        return True

    candidates = [
        _normalize_status_filter_value(transaction.tx_status),
        _normalize_status_filter_value((transaction.raw_response or {}).get("status") if isinstance(transaction.raw_response, dict) else ""),
        _normalize_status_filter_value((gateway_data or {}).get("status") if isinstance(gateway_data, dict) else ""),
    ]
    return normalized_filter in candidates


def _split_full_name(value):
    parts = [part for part in (value or "").strip().split(" ") if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _build_success_message(full_name, amount, currency, custom_message=None):
    base_message = (
        f"Hello {full_name or 'Customer'}, your payment of {amount} {currency} "
        "has been completed successfully. Thank you."
    )
    if custom_message:
        return f"{custom_message}\n\n{base_message}"
    return base_message


def _build_failed_message(full_name, amount, currency, failure_reason=None):
    base_message = (
        f"Hello {full_name or 'Customer'}, your payment of {amount} {currency} "
        "was not completed successfully."
    )
    if failure_reason:
        return f"{base_message}\nReason: {failure_reason}"
    return base_message


def _notify_create_payment_status(create_payment, status_value, failure_reason=None):
    if create_payment.notification_sent:
        return
    if status_value == CreatePayment.STATUS_COMPLETED:
        subject = "Payment Completed"
        message = _build_success_message(
            create_payment.full_name,
            create_payment.amount,
            create_payment.currency,
            create_payment.success_message,
        )
        template_name = "emails/payment_success.html"
        context = {
            "recipient_name": create_payment.full_name or "Customer",
            "payment": {
                "amount": create_payment.amount,
                "currency": create_payment.currency,
                "name": create_payment.payment_name or "Payment",
                "order_id": create_payment.order_id,
                "method": create_payment.get_payment_option_display(),
            },
        }
    elif status_value == CreatePayment.STATUS_FAILED:
        subject = "Payment Failed"
        message = _build_failed_message(
            create_payment.full_name,
            create_payment.amount,
            create_payment.currency,
            failure_reason=failure_reason,
        )
        template_name = None
        context = None
    else:
        return

    sms_sent = _send_sms_message(create_payment.user, create_payment.phone_number, message)
    email_sent = _send_email_message(
        create_payment.user,
        create_payment.email,
        subject,
        message,
        template_name=template_name,
        context=context,
    )
    if create_payment.phone_number:
        _record_communication(
            creator=create_payment.user,
            student=None,
            channel="sms",
            recipient=create_payment.phone_number,
            subject=subject,
            message=message,
            status="sent" if sms_sent else "failed",
            metadata={"order_id": create_payment.order_id, "payment_id": create_payment.id},
        )
    if create_payment.email:
        _record_communication(
            creator=create_payment.user,
            student=None,
            channel="email",
            recipient=create_payment.email,
            subject=subject,
            message=message,
            status="sent" if email_sent else "failed",
            metadata={"order_id": create_payment.order_id, "payment_id": create_payment.id},
        )
    if sms_sent or email_sent:
        create_payment.notification_sent = True
        create_payment.save(update_fields=["notification_sent", "updated_at"])


def _send_sms_message(creator, phone_number, message):
    if not phone_number:
        return False
    try:
        sms_config = SmsConfiguration.objects.get(user=creator)
    except SmsConfiguration.DoesNotExist:
        logger.warning("SMS configuration not found for payment notifications.")
        return False

    payload = {
        "source_addr": sms_config.source_addr,
        "encoding": 0,
        "message": message,
        "recipients": [{"recipient_id": str(creator.id), "dest_addr": str(phone_number)}],
    }

    try:
        response = requests.post(
            sms_config.url_required,
            json=payload,
            auth=HTTPBasicAuth(sms_config.username, sms_config.pswd),
            timeout=10,
        )
        return response.status_code == 200
    except requests.RequestException as exc:
        logger.error("SMS send failed: %s", exc)
        return False


def _record_communication(creator, student, channel, recipient, subject, message, status, metadata=None):
    try:
        StudentCommunicationLog.objects.create(
            user=creator,
            student=student,
            channel=channel,
            recipient=recipient,
            subject=subject,
            message=message,
            status=status,
            sent_at=timezone.now() if status == "sent" else None,
            metadata=metadata or {},
        )
    except Exception as exc:
        logger.warning("Unable to record communication log: %s", exc)


def _send_email_message(creator, to_email, subject, body, template_name=None, context=None):
    if not to_email:
        return False
    email_settings = get_email_settings(creator)

    original_settings = {
        "EMAIL_BACKEND": getattr(settings, "EMAIL_BACKEND", None),
        "EMAIL_HOST": getattr(settings, "EMAIL_HOST", None),
        "EMAIL_PORT": getattr(settings, "EMAIL_PORT", None),
        "EMAIL_USE_TLS": getattr(settings, "EMAIL_USE_TLS", None),
        "EMAIL_HOST_USER": getattr(settings, "EMAIL_HOST_USER", None),
        "EMAIL_HOST_PASSWORD": getattr(settings, "EMAIL_HOST_PASSWORD", None),
        "DEFAULT_FROM_EMAIL": getattr(settings, "DEFAULT_FROM_EMAIL", None),
    }

    settings.EMAIL_BACKEND = email_settings["EMAIL_BACKEND"]
    settings.EMAIL_HOST = email_settings["EMAIL_HOST"]
    settings.EMAIL_PORT = email_settings["EMAIL_PORT"]
    settings.EMAIL_USE_TLS = email_settings["EMAIL_USE_TLS"]
    settings.EMAIL_HOST_USER = email_settings["EMAIL_HOST_USER"]
    settings.EMAIL_HOST_PASSWORD = email_settings["EMAIL_HOST_PASSWORD"]
    settings.DEFAULT_FROM_EMAIL = email_settings["DEFAULT_FROM_EMAIL"]

    try:
        html_body = None
        if template_name:
            html_body = render_to_string(
                template_name,
                {
                    "subject": subject,
                    "message": body,
                    "support_email": email_settings["DEFAULT_FROM_EMAIL"],
                    **(context or {}),
                },
            )
        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=email_settings["DEFAULT_FROM_EMAIL"],
            to=[to_email],
        )
        if html_body:
            email.attach_alternative(html_body, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as exc:
        logger.error("Email send failed: %s", exc)
        return False
    finally:
        for key, value in original_settings.items():
            if value is not None:
                setattr(settings, key, value)
            elif hasattr(settings, key):
                delattr(settings, key)



def _sync_payment_segment_status(segment):
    completed_statuses = [PaymentSegmentTransaction.TX_COMPLETED, PaymentSegmentTransaction.TX_SUCCESS]
    completed_total = segment.transactions.filter(tx_status__in=completed_statuses).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    segment.total_paid = completed_total
    segment.status = (
        PaymentSegment.STATUS_COMPLETE
        if segment.amount_required and completed_total >= segment.amount_required
        else PaymentSegment.STATUS_PENDING
    )
    segment.save(update_fields=["total_paid", "status", "updated_at"])
    return segment


def _build_segment_for_payment(payment):
    if not payment or not payment.student_id or not payment.fee_id or not payment.teacherclass_id:
        return None
    student_fee = StudentFee.objects.filter(
        student_id=payment.student_id,
        fee_id=payment.fee_id,
        teacherclass_id=payment.teacherclass_id,
    ).first()
    base_amount = student_fee.amount_required if student_fee and student_fee.amount_required else payment.amount_due
    discount = Discount.objects.filter(
        student_id=payment.student_id,
        fee_id=payment.fee_id,
        teacherclass_id=payment.teacherclass_id,
    ).aggregate(total=Sum("discount_amount"))["total"] or Decimal("0.00")
    adjusted_required = max((base_amount or Decimal("0.00")) - discount, Decimal("0.00"))
    segment, _ = PaymentSegment.objects.get_or_create(
        user=payment.user or payment.student.user,
        teacherclass_id=payment.teacherclass_id,
        student_id=payment.student_id,
        fee_name_id=payment.fee_id,
        studentfee=student_fee,
        defaults={
            "amount_required": adjusted_required,
            "segment_amount": Decimal("0.00"),
            "status": PaymentSegment.STATUS_PENDING,
        },
    )
    if segment.amount_required != adjusted_required:
        segment.amount_required = adjusted_required
        segment.save(update_fields=["amount_required", "updated_at"])
    return _sync_payment_segment_status(segment)


def _send_segment_success_notifications(segment, tx):
    if tx.notification_sent:
        return
    student = segment.student
    creator = segment.user
    subject = f"Payment received for {segment.fee_name.fee_name}"
    message = (
        f"Hello {student.fullName or student.user.username}, your payment of TZS {tx.amount} "
        f"for {segment.fee_name.fee_name} was received successfully. "
        f"Total paid: TZS {segment.total_paid}. Remaining: TZS {max(segment.amount_required - segment.total_paid, Decimal('0.00'))}."
    )
    sms_sent = _send_sms_message(creator, _student_phone_number(student), message)
    email_sent = _send_email_message(creator, student.user.email, subject, message)
    _record_communication(
        creator=creator,
        student=student,
        channel="sms",
        recipient=_student_phone_number(student) or "",
        subject=subject,
        message=message,
        status="sent" if sms_sent else "failed",
        metadata={"segment_id": segment.id, "order_id": tx.order_id},
    )
    _record_communication(
        creator=creator,
        student=student,
        channel="email",
        recipient=student.user.email or "",
        subject=subject,
        message=message,
        status="sent" if email_sent else "failed",
        metadata={"segment_id": segment.id, "order_id": tx.order_id},
    )
    tx.notification_sent = sms_sent or email_sent
    tx.save(update_fields=["notification_sent", "updated_at"])


def _create_segment_transaction(request, payment, segment_amount, method):
    segment = _build_segment_for_payment(payment)
    if not segment:
        return None, JsonResponse({"success": False, "error": "Unable to build payment segment."}, status=400)

    segment_remaining = max(segment.amount_required - segment.total_paid, Decimal("0.00"))
    if segment_remaining <= 0:
        return None, JsonResponse({"success": False, "error": "Segment plan already completed."}, status=400)
    if segment_amount <= 0:
        return None, JsonResponse({"success": False, "error": "Segment amount must be greater than 0."}, status=400)
    if segment_amount > segment_remaining:
        return None, JsonResponse({"success": False, "error": "Segment amount exceeds remaining balance."}, status=400)

    student = payment.student
    first_name, last_name = _split_student_name(student)
    phone_number = _student_phone_number(student)
    email = (student.user.email or "").strip()
    if method == PaymentSegmentTransaction.METHOD_BILLPAY and not email:
        return None, JsonResponse({"success": False, "error": "Student email is required to generate pay number."}, status=400)

    order_id = _unique_order_reference(f"segment-{method}", payment.id)
    idempotency_key = order_id
    webhook_url = _resolve_webhook_url(request)
    client = SnippePaymentClient()

    if method == PaymentSegmentTransaction.METHOD_MOBILE:
        response = client.create_mobile_payment(
            amount=int(segment_amount),
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            order_id=order_id,
            currency="TZS",
            webhook_url=webhook_url,
            idempotency_key=idempotency_key,
        )
    else:
        redirect_url = request.build_absolute_uri(reverse("student_profile"))
        response = client.create_dynamic_qr_payment(
            amount=int(segment_amount),
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            order_id=order_id,
            redirect_url=redirect_url,
            cancel_url=redirect_url,
            currency="TZS",
            webhook_url=webhook_url,
            idempotency_key=idempotency_key,
        )

    data = _extract_snippe_data(response)
    status = _normalize_gateway_status(data.get("status") or response.get("status") or "")
    transaction = PaymentSegmentTransaction.objects.create(
        payment_segment=segment,
        method=method,
        order_id=order_id,
        amount=segment_amount,
        phone_number=phone_number or "",
        bill_pay_number=data.get("bill_pay_number") or data.get("payment_token") or "",
        payment_token=data.get("payment_token") or "",
        snippe_reference=data.get("reference") or "",
        tx_status=status,
        raw_response=response,
    )

    segment.segment_amount = segment_amount
    segment.save(update_fields=["segment_amount", "updated_at"])
    _sync_payment_segment_status(segment)

    return transaction, None


@accountant_role_required
def manage_online_payments(request):
    creator = request.creator
    teacher_classes = TeacherClass.objects.filter(user=creator).select_related(
        "ClassName", "academicclassyear"
    )

    selected_class_id = request.GET.get("class_id")
    selected_fee_id = request.GET.get("fee_id")
    search_query = request.GET.get("search", "").strip()

    selected_class = None
    fees = Fee.objects.none()
    students = []
    summary = {
        "completed_billpay_amount": Decimal("0.00"),
        "completed_push_amount": Decimal("0.00"),
        "completed_count": 0,
        "pending_count": 0,
    }

    if selected_class_id:
        selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=creator)
        fees = Fee.objects.filter(teacherclass=selected_class).order_by("fee_name")

        if selected_fee_id:
            selected_fee = get_object_or_404(Fee, id=selected_fee_id, teacherclass=selected_class)
            assignments = StudentFee.objects.filter(
                teacherclass=selected_class,
                fee=selected_fee,
            ).select_related("student")
            if search_query:
                assignments = assignments.filter(
                    Q(student__fullName__icontains=search_query)
                    | Q(student__indexNumber__icontains=search_query)
                )
            payments = StudentPayment.objects.filter(
                teacherclass=selected_class,
                fee=selected_fee,
                student__in=assignments.values("student_id"),
            ).select_related("student")
            payment_map = {payment.student_id: payment for payment in payments}
            gateway_by_token = _fetch_gateway_payments_by_token(limit=200)
            completed_statuses = [PaymentTransaction.TX_COMPLETED, PaymentTransaction.TX_SUCCESS]
            payment_ids = payments.values_list("id", flat=True)
            summary["completed_billpay_amount"] = (
                PaymentTransaction.objects.filter(
                    payment_id__in=payment_ids,
                    method=PaymentTransaction.METHOD_BILLPAY,
                    tx_status__in=completed_statuses,
                ).aggregate(total=Sum("amount"))["total"]
                or Decimal("0.00")
            )
            summary["completed_push_amount"] = (
                PaymentTransaction.objects.filter(
                    payment_id__in=payment_ids,
                    method=PaymentTransaction.METHOD_MOBILE,
                    tx_status__in=completed_statuses,
                ).aggregate(total=Sum("amount"))["total"]
                or Decimal("0.00")
            )
            summary["completed_count"] = payments.filter(status=StudentPayment.STATUS_PAID).count()
            summary["pending_count"] = payments.exclude(status=StudentPayment.STATUS_PAID).count()

            for assignment in assignments:
                student = assignment.student
                payment = payment_map.get(student.id)
                tracking = _resolve_payment_tracking(payment, gateway_by_token)
                latest_billpay = tracking["latest_billpay"]

                students.append(
                    {
                        "student_id": student.id,
                        "student_name": student.fullName or student.user.username,
                        "admission_no": student.indexNumber or "-",
                        "phone_number": _student_phone_number(student) or "-",
                        "amount_paid": payment.amount_paid if payment else Decimal("0.00"),
                        "payment_status": tracking["payment_status"],
                        "request_status": tracking["request_status"],
                        "transaction_status": tracking["transaction_status"],
                        "transaction_completed_at": tracking["transaction_completed_at"],
                        "bill_pay_number": (
                            (latest_billpay.bill_pay_number or latest_billpay.payment_token)
                            if latest_billpay
                            else ""
                        ),
                        "payment_token": latest_billpay.payment_token if latest_billpay else "",
                        "notify_student_account": payment.notify_student_account if payment else False,
                    }
                )

    context = {
        "teacher_classes": teacher_classes,
        "fees": fees,
        "students": students,
        "selected_class_id": int(selected_class_id) if selected_class_id else None,
        "selected_fee_id": int(selected_fee_id) if selected_fee_id else None,
        "search_query": search_query,
        "summary": summary,
        "active_tab": "accountant",
    }
    return render(request, "accountant/manage_online_payment.html", context)

@accountant_role_required
def get_reports(request):
    creator = request.creator
    teacher_classes = TeacherClass.objects.filter(user=creator).select_related(
        "ClassName", "academicclassyear"
    )
    selected_class_id = request.GET.get("class_id")
    selected_fee_id = request.GET.get("fee_id")

    fees = Fee.objects.none()
    if selected_class_id:
        teacherclass = get_object_or_404(TeacherClass, id=selected_class_id, user=creator)
        fees = Fee.objects.filter(teacherclass=teacherclass).order_by("fee_name")

    context = {
        "teacher_classes": teacher_classes,
        "fees": fees,
        "selected_class_id": int(selected_class_id) if selected_class_id else None,
        "selected_fee_id": int(selected_fee_id) if selected_fee_id else None,
        "active_tab": "accountant",
    }
    return render(request, "accountant/get_reports.html", context)


@accountant_role_required
def create_payment(request):
    creator = request.creator
    if request.method == "POST":
        payment_option = request.POST.get("payment_option")
        payment_name = request.POST.get("payment_name", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        email = request.POST.get("email", "").strip()
        description = request.POST.get("description", "").strip() or "Payment description"
        success_message = request.POST.get("success_message", "").strip()
        amount_raw = request.POST.get("amount", "").strip()
        webhook_url_input = request.POST.get("webhook_url", "").strip()

        try:
            amount = Decimal(amount_raw)
        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid amount.")
            return redirect("finance:create_payment")

        if amount <= 0:
            messages.error(request, "Amount must be greater than 0.")
            return redirect("finance:create_payment")

        if payment_option not in {"mobile_payment", "payment_token"}:
            messages.error(request, "Select a valid payment option.")
            return redirect("finance:create_payment")

        if not email:
            messages.error(request, "Email is required to create payment.")
            return redirect("finance:create_payment")

        if payment_option == "mobile_payment" and not phone_number:
            messages.error(request, "Phone number is required for mobile payments.")
            return redirect("finance:create_payment")

        order_id = _unique_order_reference("create", uuid.uuid4().hex[:6])
        try:
            webhook_url = _resolve_webhook_url(request, webhook_url_input)
        except ValidationError as exc:
            messages.error(request, str(exc) or "Webhook URL must be a valid URL.")
            return redirect("finance:create_payment")
        payment = CreatePayment.objects.create(
            user=request.user,
            payment_option=payment_option,
            payment_name=payment_name,
            amount=amount,
            currency="TZS",
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            description=description,
            success_message=success_message,
            order_id=order_id,
            notification_sent=False,
        )

        first_name, last_name = _split_full_name(full_name)
        client = SnippePaymentClient()
        response = {}

        if payment_option == "mobile_payment":
            response = client.create_mobile_payment(
                amount=int(amount),
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                order_id=order_id,
                currency="TZS",
                webhook_url=webhook_url,
                idempotency_key=order_id,
            )
        else:
            response = client.create_dynamic_qr_payment(
                amount=int(amount),
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                order_id=order_id,
                currency="TZS",
                webhook_url=webhook_url,
                idempotency_key=order_id,
            )

        if not response.get("success"):
            payment.payment_status = CreatePayment.STATUS_FAILED
            payment.save(update_fields=["payment_status", "updated_at"])
            error_msg = response.get("error") or response.get("data") or "Payment request failed."
            messages.error(request, f"Payment request failed: {error_msg}")
            return redirect("finance:create_payment")

        data = _extract_snippe_data(response)
        payment_token = (
            data.get("payment_token")
            or data.get("token")
            or data.get("bill_pay_number")
            or data.get("control_number")
            or ""
        )
        payment.payment_token = payment_token
        gateway_status = _normalize_gateway_status(data.get("status"))
        if gateway_status == PaymentTransaction.TX_COMPLETED:
            payment.payment_status = CreatePayment.STATUS_COMPLETED
        elif gateway_status == PaymentTransaction.TX_FAILED:
            payment.payment_status = CreatePayment.STATUS_FAILED
        else:
            payment.payment_status = CreatePayment.STATUS_PENDING
        payment.save(update_fields=["payment_token", "payment_status", "updated_at"])

        if payment_option == "mobile_payment":
            messages.success(request, "Payment push sent to the phone successfully.")
        else:
            messages.success(request, "Payment token generated successfully.")

        return redirect("finance:create_payment")

    payments = CreatePayment.objects.filter(user=request.user).order_by("-created_at")
    payment_option_filter = request.GET.get("payment_option", "").strip()
    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()

    if payment_option_filter:
        payments = payments.filter(payment_option=payment_option_filter)

    if date_from:
        try:
            payments = payments.filter(created_at__date__gte=datetime.strptime(date_from, "%Y-%m-%d").date())
        except ValueError:
            pass
    if date_to:
        try:
            payments = payments.filter(created_at__date__lte=datetime.strptime(date_to, "%Y-%m-%d").date())
        except ValueError:
            pass

    gateway_by_order = _fetch_gateway_payments_by_order_id(limit=200)
    payment_rows = []
    totals = {
        "all": Decimal("0.00"),
        "payment_token": Decimal("0.00"),
        "mobile_payment": Decimal("0.00"),
    }

    for payment in payments:
        gateway_data = gateway_by_order.get(payment.order_id) or {}
        gateway_status = _normalize_gateway_status(gateway_data.get("status"))
        status_value = payment.payment_status or CreatePayment.STATUS_PENDING
        if gateway_status == PaymentTransaction.TX_COMPLETED:
            status_value = CreatePayment.STATUS_COMPLETED
        elif gateway_status == PaymentTransaction.TX_FAILED:
            status_value = CreatePayment.STATUS_FAILED

        if status_value != payment.payment_status:
            payment.payment_status = status_value
            payment.save(update_fields=["payment_status", "updated_at"])

        if status_value in {CreatePayment.STATUS_COMPLETED, CreatePayment.STATUS_FAILED}:
            _notify_create_payment_status(payment, status_value)

        if status_value == CreatePayment.STATUS_COMPLETED:
            totals["all"] += payment.amount or Decimal("0.00")
            option_key = payment.payment_option or "payment_token"
            totals[option_key] += payment.amount or Decimal("0.00")

        payment_rows.append(
            {
                "payment": payment,
                "status": status_value,
                "gateway_reference": gateway_data.get("reference") or "-",
                "payment_token": gateway_data.get("payment_token") or payment.payment_token or "-",
            }
        )

    context = {
        "payments": payment_rows,
        "filters": {
            "payment_option": payment_option_filter,
            "from": date_from,
            "to": date_to,
        },
        "totals": totals,
        "active_tab": "accountant",
    }
    return render(request, "accountant/create_payment.html", context)


@accountant_role_required
def create_payment_statuses(request):
    order_ids_param = request.GET.get("order_ids", "")
    order_ids = [value for value in (order_ids_param.split(",") if order_ids_param else []) if value]
    if not order_ids:
        return JsonResponse({"payments": {}})

    payments = CreatePayment.objects.filter(user=request.user, order_id__in=order_ids)
    payload = {
        payment.order_id: {
            "status": payment.payment_status,
            "payment_token": payment.payment_token,
            "updated_at": payment.updated_at.isoformat() if payment.updated_at else None,
        }
        for payment in payments
    }
    return JsonResponse({"payments": payload})


@accountant_role_required
@require_POST
def refresh_create_payment_token(request, payment_id):
    payment = get_object_or_404(CreatePayment, id=payment_id, user=request.user)
    if payment.payment_option != "payment_token":
        messages.error(request, "Only payment token records can be refreshed.")
        return redirect("finance:create_payment")

    if not payment.email:
        messages.error(request, "Email is required to refresh the payment token.")
        return redirect("finance:create_payment")

    order_id = _unique_order_reference("create", payment.id)
    first_name, last_name = _split_full_name(payment.full_name)
    webhook_url = _resolve_webhook_url(request)
    client = SnippePaymentClient()
    response = client.create_dynamic_qr_payment(
        amount=int(payment.amount or 0),
        phone_number=payment.phone_number or "",
        first_name=first_name,
        last_name=last_name,
        email=payment.email,
        order_id=order_id,
        currency=payment.currency or "TZS",
        webhook_url=webhook_url,
        idempotency_key=order_id,
    )

    if not response.get("success"):
        error_msg = response.get("error") or response.get("data") or "Payment token refresh failed."
        messages.error(request, f"Payment token refresh failed: {error_msg}")
        return redirect("finance:create_payment")

    data = _extract_snippe_data(response)
    payment_token = (
        data.get("payment_token")
        or data.get("token")
        or data.get("bill_pay_number")
        or data.get("control_number")
        or ""
    )
    payment.order_id = order_id
    payment.payment_token = payment_token
    payment.payment_status = CreatePayment.STATUS_PENDING
    payment.notification_sent = False
    payment.save(update_fields=["order_id", "payment_token", "payment_status", "notification_sent", "updated_at"])
    messages.success(request, "Payment token refreshed successfully.")
    return redirect("finance:create_payment")


@accountant_role_required
def communication_logs(request):
    creator = request.creator
    status_filter = request.GET.get("status", "sent").strip().lower()
    channel_filter = request.GET.get("channel", "").strip().lower()

    queryset = StudentCommunicationLog.objects.filter(
        user=creator,
        channel__in=["sms", "email"],
    ).order_by("-created_at")

    if status_filter in {"sent", "failed", "pending"}:
        queryset = queryset.filter(status=status_filter)
    if channel_filter in {"sms", "email"}:
        queryset = queryset.filter(channel=channel_filter)

    context = {
        "logs": queryset,
        "filters": {
            "status": status_filter,
            "channel": channel_filter,
        },
    }
    return render(request, "accountant/communication_logs.html", context)


@accountant_role_required
@require_http_methods(["GET"])
def fees_for_class(request, class_id):
    creator = request.creator
    teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator)
    fees = Fee.objects.filter(teacherclass=teacherclass).values("id", "fee_name")
    return JsonResponse({"success": True, "fees": list(fees)})


@accountant_role_required
@require_http_methods(["GET"])
def students_for_fee(request, class_id, fee_id):
    creator = request.creator
    teacherclass = get_object_or_404(TeacherClass, id=class_id, user=creator)
    fee = get_object_or_404(Fee, id=fee_id, teacherclass=teacherclass)
    search_query = request.GET.get("search", "").strip()
    assignments = StudentFee.objects.filter(
        teacherclass=teacherclass, fee=fee
    ).select_related("student")
    if search_query:
        assignments = assignments.filter(
            Q(student__fullName__icontains=search_query)
            | Q(student__indexNumber__icontains=search_query)
        )
    payments = StudentPayment.objects.filter(
        teacherclass=teacherclass, fee=fee, student__in=assignments.values("student_id")
    ).select_related("student")
    payment_map = {payment.student_id: payment for payment in payments}
    gateway_by_token = _fetch_gateway_payments_by_token(limit=200)

    rows = []
    for assignment in assignments:
        student = assignment.student
        payment = payment_map.get(student.id)
        tracking = _resolve_payment_tracking(payment, gateway_by_token)
        latest_billpay = tracking["latest_billpay"]
        rows.append(
            {
                "student_id": student.id,
                "student_name": student.fullName or student.user.username,
                "admission_no": student.indexNumber or "",
                "phone_number": _student_phone_number(student),
                "payment_status": tracking["payment_status"],
                "request_status": tracking["request_status"],
                "transaction_status": tracking["transaction_status"],
                "transaction_completed_at": tracking["transaction_completed_at"],
                "bill_pay_number": (latest_billpay.bill_pay_number or latest_billpay.payment_token) if latest_billpay else "",
                "payment_token": latest_billpay.payment_token if latest_billpay else "",
                "notify_student_account": payment.notify_student_account if payment else False,
                "payment_id": payment.id if payment else None,
                "amount_due": str(payment.amount_due if payment else assignment.amount_required or 0),
                "amount_paid": str(payment.amount_paid if payment else 0),
            }
        )
    return JsonResponse({"success": True, "students": rows})


from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST



@accountant_role_required
@require_POST
def generate_billpay_number(request):
    creator = request.creator
    data = _parse_request_data(request)

    student_id = data.get("student_id")
    fee_id = data.get("fee_id")
    class_id = data.get("class_id")

    if not (student_id and fee_id and class_id):
        if _is_ajax_or_json_request(request):
            return JsonResponse({"success": False, "error": "Missing parameters."}, status=400)
        messages.error(request, "Missing parameters.")
        return _manage_online_payment_redirect(class_id, fee_id)

    teacherclass, fee, student, payment, error = _get_payment_context(
        request, creator, student_id, fee_id, class_id
    )
    if error:
        return error

    order_id = _unique_order_reference("billpay", payment.id)
    idempotency_key = order_id

    first_name, last_name = _split_student_name(student)
    phone_number = _student_phone_number(student)

    # ✅ Snippe requires customer.email
    email = (getattr(student.user, "email", "") or "").strip()
    if not email:
        error_msg = "Student email is required to generate a billpay number (Snippe requirement). Please add email to the student account."
        if _is_ajax_or_json_request(request):
            return JsonResponse(
                {
                    "success": False,
                    "error": error_msg,
                },
                status=400,
            )
        messages.error(request, error_msg)
        return _manage_online_payment_redirect(class_id, fee_id)

    amount = int(payment.amount_due or 0)
    if amount <= 0:
        if _is_ajax_or_json_request(request):
            return JsonResponse(
                {"success": False, "error": "Invalid amount. Amount due must be greater than 0."},
                status=400,
            )
        messages.error(request, "Invalid amount. Amount due must be greater than 0.")
        return _manage_online_payment_redirect(class_id, fee_id)

    client = SnippePaymentClient()

    redirect_url = request.build_absolute_uri(reverse("finance:manage_online_payment"))
    cancel_url = request.build_absolute_uri(reverse("finance:manage_online_payment"))
    webhook_url = _resolve_webhook_url(request)

    response = client.create_dynamic_qr_payment(
        amount=amount,
        phone_number=phone_number,
        first_name=first_name,
        last_name=last_name,
        email=email,
        order_id=order_id,
        redirect_url=redirect_url,
        cancel_url=cancel_url,
        currency="TZS",
        webhook_url=webhook_url,
        idempotency_key=idempotency_key,
    )

    # Debug (keep or remove later)
    print("SNIPPE RESPONSE:", response)

    # ✅ If Snippe failed, return error and DO NOT create transaction
    if not response.get("success"):
        msg = None
        data = response.get("data") or {}
        if isinstance(data, dict):
            msg = data.get("message")
        error_msg = msg or response.get("error") or data or "Snippe payment request failed."
        if _is_ajax_or_json_request(request):
            return JsonResponse(
            {
                "success": False,
                "error": error_msg,
                "snippe": data,
            },
            status=400,
        )
        messages.error(request, f"Snippe error: {error_msg}")
        return _manage_online_payment_redirect(class_id, fee_id)

    # ✅ Only build transaction on success
    transaction = _build_transaction(
        payment,
        PaymentTransaction.METHOD_BILLPAY,
        payment.amount_due,
        phone_number,
        order_id,
        idempotency_key,
        response,
    )

    if _is_ajax_or_json_request(request):
        return JsonResponse(
        {
            "success": True,
            "bill_pay_number": transaction.payment_token,
            "payment_token": transaction.payment_token,
            "tx_status": transaction.tx_status,
            "message": "Bill pay number generated.",
        }
        )

    messages.success(request, f"Bill pay number generated. Payment token: {transaction.payment_token}")
    return _manage_online_payment_redirect(class_id, fee_id)



@accountant_role_required
@require_POST
def generate_billpay_numbers_bulk(request):
    creator = request.creator
    data = _parse_request_data(request)

    class_id = data.get("class_id")
    fee_id = data.get("fee_id")
    student_ids = data.get("student_ids") or []

    if not (class_id and fee_id and isinstance(student_ids, list) and student_ids):
        return JsonResponse(
            {"success": False, "error": "Class, fee and selected students are required."},
            status=400,
        )

    generated = []
    failed = []

    for student_id in student_ids:
        teacherclass, fee, student, payment, error = _get_payment_context(
            request, creator, student_id, fee_id, class_id
        )
        if error:
            failed.append({"student_id": student_id, "error": "Student fee assignment not found."})
            continue

        first_name, last_name = _split_student_name(student)
        phone_number = _student_phone_number(student)
        email = (getattr(student.user, "email", "") or "").strip()

        if not email:
            failed.append(
                {
                    "student_id": student_id,
                    "student_name": student.fullName or student.user.username,
                    "error": "Student email is required to generate token.",
                }
            )
            continue

        amount = int(payment.amount_due or 0)
        if amount <= 0:
            failed.append(
                {
                    "student_id": student_id,
                    "student_name": student.fullName or student.user.username,
                    "error": "Amount due must be greater than 0.",
                }
            )
            continue

        order_id = _unique_order_reference("billpay", payment.id)
        idempotency_key = order_id
        client = SnippePaymentClient()

        redirect_url = request.build_absolute_uri(reverse("finance:manage_online_payment"))
        cancel_url = request.build_absolute_uri(reverse("finance:manage_online_payment"))
        webhook_url = _resolve_webhook_url(request)

        response = client.create_dynamic_qr_payment(
            amount=amount,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            order_id=order_id,
            redirect_url=redirect_url,
            cancel_url=cancel_url,
            currency="TZS",
            webhook_url=webhook_url,
            idempotency_key=idempotency_key,
        )

        if not response.get("success"):
            response_data = response.get("data") or {}
            error_msg = (
                response_data.get("message")
                if isinstance(response_data, dict)
                else str(response_data)
            ) or response.get("error") or "Snippe payment request failed."
            failed.append(
                {
                    "student_id": student_id,
                    "student_name": student.fullName or student.user.username,
                    "error": error_msg,
                }
            )
            continue

        transaction = _build_transaction(
            payment,
            PaymentTransaction.METHOD_BILLPAY,
            payment.amount_due,
            phone_number,
            order_id,
            idempotency_key,
            response,
        )
        generated.append(
            {
                "student_id": student_id,
                "student_name": student.fullName or student.user.username,
                "payment_token": transaction.payment_token,
                "tx_status": transaction.tx_status,
            }
        )

    message = f"Generated payment token for {len(generated)} student(s)."
    if failed:
        message += f" {len(failed)} failed."

    return JsonResponse(
        {
            "success": bool(generated),
            "message": message,
            "generated": generated,
            "failed": failed,
        },
        status=200 if generated else 400,
    )


@accountant_role_required
@require_POST
def refresh_billpay_number(request):
    return generate_billpay_number(request)


@accountant_role_required
@require_POST
def delete_billpay_number(request):
    creator = request.creator
    data = _parse_request_data(request)
    student_id = data.get("student_id")
    fee_id = data.get("fee_id")
    class_id = data.get("class_id")
    if not (student_id and fee_id and class_id):
        if _is_ajax_or_json_request(request):
            return JsonResponse({"success": False, "error": "Missing parameters."}, status=400)
        messages.error(request, "Missing parameters.")
        return _manage_online_payment_redirect(class_id, fee_id)

    _, _, _, payment, error = _get_payment_context(
        request, creator, student_id, fee_id, class_id
    )
    if error:
        return error

    latest = payment.transactions.filter(
        method=PaymentTransaction.METHOD_BILLPAY
    ).order_by("-created_at").first()
    if not latest:
        if _is_ajax_or_json_request(request):
            return JsonResponse({"success": False, "error": "No bill pay number to delete."}, status=404)
        messages.error(request, "No bill pay number to delete.")
        return _manage_online_payment_redirect(class_id, fee_id)
    latest.delete()
    if _is_ajax_or_json_request(request):
        return JsonResponse({"success": True, "message": "Bill pay number deleted."})
    messages.success(request, "Bill pay number deleted.")
    return _manage_online_payment_redirect(class_id, fee_id)


@accountant_role_required
@require_POST
def toggle_notify_student_account(request):
    creator = request.creator
    data = _parse_request_data(request)
    student_id = data.get("student_id")
    fee_id = data.get("fee_id")
    class_id = data.get("class_id")
    notify = data.get("notify")
    if not (student_id and fee_id and class_id):
        if _is_ajax_or_json_request(request):
            return JsonResponse({"success": False, "error": "Missing parameters."}, status=400)
        messages.error(request, "Missing parameters.")
        return _manage_online_payment_redirect(class_id, fee_id)
    notify_flag = str(notify).lower() == "true"

    _, _, _, payment, error = _get_payment_context(
        request, creator, student_id, fee_id, class_id
    )
    if error:
        return error

    payment.notify_student_account = notify_flag
    payment.save(update_fields=["notify_student_account", "updated_at"])
    if _is_ajax_or_json_request(request):
        return JsonResponse({"success": True, "notify_student_account": payment.notify_student_account})
    messages.success(request, "Notification preference updated.")
    return _manage_online_payment_redirect(class_id, fee_id)


@accountant_role_required
@require_POST
def push_mobile_payment(request):
    creator = request.creator
    data = _parse_request_data(request)
    student_id = data.get("student_id")
    fee_id = data.get("fee_id")
    class_id = data.get("class_id")
    if not (student_id and fee_id and class_id):
        if _is_ajax_or_json_request(request):
            return JsonResponse({"success": False, "error": "Missing parameters."}, status=400)
        messages.error(request, "Missing parameters.")
        return _manage_online_payment_redirect(class_id, fee_id)

    _, _, student, payment, error = _get_payment_context(
        request, creator, student_id, fee_id, class_id
    )
    if error:
        return error

    phone_number = _student_phone_number(student)
    if not phone_number:
        if _is_ajax_or_json_request(request):
            return JsonResponse({"success": False, "error": "Student phone number is missing."}, status=400)
        messages.error(request, "Student phone number is missing.")
        return _manage_online_payment_redirect(class_id, fee_id)

    amount = payment.amount_due - payment.amount_paid
    if amount <= 0:
        if _is_ajax_or_json_request(request):
            return JsonResponse({"success": False, "error": "No outstanding balance."}, status=400)
        messages.error(request, "No outstanding balance.")
        return _manage_online_payment_redirect(class_id, fee_id)

    order_id = _unique_order_reference("mobile", payment.id)
    idempotency_key = order_id

    first_name, last_name = _split_student_name(student)
    email = student.user.email or ""
    webhook_url = _resolve_webhook_url(request)
    client = SnippePaymentClient()
    response = client.create_mobile_payment(
        amount=int(amount),
        phone_number=phone_number,
        first_name=first_name,
        last_name=last_name,
        email=email,
        order_id=order_id,
        currency="TZS",
        webhook_url=webhook_url,
        idempotency_key=idempotency_key,
    )
    transaction = _build_transaction(
        payment,
        PaymentTransaction.METHOD_MOBILE,
        amount,
        phone_number,
        order_id,
        idempotency_key,
        response,
    )
    message = (
        "Check your phone to approve payment"
        if transaction.tx_status == PaymentTransaction.TX_PENDING
        else "Payment request sent."
    )
    if _is_ajax_or_json_request(request):
        return JsonResponse(
            {
                "success": response.get("success", False),
                "tx_status": transaction.tx_status,
                "message": message,
            }
        )

    if response.get("success", False):
        messages.success(request, message)
    else:
        messages.error(request, message)
    return _manage_online_payment_redirect(class_id, fee_id)


@login_required
@require_POST
def student_push_payment(request):
    if not request.user.is_student:
        return JsonResponse({"success": False, "error": "Unauthorized."}, status=403)

    data = _parse_request_data(request)
    payment_id = data.get("payment_id")
    if not payment_id:
        return JsonResponse({"success": False, "error": "Missing payment."}, status=400)

    payment = get_object_or_404(
        StudentPayment.objects.select_related("student", "fee", "teacherclass"),
        id=payment_id,
        student__user=request.user,
    )
    student = payment.student
    phone_number = _student_phone_number(student)
    if not phone_number:
        return JsonResponse({"success": False, "error": "Phone number is missing."}, status=400)

    amount = payment.amount_due - payment.amount_paid
    if amount <= 0:
        return JsonResponse({"success": False, "error": "No outstanding balance."}, status=400)

    order_id = _unique_order_reference("mobile", payment.id)
    idempotency_key = order_id
    first_name, last_name = _split_student_name(student)
    email = student.user.email or ""
    webhook_url = _resolve_webhook_url(request)

    client = SnippePaymentClient()
    response = client.create_mobile_payment(
        amount=int(amount),
        phone_number=phone_number,
        first_name=first_name,
        last_name=last_name,
        email=email,
        order_id=order_id,
        currency="TZS",
        webhook_url=webhook_url,
        idempotency_key=idempotency_key,
    )
    transaction = _build_transaction(
        payment,
        PaymentTransaction.METHOD_MOBILE,
        amount,
        phone_number,
        order_id,
        idempotency_key,
        response,
    )
    return JsonResponse(
        {
            "success": response.get("success", False),
            "tx_status": transaction.tx_status,
            "message": "Check your phone to approve payment"
            if transaction.tx_status == PaymentTransaction.TX_PENDING
            else "Payment request sent.",
        }
    )


@login_required
@require_POST
def student_generate_payment_token(request):
    if not request.user.is_student:
        return JsonResponse({"success": False, "error": "Unauthorized."}, status=403)

    data = _parse_request_data(request)
    payment_id = data.get("payment_id")
    if not payment_id:
        return JsonResponse({"success": False, "error": "Missing payment."}, status=400)

    payment = get_object_or_404(
        StudentPayment.objects.select_related("student", "fee", "teacherclass"),
        id=payment_id,
        student__user=request.user,
    )
    student = payment.student
    phone_number = _student_phone_number(student)
    first_name, last_name = _split_student_name(student)
    email = (student.user.email or "").strip()
    if not email:
        return JsonResponse({"success": False, "error": "Email is required to generate payment token."}, status=400)

    amount = payment.amount_due - payment.amount_paid
    if amount <= 0:
        return JsonResponse({"success": False, "error": "No outstanding balance."}, status=400)

    order_id = _unique_order_reference("student-billpay", payment.id)
    idempotency_key = order_id
    webhook_url = _resolve_webhook_url(request)
    redirect_url = request.build_absolute_uri(reverse("student_profile"))

    client = SnippePaymentClient()
    response = client.create_dynamic_qr_payment(
        amount=int(amount),
        phone_number=phone_number,
        first_name=first_name,
        last_name=last_name,
        email=email,
        order_id=order_id,
        redirect_url=redirect_url,
        cancel_url=redirect_url,
        currency="TZS",
        webhook_url=webhook_url,
        idempotency_key=idempotency_key,
    )

    if not response.get("success", False):
        data_response = response.get("data") or {}
        error_msg = (
            data_response.get("message")
            if isinstance(data_response, dict)
            else str(data_response)
        ) or response.get("error") or "Unable to generate payment token."
        return JsonResponse({"success": False, "error": error_msg}, status=400)

    transaction = _build_transaction(
        payment,
        PaymentTransaction.METHOD_BILLPAY,
        amount,
        phone_number,
        order_id,
        idempotency_key,
        response,
    )

    return JsonResponse(
        {
            "success": True,
            "tx_status": transaction.tx_status,
            "payment_token": transaction.payment_token or transaction.bill_pay_number,
            "message": "Payment token generated successfully.",
        }
    )




@login_required
@require_POST
def student_generate_segment_billpay(request):
    if not request.user.is_student:
        return JsonResponse({"success": False, "error": "Unauthorized."}, status=403)

    data = _parse_request_data(request)
    payment_id = data.get("payment_id")
    segment_amount_raw = data.get("segment_amount")
    if not payment_id:
        return JsonResponse({"success": False, "error": "Missing payment."}, status=400)
    try:
        segment_amount = Decimal(str(segment_amount_raw or "0"))
    except InvalidOperation:
        return JsonResponse({"success": False, "error": "Invalid segment amount."}, status=400)

    payment = get_object_or_404(
        StudentPayment.objects.select_related("student", "fee", "teacherclass"),
        id=payment_id,
        student__user=request.user,
    )

    transaction, error_response = _create_segment_transaction(
        request,
        payment,
        segment_amount,
        PaymentSegmentTransaction.METHOD_BILLPAY,
    )
    if error_response:
        return error_response

    return JsonResponse(
        {
            "success": True,
            "message": "Bill pay number generated successfully.",
            "payment_token": transaction.payment_token or transaction.bill_pay_number,
            "tx_status": transaction.tx_status,
        }
    )


@login_required
@require_POST
def student_push_segment_payment(request):
    if not request.user.is_student:
        return JsonResponse({"success": False, "error": "Unauthorized."}, status=403)

    data = _parse_request_data(request)
    payment_id = data.get("payment_id")
    segment_amount_raw = data.get("segment_amount")
    if not payment_id:
        return JsonResponse({"success": False, "error": "Missing payment."}, status=400)
    try:
        segment_amount = Decimal(str(segment_amount_raw or "0"))
    except InvalidOperation:
        return JsonResponse({"success": False, "error": "Invalid segment amount."}, status=400)

    payment = get_object_or_404(
        StudentPayment.objects.select_related("student", "fee", "teacherclass"),
        id=payment_id,
        student__user=request.user,
    )

    transaction, error_response = _create_segment_transaction(
        request,
        payment,
        segment_amount,
        PaymentSegmentTransaction.METHOD_MOBILE,
    )
    if error_response:
        return error_response

    return JsonResponse(
        {
            "success": True,
            "message": "Check your phone to approve payment."
            if transaction.tx_status == PaymentSegmentTransaction.TX_PENDING
            else "Payment request sent.",
            "tx_status": transaction.tx_status,
        }
    )


def _payment_segments_monitor_data(request, creator):
    teacher_classes = TeacherClass.objects.filter(user=creator).select_related("ClassName", "academicclassyear")

    selected_class_id = request.GET.get("class_id")
    selected_fee_id = request.GET.get("fee_id")
    search = request.GET.get("search", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    date_from_parsed = None
    date_to_parsed = None
    if date_from:
        try:
            date_from_parsed = timezone.datetime.strptime(date_from, "%Y-%m-%d").date()
        except ValueError:
            date_from = ""
    if date_to:
        try:
            date_to_parsed = timezone.datetime.strptime(date_to, "%Y-%m-%d").date()
        except ValueError:
            date_to = ""

    selected_class = None
    selected_fee = None
    fees = Fee.objects.none()
    students = []
    summary = {
        "total_paid": Decimal("0.00"),
        "total_required": Decimal("0.00"),
        "total_balance": Decimal("0.00"),
    }

    if selected_class_id:
        selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=creator)
        fees = Fee.objects.filter(teacherclass=selected_class).order_by("fee_name")

        if fees.exists() and not selected_fee_id:
            selected_fee = fees.first()
            selected_fee_id = str(selected_fee.id)

        if selected_fee_id:
            selected_fee = get_object_or_404(Fee, id=selected_fee_id, teacherclass=selected_class)
            assignments = StudentFee.objects.filter(teacherclass=selected_class, fee=selected_fee).select_related("student", "student__user")
            if search:
                assignments = assignments.filter(
                    Q(student__fullName__icontains=search)
                    | Q(student__indexNumber__icontains=search)
                    | Q(student__user__username__icontains=search)
                )

            segment_map = {
                (seg.student_id, seg.fee_name_id, seg.teacherclass_id): seg
                for seg in PaymentSegment.objects.filter(
                    teacherclass=selected_class,
                    fee_name=selected_fee,
                    student_id__in=assignments.values_list("student_id", flat=True),
                ).prefetch_related("transactions")
            }

            for assignment in assignments:
                key = (assignment.student_id, selected_fee.id, selected_class.id)
                segment = segment_map.get(key)
                required_amount = assignment.amount_required or Decimal("0.00")
                payment_amounts = []
                payment_times = []
                payment_entries = []

                if segment:
                    _sync_payment_segment_status(segment)
                    paid_amount = segment.total_paid
                    remaining = max(segment.amount_required - segment.total_paid, Decimal("0.00"))
                    payments_qs = segment.transactions.filter(
                        tx_status__in=[PaymentSegmentTransaction.TX_COMPLETED, PaymentSegmentTransaction.TX_SUCCESS]
                    ).order_by("created_at")
                    if date_from_parsed:
                        payments_qs = payments_qs.filter(created_at__date__gte=date_from_parsed)
                    if date_to_parsed:
                        payments_qs = payments_qs.filter(created_at__date__lte=date_to_parsed)
                    payments = list(payments_qs)
                    payment_amounts = [tx.amount for tx in payments]
                    payment_times = [tx.created_at for tx in payments]
                    payment_entries = [{"amount": tx.amount, "time": tx.created_at} for tx in payments]
                    if (date_from_parsed or date_to_parsed) and not payments:
                        continue
                else:
                    paid_amount = Decimal("0.00")
                    remaining = required_amount
                    if date_from_parsed or date_to_parsed:
                        continue

                summary["total_paid"] += paid_amount
                summary["total_required"] += required_amount
                summary["total_balance"] += remaining

                students.append(
                    {
                        "student": assignment.student,
                        "required_amount": required_amount,
                        "paid_amount": paid_amount,
                        "remaining_amount": remaining,
                        "status": segment.status if segment else "pending",
                        "payment_amounts": payment_amounts,
                        "payment_times": payment_times,
                        "payment_entries": payment_entries,
                    }
                )

    return {
        "teacher_classes": teacher_classes,
        "fees": fees,
        "students": students,
        "selected_class_id": int(selected_class_id) if selected_class_id else None,
        "selected_fee_id": int(selected_fee_id) if selected_fee_id else None,
        "summary": summary,
        "search": search,
        "date_from": date_from,
        "date_to": date_to,
    }


@accountant_role_required
def payment_segments_monitor(request):
    context = _payment_segments_monitor_data(request, request.creator)
    return render(request, "accountant/payment_segments_monitor.html", context)


@accountant_role_required
def payment_segments_monitor_pdf(request):
    context = _payment_segments_monitor_data(request, request.creator)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="payment_segments_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Payment Segments Report", ParagraphStyle("Title", parent=styles["Heading1"], alignment=1)),
        Spacer(1, 0.3 * cm),
        Paragraph(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles["BodyText"]),
        Paragraph(f"Search: {context.get('search') or 'All'}", styles["BodyText"]),
        Paragraph(f"Date range: {context.get('date_from') or '-'} to {context.get('date_to') or '-'}", styles["BodyText"]),
        Spacer(1, 0.3 * cm),
    ]

    table_data = [["#", "Student", "Phone", "Required", "Segment Paid", "Total Paid", "Balance"]]
    for index, row in enumerate(context.get("students", []), start=1):
        segment_paid_lines = [f"{amount} ({paid_time.strftime('%Y-%m-%d %H:%M')})" for amount, paid_time in zip(row.get("payment_amounts", []), row.get("payment_times", []))]
        table_data.append([
            str(index),
            row["student"].fullName or row["student"].user.username,
            str(row["student"].contact or "-"),
            f"{row['required_amount']}",
            "\n".join(segment_paid_lines) if segment_paid_lines else "-",
            f"{row['paid_amount']}",
            f"{row['remaining_amount']}",
        ])

    if len(table_data) == 1:
        table_data.append(["-", "No data", "-", "-", "-", "-", "-"])

    table = Table(table_data, colWidths=[1 * cm, 4 * cm, 2.5 * cm, 2.3 * cm, 5 * cm, 2.3 * cm, 2.3 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a93")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3 * cm))
    summary = context.get("summary", {})
    elements.append(Paragraph(f"Total Paid: {summary.get('total_paid', Decimal('0.00'))}", styles["BodyText"]))
    elements.append(Paragraph(f"Total Required: {summary.get('total_required', Decimal('0.00'))}", styles["BodyText"]))
    elements.append(Paragraph(f"Total Balance: {summary.get('total_balance', Decimal('0.00'))}", styles["BodyText"]))

    doc.build(elements)
    return response


@accountant_role_required
def transaction_list(request):
    creator = request.creator
    queryset = PaymentTransaction.objects.select_related(
        "payment",
        "payment__student",
        "payment__fee",
        "payment__teacherclass",
        "payment__teacherclass__ClassName",
    ).filter(payment__teacherclass__user=creator)

    search = request.GET.get("search", "").strip()
    status_filter = request.GET.get("tx_status", "").strip()
    method_filter = request.GET.get("method", "").strip()
    fee_filter = request.GET.get("fee", "").strip()
    class_filter = request.GET.get("teacherclass", "").strip()
    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()

    if search:
        queryset = queryset.filter(
            Q(payment__student__fullName__icontains=search)
            | Q(payment__student__indexNumber__icontains=search)
        )
    normalized_status_filter = _normalize_status_filter_value(status_filter)
    if method_filter:
        queryset = queryset.filter(method=method_filter)
    if fee_filter:
        queryset = queryset.filter(payment__fee_id=fee_filter)
    if class_filter:
        queryset = queryset.filter(payment__teacherclass_id=class_filter)
    if date_from:
        try:
            date_from_parsed = timezone.datetime.strptime(date_from, "%Y-%m-%d")
            queryset = queryset.filter(created_at__date__gte=date_from_parsed.date())
        except ValueError:
            pass
    if date_to:
        try:
            date_to_parsed = timezone.datetime.strptime(date_to, "%Y-%m-%d")
            queryset = queryset.filter(created_at__date__lte=date_to_parsed.date())
        except ValueError:
            pass

    queryset = queryset.order_by("-created_at")

    gateway_payments_by_order_id = _fetch_gateway_payments_by_order_id(limit=200)

    transaction_rows = []
    summary = {
        "completed": 0,
        "pending": 0,
        "failed": 0,
    }
    for tx in queryset:
        gateway_data = gateway_payments_by_order_id.get(tx.order_id) or _gateway_payment_payload(tx.raw_response)

        if normalized_status_filter and not _transaction_matches_status_filter(tx, gateway_data, normalized_status_filter):
            continue
        amount_data = gateway_data.get("amount") if isinstance(gateway_data.get("amount"), dict) else {}
        channel_data = gateway_data.get("channel") if isinstance(gateway_data.get("channel"), dict) else {}
        customer_data = gateway_data.get("customer") if isinstance(gateway_data.get("customer"), dict) else {}
        settlement_data = gateway_data.get("settlement") if isinstance(gateway_data.get("settlement"), dict) else {}
        fee_data = settlement_data.get("fees") if isinstance(settlement_data.get("fees"), dict) else {}
        gross_data = settlement_data.get("gross") if isinstance(settlement_data.get("gross"), dict) else {}
        net_data = settlement_data.get("net") if isinstance(settlement_data.get("net"), dict) else {}
        metadata_data = gateway_data.get("metadata") if isinstance(gateway_data.get("metadata"), dict) else {}

        student = tx.payment.student if tx.payment else None
        normalized_row_status = _normalize_status_filter_value(gateway_data.get("status") or tx.tx_status)
        if normalized_row_status in summary:
            summary[normalized_row_status] += 1

        if (
            normalized_row_status == PaymentTransaction.TX_COMPLETED
            and not tx.notification_sent
            and student
        ):
            amount_value = amount_data.get("value") if amount_data else tx.amount
            amount_currency = amount_data.get("currency") or tx.currency
            student_name = student.fullName or student.user.username
            fee_name = tx.payment.fee.fee_name if tx.payment and tx.payment.fee else "fee payment"
            message = (
                f"Hello {student_name}, your payment of {amount_value} {amount_currency} "
                f"for {fee_name} has been completed successfully."
            )
            sms_sent = _send_sms_message(creator, _student_phone_number(student), message)
            email_sent = _send_email_message(
                creator,
                student.user.email if student.user else "",
                "Payment Completed",
                message,
                template_name="emails/payment_success.html",
                context={
                    "recipient_name": student_name,
                    "payment": {
                        "amount": amount_value,
                        "currency": amount_currency,
                        "name": fee_name,
                        "order_id": tx.order_id,
                        "method": tx.get_method_display() if hasattr(tx, "get_method_display") else tx.method,
                    },
                },
            )
            if _student_phone_number(student):
                _record_communication(
                    creator=creator,
                    student=student,
                    channel="sms",
                    recipient=_student_phone_number(student),
                    subject="Payment Completed",
                    message=message,
                    status="sent" if sms_sent else "failed",
                    metadata={"order_id": tx.order_id, "transaction_id": tx.id},
                )
            if student.user and student.user.email:
                _record_communication(
                    creator=creator,
                    student=student,
                    channel="email",
                    recipient=student.user.email,
                    subject="Payment Completed",
                    message=message,
                    status="sent" if email_sent else "failed",
                    metadata={"order_id": tx.order_id, "transaction_id": tx.id},
                )
            if sms_sent or email_sent:
                tx.notification_sent = True
                tx.save(update_fields=["notification_sent"])

        transaction_rows.append(
            {
                "tx": tx,
                "gateway_id": gateway_data.get("id") or "-",
                "gateway_object": gateway_data.get("object") or "payment",
                "api_version": gateway_data.get("api_version") or "-",
                "gateway_status": gateway_data.get("status") or tx.tx_status,
                "gateway_created_at": parse_datetime(gateway_data.get("created_at") or "") if gateway_data.get("created_at") else None,
                "gateway_completed_at": parse_datetime(gateway_data.get("completed_at") or "") if gateway_data.get("completed_at") else None,
                "channel_provider": channel_data.get("provider") or "-",
                "channel_type": channel_data.get("type") or "-",
                "payment_type": gateway_data.get("payment_type") or tx.method,
                "gateway_reference": gateway_data.get("reference") or tx.snippe_reference or "-",
                "external_reference": gateway_data.get("external_reference") or tx.order_id,
                "amount_value": amount_data.get("value") if amount_data else tx.amount,
                "amount_currency": amount_data.get("currency") or tx.currency,
                "customer_name": ((student.fullName if student and student.fullName else "") or f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip() or "-"),
                "customer_phone": (_student_phone_number(student) if student else "") or customer_data.get("phone") or tx.phone_number or "-",
                "customer_email": (student.user.email if student and student.user and student.user.email else "") or customer_data.get("email") or "-",
                "payment_token": gateway_data.get("payment_token") or tx.payment_token or tx.bill_pay_number or "-",
                "payment_url": gateway_data.get("payment_url") or tx.payment_url,
                "payment_qr_code": gateway_data.get("payment_qr_code") or tx.payment_qr_code,
                "order_id": metadata_data.get("order_id") or tx.order_id,
                "settlement_fee": fee_data.get("value") if fee_data else "-",
                "settlement_gross": gross_data.get("value") if gross_data else "-",
                "settlement_net": net_data.get("value") if net_data else "-",
                "settlement_currency": fee_data.get("currency") or gross_data.get("currency") or net_data.get("currency") or tx.currency,
            }
        )

    paginator = Paginator(transaction_rows, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    teacher_classes = TeacherClass.objects.filter(user=creator).select_related("ClassName")
    fees = Fee.objects.filter(teacherclass__user=creator)

    context = {
        "page_obj": page_obj,
        "filters": {
            "search": search,
            "tx_status": status_filter,
            "method": method_filter,
            "fee": fee_filter,
            "teacherclass": class_filter,
            "from": date_from,
            "to": date_to,
        },
        "teacher_classes": teacher_classes,
        "fees": fees,
        "status_choices": [
            (PaymentTransaction.TX_COMPLETED, "Completed"),
            (PaymentTransaction.TX_PENDING, "Pending"),
            (PaymentTransaction.TX_FAILED, "Failed"),
        ],
        "summary": summary,
        "method_choices": PaymentTransaction._meta.get_field("method").choices,
        "active_tab": "accountant",
    }
    return render(request, "accountant/transactions.html", context)
