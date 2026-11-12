from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def determine_attendance_status(is_checked, check_in_time=None, cutoff_time=None, current_status=None):
    if current_status == "excused":
        return "excused"
    if not is_checked:
        return "absent"
    if cutoff_time and check_in_time and check_in_time > cutoff_time:
        return "late"
    return "present"


def apply_common_attendance_filters(queryset, cleaned_data):
    status = cleaned_data.get("status")
    from_time = cleaned_data.get("from_time")
    to_time = cleaned_data.get("to_time")
    late_only = cleaned_data.get("late_only")
    arrived_after = cleaned_data.get("arrived_after")
    date_from = cleaned_data.get("date_from")
    date_to = cleaned_data.get("date_to")

    if status:
        queryset = queryset.filter(attendance_status=status)
    if late_only:
        queryset = queryset.filter(attendance_status="late")
    if from_time:
        queryset = queryset.filter(check_in_time__gte=from_time)
    if to_time:
        queryset = queryset.filter(check_in_time__lte=to_time)
    if arrived_after:
        queryset = queryset.filter(check_in_time__gt=arrived_after)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    return queryset


def status_totals(records):
    total = records.count()
    present = records.filter(attendance_status="present").count()
    absent = records.filter(attendance_status="absent").count()
    late = records.filter(attendance_status="late").count()
    excused = records.filter(attendance_status="excused").count()
    attendance_rate = round(((present + late) / total) * 100, 2) if total else 0
    return {
        "total": total,
        "present": present,
        "absent": absent,
        "late": late,
        "excused": excused,
        "percentage": attendance_rate,
    }


def build_attendance_pdf_response(filename, title, filters_summary, rows, summary, is_staff=False):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    elems = [
        Paragraph("School Attendance System", styles["Title"]),
        Paragraph(title, styles["Heading2"]),
        Paragraph(f"Generated: {timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]),
        Paragraph(filters_summary, styles["Normal"]),
        Spacer(1, 12),
    ]

    headers = ["No.", "Name", "Identifier", "Date", "Check-in", "Check-out", "Status"]
    table_data = [headers]
    for idx, item in enumerate(rows, start=1):
        obj = item["obj"]
        person = item["person"]
        name = person.teacherName if is_staff else person.fullName
        identifier = person.teacher_key if is_staff else (person.indexNumber or "-")
        table_data.append([
            idx,
            name,
            identifier,
            obj.date.strftime("%Y-%m-%d") if obj.date else "-",
            obj.check_in_time.strftime("%H:%M") if obj.check_in_time else "-",
            obj.check_out_time.strftime("%H:%M") if obj.check_out_time else "-",
            (obj.attendance_status or obj.status or "-").title(),
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
    ]))
    elems.append(table)
    elems.append(Spacer(1, 12))
    elems.append(Paragraph(
        f"Total: {summary['total']} | Present: {summary['present']} | Late: {summary['late']} | "
        f"Absent: {summary['absent']} | Excused: {summary['excused']} | Attendance %: {summary['percentage']}%",
        styles["Normal"],
    ))
    doc.build(elems)
    return response
