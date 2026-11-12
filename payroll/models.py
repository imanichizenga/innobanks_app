from django.db import models
from rps_app.models import Teacher
# Create your models here.
from django.conf import settings


from django.db import models


class Employee(models.Model):
    # 🔹 Basic Identification
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    username = models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True)
    first_name = models.CharField(max_length=100,null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100,null=True)
    date_of_birth = models.DateField()
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices)
    marital_status_choices = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
    ]
    marital_status = models.CharField(max_length=1, choices=marital_status_choices,null=True)
    nationality = models.CharField(max_length=100,null=True)

    # 🔹 Contact Information
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(null=True)

    # 🔹 Employment Information
    employee_id = models.CharField(max_length=50, null=True)
    job_title = models.CharField(max_length=100,null=True)
    department = models.CharField(max_length=100,null=True)
    employment_type_choices = [
        ('FT', 'Full-Time'),
        ('PT', 'Part-Time'),
        ('CT', 'Contract'),
        ('IN', 'Intern'),
    ]
    employment_type = models.CharField(max_length=2, choices=employment_type_choices,null=True)
    hire_date = models.DateField(null=True)
    status_choices = [
        ('ACTIVE', 'Active'),
        ('PROBATION', 'Probation'),
        ('TERMINATED', 'Terminated'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='ACTIVE',null=True)

    # 🔹 Legal & Compliance
    national_id = models.CharField(max_length=50, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    work_permit = models.CharField(max_length=50, blank=True, null=True)
    pension_number = models.CharField(max_length=50, blank=True, null=True)
    union_member = models.BooleanField(default=False)

    # 🔹 Banking & Payment Information
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    branch_code = models.CharField(max_length=20, blank=True, null=True)
    payment_method_choices = [
        ('BANK', 'Bank Transfer'),
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
        ('MOBILE', 'Mobile Money'),
    ]
    payment_method = models.CharField(max_length=10, choices=payment_method_choices, default='BANK',null=True)
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    # 🔹 Next of Kin / Beneficiary
    next_of_kin_name = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin_relationship = models.CharField(max_length=50, blank=True, null=True)
    next_of_kin_contact = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.employee_id}"



class EmployeeDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents',null=True)
    document_name = models.CharField(max_length=100,null=True)
    document_file = models.FileField(upload_to='employee_documents/',null=True)
    upload_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_name} for {self.employee.first_name} {self.employee.last_name}"
    

class EmployeePayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField(auto_now_add=True)


    academic_excellent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Average GPA of subjects tought by this teacher should not exceed number you set, eg 1.4")
    academic_excellent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount added if teacher satisfy the condition")
    academic_good = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Average GPA of subjects tought by this teacher should not exceed number you set, eg 1.4")
    academic_good_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount added if teacher satisfy the condition")
    academic_seen = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Average GPA of subjects tought by this teacher should not exceed number you set, eg 1.4")
    academic_seen_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount added if teacher satisfy the condition")


    attendance_excellent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Total number of P status is considered to be 'EXCELLENT' when is equal or greater than the number you set, eg 2")
    attendance_excellent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount you will add if teacher satisfy the condition")
    attendance_good = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Total number of P status is considered to be 'GOOD' when is equal or greater than the number you set, eg 2")
    attendance_good_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount you will add if teacher satisfy the condition")
    attendance_seen = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Total number of P status is considered to be 'SEEN' when is equal or greater than the number you set, eg 2")
    attendance_seen_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount you will add if teacher satisfy the condition")
    time_in_required = models.TimeField(null=True,help_text="Time required for each staff to signin, it considered 'EARLY' if staff signin is before or equal to this time")
    time_out_required = models.TimeField(null=True,help_text="Time required for each staff to signout, it considered 'EXTRA' if staff signout is after to this time")



    discipline_status = [
        ('excellent', 'Excellent'),
        ('good', 'GOOD'),
        ('seen', 'SEEN'),
    ]
    discipline = models.CharField(max_length=10, choices=discipline_status, default='SEEN',null=True)
    discipline_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True)



    promotion_status = [
        ('excellent', 'Excellent'),
        ('good', 'GOOD'),
        ('seen', 'SEEN'),
    ]
    promotion = models.CharField(max_length=10, choices=discipline_status, default='SEEN',null=True)
    promotion_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True)



    deduction_amount_for_attendance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount deducted if staff violate all attendance conditions")
    deduction_amount_for_academic = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount deducted if staff violate all academic conditions")
    deduction_amount_for_time_in = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount deducted if staff violate all TIME IN conditions")
    deduction_amount_for_time_out = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount deducted if staff violate all TIME OUT conditions,Typically if signout is before required time")



    other_deduction_name = models.CharField(max_length=100,null=True,help_text="Issues that cause to deduct staff payments")
    other_deduction_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True,help_text="Amount to be deducted due to other issues")

    def __str__(self):
        return f"Payment of {self.employee.first_name} {self.employee.last_name} on {self.payment_date}"