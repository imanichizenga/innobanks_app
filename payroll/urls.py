from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    path('select-teacher/', views.select_teacher, name='select_teacher'),
    path('save-basic-identification/', views.save_basic_identification, name='save_basic_identification'),
    path('save-contact-information/', views.save_contact_information, name='save_contact_information'),
    path('save-employment-information/', views.save_employment_information, name='save_employment_information'),
    path('save-legal-compliance/', views.save_legal_compliance, name='save_legal_compliance'),
    path('save-banking-payment/', views.save_banking_payment, name='save_banking_payment'),
    path('save-next-of-kin/', views.save_next_of_kin, name='save_next_of_kin'),
    path('update-basic-identification/<int:employee_id>/', views.update_basic_identification, name='update_basic_identification'),
    path('update-contact-information/<int:employee_id>/', views.update_contact_information, name='update_contact_information'),
    path('update-employment-information/<int:employee_id>/', views.update_employment_information, name='update_employment_information'),
    path('update-legal-compliance/<int:employee_id>/', views.update_legal_compliance, name='update_legal_compliance'),
    path('update-banking-payment/<int:employee_id>/', views.update_banking_payment, name='update_banking_payment'),
    path('update-next-of-kin/<int:employee_id>/', views.update_next_of_kin, name='update_next_of_kin'),
    path('delete-employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),



    path('select-employee-documents/', views.select_employee_for_documents, name='select_employee_for_documents'),
    path('save-employee-document/', views.save_employee_document, name='save_employee_document'),
    path('update-employee-document/<int:document_id>/', views.update_employee_document, name='update_employee_document'),
    path('delete-employee-document/<int:document_id>/', views.delete_employee_document, name='delete_employee_document'),


    path('select_employee/', views.select_employee, name='select_employee'),
    path('create_payment/', views.create_payment, name='create_payment'),
    path('delete_payment/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('update_academic_conditions/<int:payment_id>/', views.update_academic_conditions, name='update_academic_conditions'),
    path('update_attendance_conditions/<int:payment_id>/', views.update_attendance_conditions, name='update_attendance_conditions'),
    path('update_discipline_conditions/<int:payment_id>/', views.update_discipline_conditions, name='update_discipline_conditions'),
    path('update_promotion_conditions/<int:payment_id>/', views.update_promotion_conditions, name='update_promotion_conditions'),
    path('update_deductions/<int:payment_id>/', views.update_deductions, name='update_deductions'),



]