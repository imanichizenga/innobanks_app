# rps_app/urls.py (corrected)
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('login/', views.login_view, name='login_view'),
  
    path('download_merged_final_financial_pdf/', views.download_merged_final_financial_pdf, name='download_merged_final_financial_pdf'),

    path('create-academic-year/', views.create_academic_year, name='create_academic_year'),
    path('create-teacher-class/', views.create_teacher_class, name='create_teacher_class'),
    path('select-teacher-class/', views.select_teacher_class, name='select_teacher_class'),
    path('assign-academic-year/', views.assign_academic_year, name='assign_academic_year'),
    path('toggle-academic-year/<int:year_id>/', views.toggle_academic_year, name='toggle_academic_year'),

    path('download_merged_pdf/', views.download_merged_pdf, name='download_merged_pdf'),
    path('download_merged_final_result_pdf/', views.download_merged_final_result_pdf, name='download_merged_final_result_pdf'),
    path('download_merged_ca_result_pdf/', views.download_merged_ca_result_pdf, name='download_merged_ca_result_pdf'),
    path('download_merged_full_report/', views.download_merged_full_report, name='download_merged_full_report'),

    path('logout/', views.user_logout, name='user_logout'),

    # Student Management
    path('student/', views.create_student, name='create_student'),
    path("applications/", views.student_application_list, name="student_applications"),
    path("applications/create/", views.student_application_create, name="student_application_create"),
    path("applications/<int:pk>/", views.student_application_detail, name="student_application_detail"),
    path("applications/<int:pk>/edit/", views.student_application_edit, name="student_application_edit"),
    path("applications/<int:pk>/delete/", views.student_application_delete, name="student_application_delete"),
    path("applications/<int:pk>/status/", views.student_application_update_status, name="student_application_update_status"),
    path("applications/<int:pk>/form/", views.student_application_form_print, name="student_application_form_print"),

    path('academic-year/create/', views.create_academic_year, name='create_academic_year'),
    path('class/delete/<int:id>/', views.delete_class, name='delete_class'),
    path('academic-year/delete/<int:id>/', views.delete_academic_year, name='delete_academic_year'),
    
    path('delete/<int:id>/', views.delete_student, name='delete_student'),
    path('delete-selected-students/', views.delete_selected_students, name='delete_selected_students'),
    path('update-student/<int:id>/', views.update_student, name='update_student'),
    path('upload-csv/', views.upload_students, name='upload_students'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path('student-profile/receipts/fee/<int:fee_id>/', views.student_fee_receipt_pdf, name='student_fee_receipt_pdf'),
    path('student-profile/receipts/all/', views.student_all_fees_receipt_pdf, name='student_all_fees_receipt_pdf'),
    path('search-students/', views.search_students, name='search_students'),

    # Teacher Management
    path('create-teacher/', views.create_teacher, name='create_teacher'),
    path('update-teacher/<int:teacher_id>/', views.update_teacher, name='update_teacher'),
    path('delete-teacher/<int:teacher_id>/', views.delete_teacher_ajax, name='delete_teacher_ajax'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-password/<int:teacher_id>/', views.change_password, name='change_teacher_password'),
    path('download_merged_combined_pdf/', views.download_merged_combined_pdf, name='download_merged_combined_pdf'),

    # Subject Management
    path('create-subject/', views.create_subject, name='create_subject'),
    path('delete-subject/<int:id>/', views.delete_subject, name='delete_subject'),
    path('update-subject/<int:id>/', views.update_subject, name='update_subject'),
    path('required-subjects/', views.required_subjects_view, name='required_subjects'),
    path('exclude/', views.exclude_subject, name='exclude_subject'),
    path('delete_excluded_subject/<int:id>/', views.delete_excluded_subject, name='delete_excluded_subject'),

    path('update_teacher_subject/<int:id>/', views.update_teacher_subject, name='update_teacher_subject'),
    path('delete_assigned_teacher/<int:id>/', views.delete_assigned_teacher, name='delete_assigned_teacher'),

    # Teacher-Subject Assignment
    path('assign-teachers/', views.assign_teachers, name='assign_teachers'),
    path('teacher-subject-list/', views.teacher_subject_list, name='teacher_subject_list'),
    path('delete-assigned-teacher/<int:id>/', views.delete_assigned_teacher, name='delete_assigned_teacher'),
    path('update-assigned-teacher/<int:id>/', views.update_teacher_subject, name='update_assigned_teacher'),
    path('download-student-report/', views.download_student_report, name='download_student_report'),

    # Student-Subject Assignment
    path('students-subjects/', views.create_student_subject, name='create_student_subject'),
    path('list-student-subjects/', views.list_student_subjects, name='list_student_subjects'),
    path('update-student-subjects/<int:id>/', views.update_student_subject, name='update_student_subject'),
    path('delete-student-subject/<int:student_id>/<int:subject_id>/', views.delete_student_subjects, name='delete_student_subject'),
    path('delete-student-subject/<int:student_id>/', views.delete_student_subjects, name='delete_student_subjects'),

    # Class Management
    path('create-class/', views.create_teacher_class, name='create_teacher_class'),
    path('edit-class/<int:id>/', views.edit_class, name='edit_class'),
    path('delete-class/<int:id>/', views.delete_class, name='delete_class'),
    path('select_class/', views.select_class, name='select_class'),
    path('select_class/<int:class_id>/', views.select_class, name='select_class_with_class'),
    path('assign-subjects/<int:class_id>/', views.assign_students_to_subject, name='assign_subjects'),
    path('assign-students/<int:class_id>/', views.assign_students_to_subject, name='assign_students_to_subject'),
    path('base/', views.base, name='base'),

    # Marks and Results
    path('all_student_marks/', views.all_student_marks, name='all_student_marks'),
    path('all_student_marks/<int:class_id>/', views.all_student_marks, name='all_student_marks_with_class'),
    path('fill-marks/<int:teacher_subject_id>/', views.fill_marks, name='fill_marks'),
    path('send_student_sms/', views.send_student_sms, name='send_student_sms'),
    path('send-single-student-sms/', views.send_single_student_sms, name='send_single_student_sms'),
    path('upload-term-marks/', views.upload_term_marks, name='upload_term_marks'),
    path('generate-annual-final-marks/', views.generate_annual_final_marks, name='generate_annual_final_marks'),
    path('ca-based-result/', views.ca_based_result, name='ca_based_result'),
    path('filter_class_results/', views.filter_class_results, name='filter_class_results'),
    path('send_student_emails/', views.send_student_emails, name='send_student_emails'),

    # Grading System
    path('grading_system/', views.grading_system, name='grading_system'),
    path('grading-form/', views.grading_form, name='grading_form'),
    path('update-grading-system/<int:id>/', views.update_grading_system, name='update_grading_system'),
    path('delete-grading-system/<int:id>/', views.delete_grading_system, name='delete_grading_system'),
    path('download_top_ten_subjects_pdf/<int:grade_id>/<int:examination_id>/', views.download_top_ten_subjects_pdf, name='download_top_ten_subjects_pdf_combined'),
    path('grading-form/<int:grading_id>/', views.grading_form, name='grading_form'),

    # Examination Management
    path('exam/list/', views.examination_list, name='examination_list'),
    path('exam/create/', views.examination_create, name='examination_create'),
    path('exam/update/<int:pk>/', views.examination_update, name='examination_update'),
    path('exam/delete/<int:pk>/', views.examination_delete, name='examination_delete'),
    path('select-examination/<int:teacher_subject_id>/', views.select_examination_name, name='select_examination_name'),
    path('change/<int:teacher_subject_id>/', views.change_examination, name='change_examination'),

    # PDF and Excel Downloads
    path('download_pdf/<int:class_id>/<int:grade_id>/<int:examination_name_id>/', views.download_pdf, name='download_pdf'),
    path('download_pdf/<int:class_id>/<int:grade_id>/<int:examination_name_id>/<int:report_id>/', views.download_pdf, name='download_pdf_with_report'),
    path('select_pdf_options/', views.select_pdf_options, name='select_pdf_options'),
    path('download/excel/<int:class_id>/', views.download_excel, name='download_excel'),

    path('download_grade_distribution_pdf/<str:class_ids>/<int:grade_id>/<int:examination_id>/', views.download_grade_distribution_pdf, name='download_grade_distribution_pdf'),
    path('download_top_ten_subjects_pdf/<int:grade_id>/<int:examination_id>/<int:class_id>/', views.download_top_ten_subjects_pdf, name='download_top_ten_subjects_pdf'),
    path(
        'download_top_and_bottom_students_pdf/', 
        views.download_top_and_bottom_students_pdf, 
        name='download_top_and_bottom_students_pdf_all'
    ),

    # URL for downloading PDF filtered by CLASS ONLY
    path(
        'download_top_and_bottom_students_pdf/class/<int:class_id>/', 
        views.download_top_and_bottom_students_pdf, 
        name='download_top_and_bottom_students_pdf_class'
    ),

    # URL for downloading PDF filtered by EXAMINATION ONLY
    path(
        'download_top_and_bottom_students_pdf/exam/<int:examination_id>/', 
        views.download_top_and_bottom_students_pdf, 
        name='download_top_and_bottom_students_pdf_exam'
    ),

    # URL for downloading PDF filtered by BOTH class and examination
    path(
        'download_top_and_bottom_students_pdf/class/<int:class_id>/exam/<int:examination_id>/', 
        views.download_top_and_bottom_students_pdf, 
        name='download_top_and_bottom_students_pdf_class_exam'
    ),

    # Reports and Analysis
    path('top-bottom-students/', views.top_and_bottom_students, name='top_bottom_students'),
    path('top-ten-subjects/', views.top_ten_subjects, name='top_ten_subjects'),
    path('subject-grade-distribution/', views.subject_grade_distribution, name='subject_grade_distribution'),
    path('merge_term_marks_pdfs/<int:class_id>/', views.merge_term_marks_pdfs, name='merge_term_marks_pdfs'),
    path('update_merge_selection/', views.update_merge_selection, name='update_merge_selection'),
    path('generate_annual_final_marks/<int:class_id>/<int:grade_id>/<int:examination_name_id>/', views.generate_annual_final_marks, name='generate_annual_final_marks'),
    path('ca_based_result/<int:class_id>/<int:grade_id>/', views.ca_based_result, name='ca_based_result'),
    # Teacher Dashboard
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teachers/', views.teacher_students_subjects_view, name='teacher_students_subjects_view'),

    # Verification and Display
    path('evaluate/', views.result_evaluation, name='result_evaluation'),
    path('verify/', views.verify_registration_number, name='verify'),
    path('search/', views.search_result, name='search_result'),
    path('display/', views.display, name='display'),
    path('delete_display/<int:id>/', views.delete_display, name='delete_display'),

    # Data Deletion
    path('delete-all-data/<int:class_id>/', views.delete_all_data, name='delete_all_data'),
    path('erase_all_data/', views.delete_all_data, name='erase_all_data'),

    # Authentication
    path('request-otp/<str:purpose>/', views.request_otp, name='request_otp'),
    path('verify-otp/<str:email>/<str:purpose>/', views.verify_otp, name='verify_otp'),
    path('password/reset/<str:email>/', views.password_reset, name='password_reset'),
    path('search/', views.search_result, name='search_result'),
    path('trial/', views.dash, name='trial'),
    path('profile/change-photo/', views.change_profile_photo, name='change_profile_photo'),

    path('update-student-subjects/<int:id>/', views.update_student_subject, name='update_student_subject'),
    path('delete-student-subject/<int:student_id>/<int:subject_id>/', views.delete_student_subjects, name='delete_student_subject'),

    path('download_combined_pdf/<int:class_id>/<int:grade_id>/<int:examination_name_id>/', views.download_combined_pdf, name='download_combined_pdf'),
    path('download_combined_pdf/<int:class_id>/<int:grade_id>/<int:examination_name_id>/<str:report_id>/', views.download_combined_pdf, name='download_combined_pdf'),
    path('download_full_report/<int:class_id>/<int:grade_id>/', views.download_full_report, name='download_full_report'),
    path('download_full_report/<int:class_id>/<int:grade_id>/<str:report_id>/', views.download_full_report, name='download_full_report'),

    path('merge_term_marks_with_financial/<int:class_id>/<int:grade_id>/', 
         views.merge_term_marks_with_financial, name='merge_term_marks_with_financial'),
    
    path('generate_annual_final_marks_with_financial/<int:class_id>/<int:grade_id>/<int:examination_name_id>/', views.generate_annual_final_marks_with_financial, name='generate_annual_final_marks_with_financial'),
    path('ca_based_result_with_financial/<int:class_id>/<int:grade_id>/', views.ca_based_result_with_financial, name='ca_based_result_with_financial'),
    
    path('required-subjects/update/<int:id>/', views.update_required_subject, name='update_required_subject'),
    path('required-subjects/delete/<int:id>/', views.delete_required_subject, name='delete_required_subject'),

    # ...existing code...
    path('download_ca_result_pdf/<int:class_id>/<int:grade_id>/', views.download_ca_result_pdf, name='download_ca_result_pdf'),
    path('download_ca_result_pdf/<int:class_id>/<int:grade_id>/<int:report_id>/', views.download_ca_result_pdf, name='download_ca_result_pdf'),
    path('download_final_result_pdf/<int:class_id>/<int:grade_id>/', views.download_final_result_pdf, name='download_final_result_pdf'),
    path('download_final_result_pdf/<int:class_id>/<int:grade_id>/<int:report_id>/', views.download_final_result_pdf, name='download_final_result_pdf'),
    path('download_pdf/<int:class_id>/<int:grade_id>/<int:examination_name_id>/<int:report_id>/', views.download_pdf, name='download_pdf_with_report'),
    path('download_top_ten_subjects_pdf/<int:grade_id>/<int:examination_id>/<str:class_ids>/', views.download_top_ten_subjects_pdf, name='download_top_ten_subjects_pdf'),

    path('download/ca-result-financial/<int:class_id>/<int:grade_id>/', views.download_ca_result_financial_pdf, name='download_ca_result_financial_pdf'),
    path('download/final-result-financial/<int:class_id>/<int:grade_id>/', views.download_final_result_financial_pdf, name='download_final_result_financial_pdf'),

    path('upload-marks/<int:teacher_subject_id>/', views.upload_marks, name='upload_marks'),
    path('update_staff_profile/', views.change_teacher_photo, name='change_teacher_photo'),
    path('teacher/profile/', views.teacher_profile, name='teacher_profile'),
    path('update/teacher/profile/', views.change_teacher_photo, name='update_teacher_profile'),  # Update photo (POST only, but handle GET gracefully)

    path('remark-ranges/', views.manage_remark_ranges, name='manage_remark_ranges'),
    path('remark-ranges/update/<int:pk>/', views.update_remark_range, name='update_remark_range'),
    path('remark-ranges/delete/<int:pk>/', views.delete_remark_range, name='delete_remark_range'),
    path('manage-source-document/', views.manage_source_document, name='manage_source_document'),

    path('division-summary/', views.division_summary, name='division_summary'),
    # Fixed URL pattern: Use <str:class_ids> for comma-separated IDs and match JS prefix
    path('download_division_summary_pdf/<str:class_ids>/<int:grade_id>/<int:examination_id>/', 
         views.download_division_summary_pdf, name='download_division_summary_pdf'),

    path('callback/', views.snippe_callback, name='snippe_callback'),
    
    # New paths
    path('payment/', views.payment_form, name='payment_form'),
    path('payment/success/<str:transaction_id>/', views.payment_success, name='payment_success'),
    path('payment/status/<str:transaction_id>/', views.payment_status, name='payment_status'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('export-students-excel/<int:class_id>/', views.export_students_excel, name='export_students_excel'),
    path('export-students-pdgf/<int:class_id>/', views.export_students_pdf, name='export_students_pdf'),

    path('composite-subjects/', views.composite_subjects_view, name='composite_subjects'),
    path('composite-subjects/update/<int:id>/', views.update_composite_subject, name='update_composite_subject'),
    path('composite-subjects/delete/<int:id>/', views.delete_composite_subject, name='delete_composite_subject'),

    path('permissions/teachers/', views.manage_teacher_permissions, name='manage_teacher_permissions'),
    path('permissions/teachers/update/', views.update_teacher_permissions, name='update_teacher_permissions'),
    path('app/', views.dash, name='dash'),

    path('crm/', views.crm_lead_list_create, name='crm_lead_list'),
    path('crm/<int:pk>/edit/', views.crm_lead_update, name='crm_lead_update'),
    path('crm/<int:pk>/delete/', views.crm_lead_delete, name='crm_lead_delete'),
    path('home-enquiries/', views.home_enquiry_list, name='home_enquiries'),
    path('home-enquiries/<int:pk>/update/', views.home_enquiry_update, name='home_enquiry_update'),

    path('transport/dashboard/', views.transport_dashboard, name='transport_dashboard'),
    path('transport/vehicles/', views.vehicle_list, name='vehicle_list'),
    path('transport/vehicles/create/', views.vehicle_create, name='vehicle_create'),
    path('transport/vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('transport/vehicles/<int:pk>/update/', views.vehicle_update, name='vehicle_update'),
    path('transport/vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('transport/routes/', views.route_list, name='route_list'),
    path('transport/routes/create/', views.route_create, name='route_create'),
    path('transport/routes/<int:pk>/update/', views.route_update, name='route_update'),
    path('transport/routes/<int:pk>/delete/', views.route_delete, name='route_delete'),
    path('transport/fuel-records/', views.fuel_record_list, name='fuel_record_list'),
    path('transport/fuel-records/create/', views.fuel_record_create, name='fuel_record_create'),
    path('transport/fuel-records/<int:pk>/update/', views.fuel_record_update, name='fuel_record_update'),
    path('transport/fuel-records/<int:pk>/delete/', views.fuel_record_delete, name='fuel_record_delete'),
    path('transport/maintenance/', views.maintenance_list, name='maintenance_list'),
    path('transport/maintenance/create/', views.maintenance_create, name='maintenance_create'),
    path('transport/maintenance/<int:pk>/update/', views.maintenance_update, name='maintenance_update'),
    path('transport/maintenance/<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),
    path('transport/expenses/', views.vehicle_expense_list, name='vehicle_expense_list'),
    path('transport/expenses/create/', views.vehicle_expense_create, name='vehicle_expense_create'),
    path('transport/expenses/<int:pk>/update/', views.vehicle_expense_update, name='vehicle_expense_update'),
    path('transport/expenses/<int:pk>/delete/', views.vehicle_expense_delete, name='vehicle_expense_delete'),

    # CHAT PATHS (CORRECTED FOR REAL-TIME SUPPORT)
    # CHAT PATHS — ORDER MATTERS!
    path('chat/upload-file/', views.upload_chat_file, name='upload_chat_file'),  # ← MUST COME FIRST
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/room/<path:receiver_username>/', views.chat_room, name='chat_room'),     # ← Dynamic — must be last
    path('chat/<path:receiver_username>/', views.chat_room, name='chat_room'),     # ← Dynamic — must be last

    path('create-teacher-stream/', views.create_teacher_stream, name='create_teacher_stream'),
    path('update-teacher-stream/', views.update_teacher_stream, name='update_teacher_stream'),
    path('delete-teacher-stream/<int:stream_id>/', views.delete_teacher_stream, name='delete_teacher_stream'),
    path('lock/<str:username>/',views.lock_account,name='lock_account'),

    path('get_teacher/<int:teacher_id>/', views.get_teacher, name='get_teacher'),
    path('update_teacher/<int:teacher_id>/', views.update_teacher, name='update_teacher'),
    path('delete_teacher_ajax/<int:teacher_id>/', views.delete_teacher_ajax, name='delete_teacher_ajax'),

    path('students/index-number/', views.generate_student_index_number, name='generate_student_index_number'),
    path('students/<int:student_id>/short-course-validity/', views.update_short_course_validity, name='update_short_course_validity'),
    path('students/<int:student_id>/id-card/', views.student_id_card_view, name='student_id_card_view'),
    path('students/<int:student_id>/id-card/pdf/', views.student_id_card_pdf_view, name='student_id_card_pdf_view'),
    path('students/<int:student_id>/id-card/png/', views.student_id_card_png_view, name='student_id_card_png_view'),
    path('students/<int:student_id>/id-card/public-url/', views.student_public_qr_url, name='student_public_qr_url'),
    path('students/<int:student_id>/id-card/appearance-defaults/', views.student_id_appearance_defaults_view, name='student_id_appearance_defaults'),
    path('student-id-settings/', views.student_id_settings, name='student_id_settings'),
    path('students/<int:student_id>/information/page/', views.student_information_page, name='student_information_page'),
    path('students/<int:student_id>/information/', views.student_information_modal, name='student_information_modal'),
    path('students/<int:student_id>/information/save/', views.save_student_information, name='save_student_information'),
    path('students/<int:student_id>/information/delete/<str:model_key>/<int:record_id>/', views.delete_student_information, name='delete_student_information'),
    path('students/information/import/<str:model_key>/', views.import_student_information, name='import_student_information'),

    path('teachers/<int:teacher_id>/information/', views.teacher_information_modal, name='teacher_information_modal'),
    path('teachers/<int:teacher_id>/information/save/', views.save_teacher_information, name='save_teacher_information'),
    path('teachers/<int:teacher_id>/information/delete/<str:model_key>/<int:record_id>/', views.delete_teacher_information, name='delete_teacher_information'),
    path('teachers/information/import/<str:model_key>/', views.import_teacher_information, name='import_teacher_information'),
    path('public/id-card/student/<str:token>/', views.public_student_id_details, name='public_student_id_details'),
    path('public/student-result/', views.public_student_qr_result, name='public_student_qr_result'),
    path('public/student-result/report/', views.public_student_qr_report_download, name='public_student_qr_report_download'),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
