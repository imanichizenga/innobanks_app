from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from rps_app.models import Teacher
from .models import Employee
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
@transaction.atomic
def select_teacher(request):
    """
    Handle teacher selection and store the selected teacher in the session.
    Display the employee creation form with available teachers.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to manage employee details.")
        return redirect('homepage')

    # Fetch teachers created by the current user
    teachers = Teacher.objects.filter(created_by=request.user)
    
    # Get selected teacher from session or POST
    selected_teacher_id = request.session.get('selected_teacher_id')
    selected_teacher = None
    if selected_teacher_id:
        try:
            selected_teacher = Teacher.objects.get(id=selected_teacher_id, created_by=request.user)
        except Teacher.DoesNotExist:
            selected_teacher = None

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        if teacher_id:
            try:
                selected_teacher = Teacher.objects.get(id=teacher_id, created_by=request.user)
                request.session['selected_teacher_id'] = teacher_id
                messages.success(request, f"Selected teacher: {selected_teacher.teacherName or selected_teacher.user.username}")
            except Teacher.DoesNotExist:
                messages.error(request, "Invalid teacher selected.")
        else:
            messages.error(request, "Please select a teacher.")
            request.session.pop('selected_teacher_id', None)
            selected_teacher = None

    # Fetch existing employees for the selected teacher
    employees = Employee.objects.filter(username__created_by=request.user) if request.user.is_teacher else Employee.objects.all()

    return render(request, 'payroll/employee_create.html', {
        'teachers': teachers,
        'selected_teacher': selected_teacher,
        'employees': employees,
    })

@login_required
@transaction.atomic
def save_basic_identification(request):
    """
    Save Basic Identification details for the selected teacher.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to save employee details.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        try:
            teacher = Teacher.objects.get(id=teacher_id, created_by=request.user)
        except Teacher.DoesNotExist:
            messages.error(request, "Invalid teacher selected.")
            return redirect('payroll:select_teacher')

        # Check if employee already exists for this teacher
        if Employee.objects.filter(username=teacher).exists():
            messages.error(request, f"Employee profile already exists for {teacher.teacherName or teacher.user.username}.")
            return redirect('payroll:select_teacher')

        # Validate required fields
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'marital_status', 'nationality']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_teacher')

        try:
            Employee.objects.create(
                user=request.user,
                username=teacher,
                first_name=request.POST.get('first_name'),
                middle_name=request.POST.get('middle_name'),
                last_name=request.POST.get('last_name'),
                date_of_birth=request.POST.get('date_of_birth'),
                gender=request.POST.get('gender'),
                marital_status=request.POST.get('marital_status'),
                nationality=request.POST.get('nationality'),
            )
            messages.success(request, "Basic Identification details saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving Basic Identification details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def save_contact_information(request):
    """
    Save Contact Information details for the selected teacher.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to save employee details.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        try:
            teacher = Teacher.objects.get(id=teacher_id, created_by=request.user)
            employee = Employee.objects.get(username=teacher,user=request.user)
        except Teacher.DoesNotExist:
            messages.error(request, "Invalid teacher selected.")
            return redirect('payroll:select_teacher')
        except Employee.DoesNotExist:
            messages.error(request, "Employee profile not found. Please complete Basic Identification first.")
            return redirect('payroll:select_teacher')

        # Validate required fields
        required_fields = ['address', 'phone_number', 'email']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_teacher')

        try:
            employee.address = request.POST.get('address')
            employee.phone_number = request.POST.get('phone_number')
            employee.email = request.POST.get('email')
            employee.user=request.user
            employee.save()
            messages.success(request, "Contact Information details saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving Contact Information details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def save_employment_information(request):
    """
    Save Employment Information details for the selected teacher.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to save employee details.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        try:
            teacher = Teacher.objects.get(id=teacher_id, created_by=request.user)
            employee = Employee.objects.get(username=teacher,user=request.user)
        except Teacher.DoesNotExist:
            messages.error(request, "Invalid teacher selected.")
            return redirect('payroll:select_teacher')
        except Employee.DoesNotExist:
            messages.error(request, "Employee profile not found. Please complete Basic Identification first.")
            return redirect('payroll:select_teacher')

        # Validate required fields
        required_fields = ['employee_id', 'job_title', 'department', 'employment_type', 'hire_date', 'status']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_teacher')

        try:
            employee.employee_id = request.POST.get('employee_id')
            employee.job_title = request.POST.get('job_title')
            employee.department = request.POST.get('department')
            employee.employment_type = request.POST.get('employment_type')
            employee.hire_date = request.POST.get('hire_date')
            employee.status = request.POST.get('status')
            employee.user=request.user
            employee.save()
            messages.success(request, "Employment Information details saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving Employment Information details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def save_legal_compliance(request):
    """
    Save Legal & Compliance details for the selected teacher.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to save employee details.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        try:
            teacher = Teacher.objects.get(id=teacher_id, created_by=request.user)
            employee = Employee.objects.get(username=teacher,user=request.user)
        except Teacher.DoesNotExist:
            messages.error(request, "Invalid teacher selected.")
            return redirect('payroll:select_teacher')
        except Employee.DoesNotExist:
            messages.error(request, "Employee profile not found. Please complete Basic Identification first.")
            return redirect('payroll:select_teacher')

        # Validate required fields
        required_fields = ['national_id', 'union_member']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_teacher')

        try:
            employee.national_id = request.POST.get('national_id')
            employee.tax_id = request.POST.get('tax_id')
            employee.work_permit = request.POST.get('work_permit')
            employee.pension_number = request.POST.get('pension_number')
            employee.union_member = request.POST.get('union_member') == 'True'
            employee.user=request.user
            employee.save()
            messages.success(request, "Legal & Compliance details saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving Legal & Compliance details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def save_banking_payment(request):
    """
    Save Banking & Payment Information details for the selected teacher.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to save employee details.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        try:
            teacher = Teacher.objects.get(id=teacher_id, created_by=request.user)
            employee = Employee.objects.get(username=teacher,user=request.user)
        except Teacher.DoesNotExist:
            messages.error(request, "Invalid teacher selected.")
            return redirect('payroll:select_teacher')
        except Employee.DoesNotExist:
            messages.error(request, "Employee profile not found. Please complete Basic Identification first.")
            return redirect('payroll:select_teacher')

        # Validate required fields
        required_fields = ['payment_method']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_teacher')

        try:
            employee.bank_name = request.POST.get('bank_name')
            employee.bank_account_number = request.POST.get('bank_account_number')
            employee.branch_code = request.POST.get('branch_code')
            employee.payment_method = request.POST.get('payment_method')
            employee.fixed_amount = request.POST.get('fixed_amount')
            employee.user=request.user
            employee.save()
            messages.success(request, "Banking & Payment Information details saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving Banking & Payment Information details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def save_next_of_kin(request):
    """
    Save Next of Kin details for the selected teacher.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to save employee details.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        try:
            teacher = Teacher.objects.get(id=teacher_id, created_by=request.user)
            employee = Employee.objects.get(username=teacher,user=request.user)
        except Teacher.DoesNotExist:
            messages.error(request, "Invalid teacher selected.")
            return redirect('payroll:select_teacher')
        except Employee.DoesNotExist:
            messages.error(request, "Employee profile not found. Please complete Basic Identification first.")
            return redirect('payroll:select_teacher')

        try:
            employee.next_of_kin_name = request.POST.get('next_of_kin_name')
            employee.next_of_kin_relationship = request.POST.get('next_of_kin_relationship')
            employee.next_of_kin_contact = request.POST.get('next_of_kin_contact')
            employee.user=request.user
            employee.save()
            messages.success(request, "Next of Kin details saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving Next of Kin details: {str(e)}")

    return redirect('payroll:select_teacher')





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from rps_app.models import Teacher
from .models import Employee
from django.contrib.auth import get_user_model

User = get_user_model()

# Existing views (not repeated here): select_teacher, save_basic_identification, save_contact_information,
# save_employment_information, save_legal_compliance, save_banking_payment, save_next_of_kin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from rps_app.models import Teacher
from .models import Employee
from django.contrib.auth import get_user_model

User = get_user_model()

# Existing views (not repeated here): select_teacher, save_basic_identification, save_contact_information,
# save_employment_information, save_legal_compliance, save_banking_payment, save_next_of_kin

@login_required
@transaction.atomic
def update_basic_identification(request, employee_id):
    """
    Update Basic Identification details for the specified employee.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update employee details.")
        return redirect('payroll:select_teacher')

    try:
        employee = Employee.objects.get(id=employee_id, username__created_by=request.user,user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found or you don’t have permission to update this employee.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'marital_status', 'nationality']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_teacher')

        try:
            employee.first_name = request.POST.get('first_name')
            employee.middle_name = request.POST.get('middle_name')
            employee.last_name = request.POST.get('last_name')
            employee.date_of_birth = request.POST.get('date_of_birth')
            employee.gender = request.POST.get('gender')
            employee.marital_status = request.POST.get('marital_status')
            employee.nationality = request.POST.get('nationality')
            employee.user=request.user
            employee.save()
            messages.success(request, "Basic Identification details updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating Basic Identification details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def update_contact_information(request, employee_id):
    """
    Update Contact Information details for the specified employee.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update employee details.")
        return redirect('payroll:select_teacher')

    try:
        employee = Employee.objects.get(id=employee_id, username__created_by=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found or you don’t have permission to update this employee.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        # Validate required fields
        required_fields = ['address', 'phone_number', 'email']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_teacher')

        try:
            employee.address = request.POST.get('address')
            employee.phone_number = request.POST.get('phone_number')
            employee.email = request.POST.get('email')
            employee.user=request.user
            employee.save()
            messages.success(request, "Contact Information details updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating Contact Information details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def update_employment_information(request, employee_id):
    """
    Update Employment Information details for the specified employee.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update employee details.")
        return redirect('payroll:select_teacher')

    try:
        employee = Employee.objects.get(id=employee_id, username__created_by=request.user,user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found or you don’t have permission to update this employee.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        # Validate required fields
        required_fields = ['employee_id', 'job_title', 'department', 'employment_type', 'hire_date', 'status']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_teacher')

        try:
            employee.employee_id = request.POST.get('employee_id')
            employee.job_title = request.POST.get('job_title')
            employee.department = request.POST.get('department')
            employee.employment_type = request.POST.get('employment_type')
            employee.hire_date = request.POST.get('hire_date')
            employee.status = request.POST.get('status')
            employee.user=request.user
            employee.save()
            messages.success(request, "Employment Information details updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating Employment Information details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def update_legal_compliance(request, employee_id):
    """
    Update Legal & Compliance details for the specified employee.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update employee details.")
        return redirect('payroll:select_teacher')

    try:
        employee = Employee.objects.get(id=employee_id, username__created_by=request.user,user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found or you don’t have permission to update this employee.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        # Validate required fields
        required_fields = ['national_id', 'union_member']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_teacher')

        try:
            employee.national_id = request.POST.get('national_id')
            employee.tax_id = request.POST.get('tax_id')
            employee.work_permit = request.POST.get('work_permit')
            employee.pension_number = request.POST.get('pension_number')
            employee.union_member = request.POST.get('union_member') == 'True'
            employee.user=request.user  
            employee.save()
            messages.success(request, "Legal & Compliance details updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating Legal & Compliance details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def update_banking_payment(request, employee_id):
    """
    Update Banking & Payment Information details for the specified employee.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update employee details.")
        return redirect('payroll:select_teacher')

    try:
        employee = Employee.objects.get(id=employee_id, username__created_by=request.user,user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found or you don’t have permission to update this employee.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        # Validate required fields
        required_fields = ['payment_method']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_teacher')

        try:
            employee.bank_name = request.POST.get('bank_name')
            employee.bank_account_number = request.POST.get('bank_account_number')
            employee.branch_code = request.POST.get('branch_code')
            employee.payment_method = request.POST.get('payment_method')
            employee.fixed_amount = request.POST.get('fixed_amount')
            employee.user=request.user
            employee.save()
            messages.success(request, "Banking & Payment Information details updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating Banking & Payment Information details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def update_next_of_kin(request, employee_id):
    """
    Update Next of Kin details for the specified employee.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update employee details.")
        return redirect('payroll:select_teacher')

    try:
        employee = Employee.objects.get(id=employee_id, username__created_by=request.user,user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found or you don’t have permission to update this employee.")
        return redirect('payroll:select_teacher')

    if request.method == 'POST':
        try:
            employee.next_of_kin_name = request.POST.get('next_of_kin_name')
            employee.next_of_kin_relationship = request.POST.get('next_of_kin_relationship')
            employee.next_of_kin_contact = request.POST.get('next_of_kin_contact')
            employee.user=request.user
            employee.save()
            messages.success(request, "Next of Kin details updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating Next of Kin details: {str(e)}")

    return redirect('payroll:select_teacher')

@login_required
@transaction.atomic
def delete_employee(request, employee_id):
    """
    Delete the specified employee record.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to delete employee details.")
        return redirect('payroll:select_teacher')

    try:
        employee = Employee.objects.get(id=employee_id, username__created_by=request.user,user=request.user)
        employee_name = f"{employee.first_name} {employee.last_name}"
        employee.delete()
        messages.success(request, f"Employee {employee_name} deleted successfully.")
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found or you don’t have permission to delete this employee.")

    return redirect('payroll:select_teacher')

    

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Employee, EmployeeDocument
from django.core.files.storage import FileSystemStorage
import os

@login_required
@transaction.atomic
def select_employee_for_documents(request):
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to manage employee documents.")
        return redirect('homepage')

    employees = Employee.objects.filter(user=request.user)
    selected_employee_id = request.session.get('selected_employee_id')
    selected_employee = None
    if selected_employee_id:
        try:
            selected_employee = Employee.objects.get(id=selected_employee_id, user=request.user)
        except Employee.DoesNotExist:
            selected_employee = None

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if employee_id:
            try:
                selected_employee = Employee.objects.get(id=employee_id, user=request.user)
                request.session['selected_employee_id'] = employee_id
                messages.success(request, f"Selected employee: {selected_employee.first_name} {selected_employee.last_name}")
            except Employee.DoesNotExist:
                messages.error(request, "Invalid employee selected.")
        else:
            messages.error(request, "Please select an employee.")
            request.session.pop('selected_employee_id', None)
            selected_employee = None

    documents = EmployeeDocument.objects.filter(employee=selected_employee) if selected_employee else []
    print("Selected employee:", selected_employee)
    print("Documents:", list(documents))

    return render(request, 'payroll/employee_documents.html', {
        'employees': employees,
        'selected_employee': selected_employee,
        'documents': documents,
    })

@login_required
@transaction.atomic
def save_employee_document(request):
    """
    Save a new employee document for the selected employee.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to save employee documents.")
        return redirect('payroll:select_employee_for_documents')

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        try:
            employee = Employee.objects.get(id=employee_id, username__created_by=request.user)
        except Employee.DoesNotExist:
            messages.error(request, "Invalid employee selected.")
            return redirect('payroll:select_employee_for_documents')

        # Validate required fields
        required_fields = ['document_name', 'document_file']
        if not all(request.POST.get(field) or request.FILES.get(field) for field in required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('payroll:select_employee_for_documents')

        try:
            document_file = request.FILES['document_file']
            EmployeeDocument.objects.create(
                user=request.user,
                employee=employee,
                document_name=request.POST.get('document_name'),
                document_file=document_file,
            )
            messages.success(request, "Employee document saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving employee document: {str(e)}")

    return redirect('payroll:select_employee_for_documents')

@login_required
@transaction.atomic
def update_employee_document(request, document_id):
    """
    Update an existing employee document.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update employee documents.")
        return redirect('payroll:select_employee_for_documents')

    try:
        document = EmployeeDocument.objects.get(id=document_id, employee__username__created_by=request.user)
    except EmployeeDocument.DoesNotExist:
        messages.error(request, "Document not found or you don’t have permission to update this document.")
        return redirect('payroll:select_employee_for_documents')

    if request.method == 'POST':
        # Validate required fields
        required_fields = ['document_name']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, "Document name is required.")
            return redirect('payroll:select_employee_for_documents')

        try:
            document.document_name = request.POST.get('document_name')
            if 'document_file' in request.FILES:
                # Delete old file if a new one is uploaded
                if document.document_file:
                    if os.path.exists(document.document_file.path):
                        os.remove(document.document_file.path)
                document.document_file = request.FILES['document_file']
            document.save()
            messages.success(request, "Employee document updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating employee document: {str(e)}")

    return redirect('payroll:select_employee_for_documents')

@login_required
@transaction.atomic
def delete_employee_document(request, document_id):
    """
    Delete an employee document.
    """
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to delete employee documents.")
        return redirect('payroll:select_employee_for_documents')

    try:
        document = EmployeeDocument.objects.get(id=document_id, employee__username__created_by=request.user)
        document_name = document.document_name
        # Delete file from storage
        if document.document_file:
            if os.path.exists(document.document_file.path):
                os.remove(document.document_file.path)
        document.delete()
        messages.success(request, f"Document {document_name} deleted successfully.")
    except EmployeeDocument.DoesNotExist:
        messages.error(request, "Document not found or you don’t have permission to delete this document.")

    return redirect('payroll:select_employee_for_documents')















# payroll/views.py (add these to the existing views.py)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Employee, EmployeePayment
from rps_app.models import Teacher

@login_required
@transaction.atomic
def select_employee(request):
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to manage payment conditions.")
        return redirect('homepage')

    # Fetch employees based on user role
    if request.user.is_teacher:
        employees = Employee.objects.filter(username__created_by=request.user)
    else:
        employees = Employee.objects.all()

    # Get selected employee from session or POST
    selected_employee_id = request.session.get('selected_employee_id')
    selected_employee = None
    if selected_employee_id:
        try:
            selected_employee = Employee.objects.get(id=selected_employee_id)
            # Permission check
            if request.user.is_teacher and selected_employee.username.created_by != request.user:
                selected_employee = None
        except Employee.DoesNotExist:
            selected_employee = None

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if employee_id:
            try:
                selected_employee = Employee.objects.get(id=employee_id)
                if request.user.is_teacher and selected_employee.username.created_by != request.user:
                    raise Employee.DoesNotExist
                request.session['selected_employee_id'] = employee_id
                messages.success(request, f"Selected employee: {selected_employee.first_name} {selected_employee.last_name}")
            except Employee.DoesNotExist:
                messages.error(request, "Invalid employee selected.")
        else:
            messages.error(request, "Please select an employee.")
            request.session.pop('selected_employee_id', None)
            selected_employee = None

    # Fetch existing payments for the selected employee
    payments = EmployeePayment.objects.filter(employee=selected_employee) if selected_employee else EmployeePayment.objects.none()

    return render(request, 'payroll/payment_conditions.html', {
        'employees': employees,
        'selected_employee': selected_employee,
        'payments': payments,
    })

@login_required
@transaction.atomic
def create_payment(request):
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to create payments.")
        return redirect('payroll:select_employee')

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        payment_date = request.POST.get('payment_date')
        if not employee_id or not payment_date:
            messages.error(request, "Employee and payment date are required.")
            return redirect('payroll:select_employee')

        try:
            employee = Employee.objects.get(id=employee_id)
            if request.user.is_teacher and employee.username.created_by != request.user:
                raise Employee.DoesNotExist
            EmployeePayment.objects.create(
                user=request.user,
                employee=employee,
                payment_date=payment_date
            )
            messages.success(request, "New payment created successfully.")
        except Employee.DoesNotExist:
            messages.error(request, "Invalid employee selected.")
        except Exception as e:
            messages.error(request, f"Error creating payment: {str(e)}")

    return redirect('payroll:select_employee')

@login_required
@transaction.atomic
def delete_payment(request, payment_id):
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to delete payments.")
        return redirect('payroll:select_employee')

    try:
        payment = EmployeePayment.objects.get(id=payment_id)
        if request.user.is_teacher and payment.employee.username.created_by != request.user:
            raise EmployeePayment.DoesNotExist
        payment.delete()
        messages.success(request, "Payment deleted successfully.")
    except EmployeePayment.DoesNotExist:
        messages.error(request, "Invalid payment selected.")

    return redirect('payroll:select_employee')

@login_required
@transaction.atomic
def update_academic_conditions(request, payment_id):
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update conditions.")
        return redirect('payroll:select_employee')

    if request.method == 'POST':
        try:
            payment = EmployeePayment.objects.get(id=payment_id)
            if request.user.is_teacher and payment.employee.username.created_by != request.user:
                raise EmployeePayment.DoesNotExist
            payment.academic_excellent = request.POST.get('academic_excellent', payment.academic_excellent)
            payment.academic_excellent_amount = request.POST.get('academic_excellent_amount', payment.academic_excellent_amount)
            payment.academic_good = request.POST.get('academic_good', payment.academic_good)
            payment.academic_good_amount = request.POST.get('academic_good_amount', payment.academic_good_amount)
            payment.academic_seen = request.POST.get('academic_seen', payment.academic_seen)
            payment.academic_seen_amount = request.POST.get('academic_seen_amount', payment.academic_seen_amount)
            payment.save()
            messages.success(request, "Academic conditions updated successfully.")
        except EmployeePayment.DoesNotExist:
            messages.error(request, "Invalid payment selected.")
        except Exception as e:
            messages.error(request, f"Error updating academic conditions: {str(e)}")

    return redirect('payroll:select_employee')

@login_required
@transaction.atomic
def update_attendance_conditions(request, payment_id):
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update conditions.")
        return redirect('payroll:select_employee')

    if request.method == 'POST':
        try:
            payment = EmployeePayment.objects.get(id=payment_id)
            if request.user.is_teacher and payment.employee.username.created_by != request.user:
                raise EmployeePayment.DoesNotExist
            payment.attendance_excellent = request.POST.get('attendance_excellent', payment.attendance_excellent)
            payment.attendance_excellent_amount = request.POST.get('attendance_excellent_amount', payment.attendance_excellent_amount)
            payment.attendance_good = request.POST.get('attendance_good', payment.attendance_good)
            payment.attendance_good_amount = request.POST.get('attendance_good_amount', payment.attendance_good_amount)
            payment.attendance_seen = request.POST.get('attendance_seen', payment.attendance_seen)
            payment.attendance_seen_amount = request.POST.get('attendance_seen_amount', payment.attendance_seen_amount)
            payment.time_in_required = request.POST.get('time_in_required', payment.time_in_required)
            payment.time_out_required = request.POST.get('time_out_required', payment.time_out_required)
            payment.save()
            messages.success(request, "Attendance conditions updated successfully.")
        except EmployeePayment.DoesNotExist:
            messages.error(request, "Invalid payment selected.")
        except Exception as e:
            messages.error(request, f"Error updating attendance conditions: {str(e)}")

    return redirect('payroll:select_employee')

@login_required
@transaction.atomic
def update_discipline_conditions(request, payment_id):
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update conditions.")
        return redirect('payroll:select_employee')

    if request.method == 'POST':
        try:
            payment = EmployeePayment.objects.get(id=payment_id)
            if request.user.is_teacher and payment.employee.username.created_by != request.user:
                raise EmployeePayment.DoesNotExist
            payment.discipline = request.POST.get('discipline', payment.discipline)
            payment.discipline_amount = request.POST.get('discipline_amount', payment.discipline_amount)
            payment.save()
            messages.success(request, "Discipline conditions updated successfully.")
        except EmployeePayment.DoesNotExist:
            messages.error(request, "Invalid payment selected.")
        except Exception as e:
            messages.error(request, f"Error updating discipline conditions: {str(e)}")

    return redirect('payroll:select_employee')

@login_required
@transaction.atomic
def update_promotion_conditions(request, payment_id):
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update conditions.")
        return redirect('payroll:select_employee')

    if request.method == 'POST':
        try:
            payment = EmployeePayment.objects.get(id=payment_id)
            if request.user.is_teacher and payment.employee.username.created_by != request.user:
                raise EmployeePayment.DoesNotExist
            payment.promotion = request.POST.get('promotion', payment.promotion)
            payment.promotion_amount = request.POST.get('promotion_amount', payment.promotion_amount)
            payment.save()
            messages.success(request, "Promotion conditions updated successfully.")
        except EmployeePayment.DoesNotExist:
            messages.error(request, "Invalid payment selected.")
        except Exception as e:
            messages.error(request, f"Error updating promotion conditions: {str(e)}")

    return redirect('payroll:select_employee')

@login_required
@transaction.atomic
def update_deductions(request, payment_id):
    if not (request.user.is_superuser or request.user.is_teacher):
        messages.error(request, "You don’t have permission to update conditions.")
        return redirect('payroll:select_employee')

    if request.method == 'POST':
        try:
            payment = EmployeePayment.objects.get(id=payment_id)
            if request.user.is_teacher and payment.employee.username.created_by != request.user:
                raise EmployeePayment.DoesNotExist
            payment.deduction_amount_for_attendance = request.POST.get('deduction_amount_for_attendance', payment.deduction_amount_for_attendance)
            payment.deduction_amount_for_academic = request.POST.get('deduction_amount_for_academic', payment.deduction_amount_for_academic)
            payment.deduction_amount_for_time_in = request.POST.get('deduction_amount_for_time_in', payment.deduction_amount_for_time_in)
            payment.deduction_amount_for_time_out = request.POST.get('deduction_amount_for_time_out', payment.deduction_amount_for_time_out)
            payment.other_deduction_name = request.POST.get('other_deduction_name', payment.other_deduction_name)
            payment.other_deduction_amount = request.POST.get('other_deduction_amount', payment.other_deduction_amount)
            payment.save()
            messages.success(request, "Deductions updated successfully.")
        except EmployeePayment.DoesNotExist:
            messages.error(request, "Invalid payment selected.")
        except Exception as e:
            messages.error(request, f"Error updating deductions: {str(e)}")

    return redirect('payroll:select_employee')