# from django.contrib import admin
# from .models import Employee, EmployeeDocument, EmployeePayment


# # 🔹 Inline for Employee Documents (appears inside Employee admin)
# class EmployeeDocumentInline(admin.TabularInline):
#     model = EmployeeDocument
#     extra = 1  # how many empty forms to show


# # 🔹 Inline for Employee Payment (OneToOne, so just 1 allowed)
# class EmployeePaymentInline(admin.StackedInline):
#     model = EmployeePayment
#     can_delete = False
#     max_num = 1


# @admin.register(Employee)
# class EmployeeAdmin(admin.ModelAdmin):
#     list_display = (
#         "employee_id", "first_name", "last_name", "job_title",
#         "department", "status", "employment_type", "hire_date"
#     )
#     list_filter = ("department", "status", "employment_type", "gender", "marital_status")
#     search_fields = ("employee_id", "first_name", "last_name", "email", "phone_number")
#     inlines = [EmployeeDocumentInline, EmployeePaymentInline]


# @admin.register(EmployeeDocument)
# class EmployeeDocumentAdmin(admin.ModelAdmin):
#     list_display = ("document_name", "employee", "upload_date")
#     search_fields = ("document_name", "employee__first_name", "employee__last_name")
#     list_filter = ("upload_date",)


# @admin.register(EmployeePayment)
# class EmployeePaymentAdmin(admin.ModelAdmin):
#     list_display = ("employee", "amount", "payment_method", "payment_date")
#     list_filter = ("payment_method", "payment_date")
#     search_fields = ("employee__first_name", "employee__last_name")
