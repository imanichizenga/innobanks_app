from django.conf import settings
from django.db import models
from datetime import date
from rps_app.models import Student, Teacher


ATTENDANCE_STATUS_CHOICES = [
    ("present", "Present"),
    ("absent", "Absent"),
    ("late", "Late"),
    ("excused", "Excused"),
]


class StudentAttendance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Teacher/admin who recorded attendance",
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=10, choices=[("present", "P"), ("absent", "A")], default="absent")
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "date")
        verbose_name = "Student Attendance"
        verbose_name_plural = "Students Attendance"


class StaffAttendance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Teacher/admin who recorded attendance",
    )
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="teacher_attendance")
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=10, choices=[("present", "P"), ("absent", "A")], default="absent")
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("teacher", "date")
        verbose_name = "Teacher Attendance"
        verbose_name_plural = "Teachers Attendance"


class ManualStudentAttendance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Teacher/admin who recorded attendance",
        null=True,
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="manual_attendances",
        null=True,
    )
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default="absent")
    attendance_status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default="absent", null=True, blank=True)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    late_cutoff_time = models.TimeField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        unique_together = ("student", "date")
        verbose_name = "Manual Student Attendance"
        verbose_name_plural = "Manual Students Attendance"

    def save(self, *args, **kwargs):
        if not self.attendance_status:
            self.attendance_status = self.status
        self.status = self.attendance_status or self.status
        super().save(*args, **kwargs)


class ManualStaffAttendance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Teacher/admin who recorded attendance",
        null=True,
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="manual_teacher_attendance",
        null=True,
    )
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default="absent")
    attendance_status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default="absent", null=True, blank=True)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    late_cutoff_time = models.TimeField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        unique_together = ("teacher", "date")
        verbose_name = "Manual Teacher Attendance"
        verbose_name_plural = "Manual Teachers Attendance"

    def save(self, *args, **kwargs):
        if not self.attendance_status:
            self.attendance_status = self.status
        self.status = self.attendance_status or self.status
        super().save(*args, **kwargs)
