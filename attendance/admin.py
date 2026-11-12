from django.contrib import admin

# Register your models here.
# rps_app/admin.py
from django.contrib import admin
from .models import StudentAttendance, Student,StaffAttendance

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'user', 'date', 'status', 'check_in_time', 'check_out_time')
    list_filter = ('status', 'date', 'user')  # filters in sidebar
    search_fields = ('student__fullName', 'user__username')  # search by student name or user
    date_hierarchy = 'date'  # top-level date navigation
    ordering = ('-date', 'student')  # latest first



@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'teacher',
        'date',
        'status',
        'check_in_time',
        'check_out_time',
        'user',
    )
    list_filter = ('status', 'date', 'teacher')
    search_fields = ('teacher__name', 'user__username')
    ordering = ('-date',)
    date_hierarchy = 'date'
