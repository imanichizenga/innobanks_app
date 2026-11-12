from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('manage-payments/', views.manage_online_payments, name='manage_online_payment'),
    path('manage-payments/segments/', views.payment_segments_monitor, name='payment_segments_monitor'),
    path('manage-payments/segments/report/pdf/', views.payment_segments_monitor_pdf, name='payment_segments_monitor_pdf'),
    path('reports/', views.get_reports, name='get_reports'),
    path('create-payments/', views.create_payment, name='create_payment'),
    path('create-payments/statuses/', views.create_payment_statuses, name='create_payment_statuses'),
    path('create-payments/<int:payment_id>/refresh/', views.refresh_create_payment_token, name='refresh_create_payment_token'),
    path('communications/', views.communication_logs, name='communication_logs'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('webhooks/snippe/', views.snippe_webhook, name='snippe_webhook'),
    path('manage-payments/fees/<int:class_id>/', views.fees_for_class, name='fees_for_class'),
    path('manage-payments/students/<int:class_id>/<int:fee_id>/', views.students_for_fee, name='students_for_fee'),
    path('manage-payments/billpay/generate/', views.generate_billpay_number, name='generate_billpay_number'),
    path('manage-payments/billpay/generate-bulk/', views.generate_billpay_numbers_bulk, name='generate_billpay_numbers_bulk'),
    path('manage-payments/billpay/refresh/', views.refresh_billpay_number, name='refresh_billpay_number'),
    path('manage-payments/billpay/delete/', views.delete_billpay_number, name='delete_billpay_number'),
    path('manage-payments/notify/', views.toggle_notify_student_account, name='toggle_notify_student_account'),
    path('manage-payments/push/', views.push_mobile_payment, name='push_mobile_payment'),
    path('student-payments/push/', views.student_push_payment, name='student_push_payment'),
    path('student-payments/token/', views.student_generate_payment_token, name='student_generate_payment_token'),
    path('student-payments/segments/push/', views.student_push_segment_payment, name='student_push_segment_payment'),
    path('student-payments/segments/generate/', views.student_generate_segment_billpay, name='student_generate_segment_billpay'),
    # Fee Management
    path('fees/', views.fee_list, name='fee_list'),
    path('fees/create/', views.fee_create, name='fee_create'),
    path('fees/update/<int:fee_id>/', views.fee_update, name='fee_update'),
    path('fees/delete/<int:fee_id>/', views.fee_delete, name='fee_delete'),
    # Student Fee Assignment and Listing
    path('assign-fees/<int:class_id>/', views.assign_fees_to_students, name='assign_fees_to_students'),
    path('student-fees/', views.student_fee_list, name='student_fee_list_default'),
    path('student-fees/<int:class_id>/', views.student_fee_list, name='student_fee_list'),
    path('student-fees-dynamic/', views.student_fee_list_dynamic, name='student_fee_list_dynamic'),
    path('student-fees/update/<int:student_id>/', views.update_student_fee, name='update_student_fee'),
    path('student-fees/delete/<int:student_id>/<int:fee_id>/', views.delete_student_fee, name='delete_student_fee'),
    path('student-fees/add/<int:student_id>/<int:class_id>/', views.add_student_fee, name='add_student_fee'),
    path('get-fees/<int:class_id>/', views.get_fees_for_class, name='get_fees_for_class'),
    path('get-student-fees/<int:class_id>/', views.get_student_fees_for_class, name='get_student_fees_for_class'),
    # Discount Management
    path('discount/update/', views.update_discount, name='update_discount'),
    path('discount/delete/<int:discount_id>/', views.delete_discount, name='delete_discount'),
    # Payment Management
    path('delete-payment/<int:student_id>/<int:class_id>/<int:fee_id>/', views.delete_payment, name='delete_payment'),
    path('delete-single-payment/<int:payment_id>/<int:class_id>/<int:fee_id>/', views.delete_single_payment, name='delete_single_payment'),
    path('edit-payment/<int:payment_id>/<int:class_id>/<int:fee_id>/', views.edit_payment, name='edit_payment'),
    path('payment/pay/<int:student_id>/<int:fee_id>/', views.pay_fee, name='pay_fee'),
    path('payments/upload/', views.upload_payments, name='upload_payments'),
    # Fee Account Numbers
    path('fee-account-numbers/', views.fee_account_number_list, name='fee_account_number_list'),
    path('fee-account-number/update/<int:pk>/', views.fee_account_number_update, name='fee_account_number_update'),
    path('fee-account-number/delete/<int:pk>/', views.fee_account_number_delete, name='fee_account_number_delete'),
    # Miscellaneous
    path('fee-management/', views.fee_management, name='fee_management'),
    path('change-logs/', views.view_change_logs, name='view_change_logs'),
    # PDF and SMS/Email
    # path('download/student-fee/<int:class_id>/<int:fee_id>/', views.download_student_fee_pdf, name='download_student_fee_pdf'),
    path('download/student-financial/', views.download_student_financial_pdf, name='download_student_financial_pdf'),
    # path('download/general-student-fee/<int:class_id>/', views.download_general_student_fee_pdf, name='download_general_student_fee_pdf'),
    # path('sms/send-student-fee/', views.send_student_fee_sms, name='send_student_fee_sms'),
    # path('sms/send-remaining-fee/', views.send_remaining_fee_sms, name='send_remaining_fee_sms'),
    # path('email/send-student-fee/', views.send_student_fee_email, name='send_student_fee_email'),
    path('get-student-focus/<int:class_id>/', views.get_student_focus_for_class, name='get_student_focus_for_class'),
    path('assign-focus/', views.assign_student_focus, name='assign_student_focus'),
    path('assign-focus/<int:class_id>/', views.assign_student_focus, name='assign_student_focus_with_class'),
    path('get-student-focus/<int:class_id>/', views.get_student_focus_for_class, name='get_student_focus_for_class'),
    path('assign-registration/', views.assign_student_registration, name='assign_student_registration'),
    path('assign-registration/<int:class_id>/', views.assign_student_registration, name='assign_student_registration_with_class'),
    path('get-student-registration/<int:class_id>/', views.get_student_registration_for_class, name='get_student_registration_for_class'),
    path('apply-discount/<int:student_id>/<int:fee_id>/<int:class_id>/', views.apply_discount, name='apply_discount'),
    path('apply-payment/<int:student_id>/<int:fee_id>/<int:class_id>/', views.apply_payment, name='apply_payment'),
    path('view-payment-records/<int:student_id>/<int:fee_id>/<int:class_id>/', views.view_payment_records, name='view_payment_records'),

    path('student-fee/delete/<int:student_id>/<int:fee_id>/', views.delete_student_fee_specific, name='delete_student_fee'),
    path('student-fee/update/<int:student_id>/<int:fee_id>/', views.update_student_fee_specific, name='update_student_fee'),

    path('download_student_fee_pdf/<int:class_id>/<int:fee_id>/', views.download_student_fee_pdf, name='download_student_fee_pdf'),
    path('download_general_student_fee_pdf/<int:class_id>/', views.download_general_student_fee_pdf, name='download_general_student_fee_pdf'),

    path('send_remaining_fee_sms/', views.send_remaining_fee_sms, name='send_remaining_fee_sms'),
    path('send_student_fee_sms/', views.send_student_fee_sms, name='send_student_fee_sms'),
    path('send_student_fee_email/', views.send_student_fee_email, name='send_student_fee_email'),

    path('update-student-registration/<int:registration_id>/', views.update_student_registration, name='update_student_registration'),
    path('delete-student-registration/<int:registration_id>/', views.delete_student_registration, name='delete_student_registration'),

    # Student Focus Management
    path('student-focus/delete/<int:student_id>/', views.delete_student_focus, name='delete_student_focus'),
    path('student-focus/update/<int:student_id>/', views.update_student_focus, name='update_student_focus'),
    path('assign-focus/<int:class_id>/', views.assign_student_focus, name='assign_student_focus_with_class'),


    path('fee-accounts/', views.fee_account_management, name='fee_account_management'),
    path('fee-accounts/create/', views.create_fee_account, name='create_fee_account'),
    path('fee-accounts/update/<int:fee_account_id>/', views.update_fee_account, name='update_fee_account'),
    path('fee-accounts/delete/<int:fee_account_id>/', views.delete_fee_account, name='delete_fee_account'),

    path('fees/update/<int:fee_id>/', views.fee_update, name='fee_update'),
    path('fees/delete/<int:fee_id>/', views.fee_delete, name='fee_delete'),
]
