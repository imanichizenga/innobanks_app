
# @login_required
# def all_student_marks(request, class_id=None):
#     classes = TeacherClass.objects.filter(user=request.user)
#     grades = GradingModel.objects.filter(user=request.user)
#     display = DisplayModel.objects.filter(user=request.user)

#     if request.method == 'POST' or class_id:
#         class_id = request.POST.get('class_id', class_id)
#         grade_id = request.POST.get('grade_id')
#         report_id = request.POST.get('report_id')

#         if not class_id or not grade_id or not TeacherClass.objects.filter(id=class_id, user=request.user).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}.")
#             return render(request, 'all_student_marks.html', {
#                 'grades': grades,
#                 'display': display,
#                 'classes': classes
#             })

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user)
#         grading_required = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         report_display = DisplayModel.objects.filter(id=report_id, user=request.user).first() if report_id and DisplayModel.objects.filter(id=report_id, user=request.user).exists() else None

#         if grading_required.is_advance:
#             exclude_subjects = ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True)
#             grade_thresholds = {
#                 grading_required.grade_a: 'A',
#                 grading_required.grade_b: 'B',
#                 grading_required.grade_c: 'C',
#                 grading_required.grade_d: 'D',
#                 grading_required.grade_e: 'E',
#                 grading_required.grade_s: 'S',
#                 grading_required.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         else:
#             exclude_subjects = []
#             grade_thresholds = {
#                 grading_required.grade_a: 'A',
#                 grading_required.grade_b: 'B',
#                 grading_required.grade_c: 'C',
#                 grading_required.grade_d: 'D',
#                 grading_required.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#         subjects = Subject.objects.filter(user=request.user)
#         if not subjects.exists():
#             logger.warning(f"No subjects found for TeacherClass {teacherclass.ClassName}")
#             messages.warning(request, f"No subjects defined for '{teacherclass.ClassName}'. Add subjects to proceed.")

#         students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#             Prefetch('marks', queryset=Mark.objects.filter(teacherclass=teacherclass).select_related('subject'))
#         )
#         if not students.exists():
#             logger.warning(f"No students found for TeacherClass {teacherclass.ClassName}")
#             messages.warning(request, f"No students enrolled in '{teacherclass.ClassName}'.")

#         students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#             total_marks=Sum('marks__marks'),
#             average_marks=Avg('marks__marks')
#         )

#         marks_evaluation_dict = {
#             s.id: {
#                 'total_marks': s.total_marks or 0,
#                 'average_marks': s.average_marks or 0
#             } for s in students_marks_evaluation
#         }

#         division_thresholds = [
#             {'max': grading_required.division_1, 'label': 'I'},
#             {'max': grading_required.division_2, 'label': 'II'},
#             {'max': grading_required.division_3, 'label': 'III'},
#             {'max': grading_required.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         student_data = []
#         for student in students:
#             student_marks = []
#             all_grades = []
#             grades_for_division = []

#             student_subjects_with_marks = Mark.objects.filter(student=student, teacherclass=teacherclass).select_related('subject')
#             subject_ids_with_marks = student_subjects_with_marks.values_list('subject_id', flat=True)

#             for subject in subjects:
#                 mark_obj = student.marks.filter(subject=subject, teacherclass=teacherclass).first()
#                 mark_value = mark_obj.marks if mark_obj else None
#                 grade = '-'
#                 if mark_value is not None:
#                     for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                         if mark_value >= threshold:
#                             grade = letter_grade
#                             break
#                 if mark_value is not None:
#                     student_marks.append({
#                         'subject': subject.id,
#                         'subject_name': subject.nameSubject,
#                         'mark': mark_value,
#                         'grade': grade,
#                         'is_excluded': subject.id in exclude_subjects
#                     })
#                 all_grades.append(grade)
#                 if not grading_required.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)

#             logger.debug(f"Student {student.fullName} marks: {student_marks}")

#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)

#             if grading_required.is_advance and num_valid_subjects < 3:
#                 division = "Inc"
#                 total_points = 0
#             elif not grading_required.is_advance and num_valid_subjects < 7:
#                 division = "Inc"
#                 total_points = 0
#             else:
#                 sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:3 if grading_required.is_advance else 7]
#                 total_points = sum(grade_points[g] for g in sorted_grades)
#                 division = 'IV'
#                 for threshold in division_thresholds:
#                     if total_points <= threshold['max']:
#                         division = threshold['label']
#                         break

#             student_average = marks_evaluation_dict.get(student.id, {}).get('average_marks', 0)
#             overall_grade = 'F'
#             for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                 if student_average >= threshold:
#                     overall_grade = letter_grade
#                     break

#             has_valid_marks = any(grade != '-' for grade in all_grades)

#             student_data.append({
#                 'id': student.id,
#                 'fullName': student.fullName,
#                 'sex': student.sex,
#                 'indexNumber': student.indexNumber,
#                 'marks': student_marks,
#                 'total_marks': marks_evaluation_dict.get(student.id, {}).get('total_marks', 0),
#                 'average_marks': student_average,
#                 'grade': overall_grade,
#                 'division': division,
#                 'total_points': total_points,
#                 'has_valid_marks': has_valid_marks
#             })

#         student_data.sort(key=lambda x: (-x['has_valid_marks'], -x['average_marks']))
#         for position, student in enumerate(student_data, 1):
#             student['position'] = position

#         context = {
#             'students': student_data,
#             'subjects': subjects,
#             'display': [report_display] if report_display else display[:1],
#             'teacherclass': teacherclass,
#             'classes': classes,
#             'grades': grades,
#             'grading_required': grading_required,  # Add this to ensure grade_id is available
#             'exclude_subjects': list(exclude_subjects) if grading_required.is_advance else [],
#         }
#         logger.debug(f"Context prepared: {len(student_data)} students, {len(subjects)} subjects")
#         return render(request, 'all_student_marks.html', context)

#     return render(request, 'grading_system.html', {
#         'grades': grades,
#         'display': display,
#         'classes': classes
#     })

    
# @login_required
# def download_pdf(request, class_id, grade_id, report_id=''):
#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user)
#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related('marks')
#     subjects = Subject.objects.filter(user=request.user)
#     grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     display = DisplayModel.objects.filter(id=report_id, user=request.user).first() if report_id else DisplayModel.objects.filter(user=request.user).first()

#     if grading.is_advance:
#         exclude_subjects = ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True)
#         grade_thresholds = {
#             grading.grade_a: 'A',
#             grading.grade_b: 'B',
#             grading.grade_c: 'C',
#             grading.grade_d: 'D',
#             grading.grade_e: 'E',
#             grading.grade_s: 'S',
#             grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#     else:
#         exclude_subjects = []
#         grade_thresholds = {
#             grading.grade_a: 'A',
#             grading.grade_b: 'B',
#             grading.grade_c: 'C',
#             grading.grade_d: 'D',
#             grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="student_report_{teacherclass.ClassName or "Unnamed_Class"}.pdf"'
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()
#     header_style = styles['Heading1']
#     subheader_style = styles['Heading2']
#     body_style = styles['BodyText']
#     header_style.alignment = 1
#     subheader_style.alignment = 1
#     body_style.alignment = 1
#     body_style.fontSize = 7

#     def get_grade(mark):
#         if mark is None:
#             return '-'
#         for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#             if mark >= threshold:
#                 return grade
#         return 'F'

#     division_thresholds = [
#         {'max': grading.division_1, 'label': 'I'},
#         {'max': grading.division_2, 'label': 'II'},
#         {'max': grading.division_3, 'label': 'III'},
#         {'max': grading.division_4, 'label': 'IV'},
#         {'max': float('inf'), 'label': '0'}
#     ]

#     def get_division(grades_for_division):
#         filtered_grades = [g for g in grades_for_division if g != '-']
#         num_valid_subjects = len(filtered_grades)
#         if grading.is_advance and num_valid_subjects < 3:
#             return "Inc", 0
#         elif not grading.is_advance and num_valid_subjects < 7:
#             return "Inc", 0
#         else:
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:3 if grading.is_advance else 7]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break
#             return division, total_points

#     if display:
#         elements.append(Paragraph(display.header or "Student Performance Report", header_style))
#         elements.append(Spacer(1, 4))
#         elements.append(Paragraph(display.body or f"Comprehensive Academic Summary - {teacherclass.ClassName}", subheader_style))
#     else:
#         elements.append(Paragraph(f"Results for {teacherclass.ClassName or 'Unnamed Class'}", header_style))
#     elements.append(Spacer(1, 8))

#     if not students.exists() or not subjects.exists():
#         elements.append(Paragraph("No data available for this class.", body_style))
#     else:
#         # Prepare student data for sorting
#         students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#             total_marks=Sum('marks__marks'),
#             average_marks=Avg('marks__marks')
#         )
#         student_totals = []
#         for student in students_marks_evaluation:
#             total_marks = student.total_marks or 0
#             average_marks = student.average_marks or 0
#             grades = []
#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject).first()
#                 mark_value = mark.marks if mark else None
#                 grade = get_grade(mark_value)
#                 grades.append(grade)
#             has_valid_marks = any(grade != '-' for grade in grades)
#             student_totals.append((student, total_marks, average_marks, has_valid_marks))

#         # Sort students: those with valid marks by average (descending), then those without valid marks at the bottom
#         student_totals.sort(key=lambda x: (-x[3], -x[2]))  # Sort by has_valid_marks (descending), then average_marks (descending)

#         # Overall table
#         overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] + 
#                         [s.nameSubject for s in subjects] + 
#                         ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]

#         for i, (student, total_marks, average_marks, _) in enumerate(student_totals, 1):
#             row = [str(i), student.fullName or 'Unnamed', student.sex or '-', student.indexNumber or '-']
#             grades_for_division = []

#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject).first()
#                 mark_value = mark.marks if mark else None
#                 grade = get_grade(mark_value)
#                 sub_table = Table([[str(mark_value) if mark_value is not None else '-', grade]], colWidths=[10, 12], hAlign='CENTER')
#                 sub_table.setStyle(TableStyle([
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 4),
#                     ('LEADING', (0, 0), (-1, -1), 8),
#                     ('TEXTCOLOR', (1, 0), (1, 0), colors.red if grade == 'F' else colors.black),
#                 ]))
#                 row.append(sub_table)
#                 if not grading.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)

#             overall_grade = get_grade(average_marks)
#             division, total_points = get_division(grades_for_division)

#             row.extend([total_marks if total_marks > 0 else '-', f"{average_marks:.2f}" if average_marks > 0 else '-',
#                         overall_grade, str(i), division, total_points if total_points > 0 else '-'])
#             overall_data.append(row)

#         total_columns = len(overall_data[0])
#         available_width = A4[0] - 30
#         base_width = available_width / total_columns
#         col_widths = ([base_width * 0.5] + [base_width * 3.0] + [base_width * 0.5] + [base_width * 2.0] + 
#                       [base_width * 1.0] * len(subjects) + [base_width * 0.7] * 6)

#         overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#         overall_table.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 6),
#             ('LEADING', (0, 0), (-1, -1), 8),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#         ]))
#         elements.append(KeepTogether(overall_table))
#         elements.append(Spacer(1, 10))

#         # Individual student reports (same order as the overall table)
#         for i, (student, total_marks, average_marks, _) in enumerate(student_totals):
#             if i > 0:
#                 elements.append(PageBreak())
#             elements.append(Paragraph(f"Student: {student.fullName or 'Unnamed Student'}", subheader_style))
#             elements.append(Spacer(1, 6))

#             student_data = [['Subject', 'Marks', 'Grade', 'Teacher', 'Signature', 'Status']]
#             grades_for_division = []

#             student_marks = student.marks.filter(teacherclass=teacherclass)
#             for mark in student_marks:
#                 subject = mark.subject
#                 mark_value = mark.marks
#                 grade = get_grade(mark_value)
#                 student_data.append([subject.nameSubject or 'Unnamed', str(mark_value), grade, '-', '-', '-'])
#                 if not grading.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)

#             if len(student_data) == 1:
#                 student_data.append(['No subjects with marks available', '-', '-', '-', '-', '-'])

#             student_table = Table(student_data, colWidths=[120, 40, 40, 60, 40, 25], splitByRow=True, repeatRows=1)
#             student_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.append(student_table)

#             overall_grade = get_grade(average_marks)
#             division, total_points = get_division(grades_for_division)
#             avg_display = f"{average_marks:.2f}" if average_marks > 0 else '-'
#             summary = f"Position: {i + 1} | Avg: {avg_display} | Total: {total_marks if total_marks > 0 else '-'} | Division: {division} | Points: {total_points if total_points > 0 else '-'}" 
#             elements.append(Spacer(1, 6))
#             elements.append(Paragraph(summary, body_style))

#     elements.append(Spacer(1, 10))
#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", body_style))

#     doc.build(elements)
#     return response

# @login_required
# def generate_annual_final_marks(request, class_id=None):
#     classes = TeacherClass.objects.filter(user=request.user)
#     grades = GradingModel.objects.filter(user=request.user)

#     context = {
#         'classes': classes,
#         'grades': grades,
#     }

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')

#         if not class_id or not grade_id or not TeacherClass.objects.filter(id=class_id, user=request.user).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}.")
#             return render(request, 'generate_annual_final_marks.html', context)

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user)
#         grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['selected_grade_id'] = grade_id

#         if grading.is_advance:
#             exclude_subjects = ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True)
#             grade_thresholds = {
#                 grading.grade_a: 'A',
#                 grading.grade_b: 'B',
#                 grading.grade_c: 'C',
#                 grading.grade_d: 'D',
#                 grading.grade_e: 'E',
#                 grading.grade_s: 'S',
#                 grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         else:
#             exclude_subjects = []
#             grade_thresholds = {
#                 grading.grade_a: 'A',
#                 grading.grade_b: 'B',
#                 grading.grade_c: 'C',
#                 grading.grade_d: 'D',
#                 grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#         division_thresholds = [
#             {'max': grading.division_1, 'label': 'I'},
#             {'max': grading.division_2, 'label': 'II'},
#             {'max': grading.division_3, 'label': 'III'},
#             {'max': grading.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         term_uploads = TermMarksUpload.objects.filter(
#             user=request.user, 
#             teacherclass=teacherclass, 
#             for_merging_pdf=False
#         )
#         if not term_uploads.exists():
#             messages.error(request, "No unchecked term marks PDFs available for generating final marks.")
#             return render(request, 'generate_annual_final_marks.html', context)

#         term_data = {}
#         subjects_set = set()
#         for upload in term_uploads:
#             pdf_path = upload.pdf_file.path
#             if not os.path.exists(pdf_path):
#                 messages.error(request, f"PDF file for {upload.term_name} not found at {pdf_path}.")
#                 return render(request, 'generate_annual_final_marks.html', context)

#             dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True)
#             if not dfs:
#                 messages.error(request, f"No tables found in {upload.term_name} PDF.")
#                 return render(request, 'generate_annual_final_marks.html', context)

#             df = dfs[0].dropna(how='all')
#             df.columns = df.columns.str.strip()
#             if all(col not in df.columns for col in ['S/No', 'Student Name', 'Sex', 'Index No']):
#                 messages.error(request, f"Missing required headers in {upload.term_name} PDF.")
#                 return render(request, 'generate_annual_final_marks.html', context)

#             df = df.rename(columns={'S/No': 'S/No', 'Student Name': 'fullName', 'Sex': 'sex', 'Index No': 'indexNumber'})
#             term_data[upload.term_name] = df
#             excluded_cols = ['S/No', 'fullName', 'sex', 'indexNumber', 'Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']
#             subjects_set.update([col for col in df.columns if col not in excluded_cols])

#         subjects_db = Subject.objects.filter(user=request.user)
#         students = Student.objects.filter(teacherclass=teacherclass)
#         student_data = []

#         def get_grade(mark):
#             if pd.isna(mark) or mark is None or mark == 0:
#                 return '-'
#             for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#                 if mark >= threshold:
#                     return grade
#             return 'F'

#         def get_division(grades_for_division):
#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)
#             if grading.is_advance and num_valid_subjects < 3:
#                 return "Inc", 0
#             elif not grading.is_advance and num_valid_subjects < 7:
#                 return "Inc", 0
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:3 if grading.is_advance else 7]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break
#             return division, total_points

#         for student in students:
#             student_dict = {'id': student.id, 'fullName': student.fullName, 'sex': student.sex, 'indexNumber': student.indexNumber}
#             marks_list = []
#             total_marks = 0
#             subject_count = 0

#             for subject in subjects_db:
#                 if subject.nameSubject in subjects_set:
#                     marks = []
#                     for term in term_data.values():
#                         student_row = term[term['indexNumber'] == str(student.indexNumber)]
#                         if not student_row.empty and subject.nameSubject in student_row.columns:
#                             mark = student_row[subject.nameSubject].iloc[0]
#                             try:
#                                 if isinstance(mark, str):
#                                     numeric_part = re.search(r'^\d+\.?\d*', mark)
#                                     mark = float(numeric_part.group()) if numeric_part else 0
#                                 else:
#                                     mark = float(mark) if pd.notna(mark) else 0
#                                 marks.append(mark)
#                             except:
#                                 marks.append(0)

#                     annual_mark = sum(marks) / len(marks) if marks else 0
#                     if annual_mark > 0:
#                         grade = get_grade(annual_mark)
#                         marks_list.append({
#                             'subject_id': subject.id,
#                             'subject_name': subject.nameSubject,
#                             'mark': annual_mark,
#                             'grade': grade,
#                             'is_excluded': subject.id in exclude_subjects
#                         })
#                         total_marks += annual_mark
#                         subject_count += 1

#             student_dict['marks'] = marks_list
#             student_dict['total_marks'] = total_marks
#             student_dict['average_marks'] = total_marks / subject_count if subject_count > 0 else 0
#             student_dict['grade'] = get_grade(student_dict['average_marks'])

#             grades_for_division = [m['grade'] for m in marks_list if not m['is_excluded']]
#             division, total_points = get_division(grades_for_division)
#             student_dict['division'] = division
#             student_dict['total_points'] = total_points

#             student_data.append(student_dict)

#         student_data.sort(key=lambda x: x['average_marks'], reverse=True)
#         for i, student in enumerate(student_data, 1):
#             student['position'] = i

#         response = HttpResponse(content_type='application/pdf')
#         filename = f"annual_final_marks_{teacherclass.ClassName}_{datetime.now().strftime('%Y%m%d')}.pdf"
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#         elements = []
#         styles = getSampleStyleSheet()
#         header_style, subheader_style, body_style = styles['Heading1'], styles['Heading2'], styles['BodyText']
#         header_style.alignment = subheader_style.alignment = body_style.alignment = 1
#         body_style.fontSize = 7

#         elements.append(Paragraph(f"Annual Final Marks for {teacherclass.ClassName}", header_style))
#         elements.append(Spacer(1, 8))

#         if not student_data:
#             elements.append(Paragraph("No data available for this class from unchecked PDFs.", body_style))
#         else:
#             overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] + 
#                            [s.nameSubject for s in subjects_db if s.nameSubject in subjects_set] + 
#                            ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]
            
#             for i, student in enumerate(student_data, 1):
#                 row = [str(i), student['fullName'] or '-', student['sex'] or '-', student['indexNumber'] or '-']
#                 for subject in subjects_db:
#                     if subject.nameSubject in subjects_set:
#                         mark_info = next((m for m in student['marks'] if m['subject_id'] == subject.id), None)
#                         if mark_info:
#                             sub_table = Table([[f"{mark_info['mark']:.2f}", mark_info['grade']]],
#                                             colWidths=[10, 12], hAlign='CENTER')
#                             sub_table.setStyle(TableStyle([
#                                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                                 ('FONTSIZE', (0, 0), (-1, -1), 4),
#                                 ('LEADING', (0, 0), (-1, -1), 8),
#                                 ('TEXTCOLOR', (1, 0), (1, 0), colors.red if mark_info['grade'] == 'F' else colors.black),
#                             ]))
#                             row.append(sub_table)
#                         else:
#                             row.append('-')
                
#                 row.extend([
#                     f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-',
#                     f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-',
#                     student['grade'],
#                     str(student['position']),
#                     student['division'],
#                     student['total_points'] if student['total_points'] > 0 else '-'
#                 ])
#                 overall_data.append(row)

#             total_columns = len(overall_data[0])
#             base_width = (A4[0] - 30) / total_columns
#             col_widths = ([base_width * 0.5] + [base_width * 3.0] + [base_width * 0.5] + [base_width * 2.0] +
#                           [base_width * 1.0] * len([s for s in subjects_db if s.nameSubject in subjects_set]) + [base_width * 0.8] * 6)

#             overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#             overall_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.extend([KeepTogether(overall_table), Spacer(1, 10)])

#         from reportlab.platypus import PageBreak
#         for i, student in enumerate(student_data):
#             if i > 0:
#                 elements.append(PageBreak())
            
#             elements.append(Paragraph(f"Student: {student['fullName'] or 'Unnamed Student'}", subheader_style))
#             elements.append(Spacer(1, 6))

#             student_data_table = [['Subject', 'Marks', 'Grade', 'Teacher', 'Signature', 'Status']]
#             grades_for_division = []

#             for mark in student['marks']:
#                 student_data_table.append([
#                     mark['subject_name'] or 'Unnamed',
#                     f"{mark['mark']:.2f}" if mark['mark'] > 0 else '-',
#                     mark['grade'],
#                     '',  # Placeholder for Teacher
#                     '',  # Placeholder for Signature
#                     ''   # Placeholder for Status
#                 ])
#                 if not mark['is_excluded']:
#                     grades_for_division.append(mark['grade'])

#             if len(student_data_table) == 1:
#                 student_data_table.append(['No subjects with marks available', '-', '-', '', '', ''])

#             student_table = Table(student_data_table, colWidths=[120, 40, 40, 60, 60, 60], splitByRow=True, repeatRows=1)
#             student_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.append(student_table)

#             overall_grade = student['grade']
#             division, total_points = get_division(grades_for_division)
#             avg_display = f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-'
#             total_display = f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-'
#             points_display = str(total_points) if total_points > 0 else '-'
#             summary = f"Position: {student['position']} | Avg: {avg_display} | Total: {total_display} | Division: {division} | Points: {points_display}"
#             elements.append(Spacer(1, 6))
#             elements.append(Paragraph(summary, body_style))

#         elements.append(Spacer(1, 10))
#         elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", body_style))

#         doc.build(elements)
#         return response

#     return render(request, 'generate_annual_final_marks.html', context)


# @login_required
# def merge_term_marks_pdfs(request, class_id=None):
#     classes = TeacherClass.objects.filter(user=request.user)
#     grades = GradingModel.objects.filter(user=request.user)

#     context = {
#         'classes': classes,
#         'grades': grades,
#     }

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')

#         if not class_id or not grade_id or not TeacherClass.objects.filter(id=class_id, user=request.user).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}.")
#             return render(request, 'merge_term_marks_pdfs.html', context)

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user)
#         grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['selected_grade_id'] = grade_id

#         pdf_uploads = TermMarksUpload.objects.filter(
#             user=request.user, 
#             teacherclass=teacherclass,
#             for_merging_pdf=True
#         )
#         if not pdf_uploads.exists():
#             messages.error(request, "No PDFs selected for merging.")
#             logger.error(f"No TermMarksUpload objects marked for merging found for user {request.user} and class {teacherclass}.")
#             return render(request, 'merge_term_marks_pdfs.html', context)

#         if grading.is_advance:
#             exclude_subjects = ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True)
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_e: 'E', grading.grade_s: 'S', grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         else:
#             exclude_subjects = []
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#         division_thresholds = [
#             {'max': grading.division_1, 'label': 'I'},
#             {'max': grading.division_2, 'label': 'II'},
#             {'max': grading.division_3, 'label': 'III'},
#             {'max': grading.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         all_data = []
#         subjects_set = set()
#         student_data_dict = {}

#         for upload in pdf_uploads:
#             pdf_path = upload.pdf_file.path
#             if not os.path.exists(pdf_path):
#                 messages.error(request, f"PDF file not found at {pdf_path}.")
#                 logger.error(f"PDF not found: {pdf_path}")
#                 continue
                
#             try:
#                 dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True, guess=False)
#                 if not dfs:
#                     messages.error(request, f"No tables found in PDF at {pdf_path}.")
#                     logger.error(f"No tables in PDF: {pdf_path}")
#                     continue

#                 pdf_dfs = []
#                 for i, df in enumerate(dfs):
#                     df = df.dropna(how='all')
#                     if df.empty:
#                         logger.warning(f"Table {i} in PDF {pdf_path} is empty after dropping NA.")
#                         continue
#                     df.columns = df.columns.str.strip().str.lower()
#                     df = df.rename(columns={'s/no': 's_no', 'student name': 'fullname', 'sex': 'sex', 'index no': 'indexnumber'})
#                     logger.debug(f"Table {i} in PDF {pdf_path} - Columns: {list(df.columns)}")
#                     logger.debug(f"Table {i} in PDF {pdf_path} - Number of students: {len(df)}")
#                     pdf_dfs.append(df)

#                 if not pdf_dfs:
#                     messages.error(request, f"No valid tables found in PDF at {pdf_path}.")
#                     logger.error(f"No valid tables in PDF: {pdf_path}")
#                     continue

#                 df = pd.concat(pdf_dfs, ignore_index=True)
#                 logger.debug(f"PDF {pdf_path} - Total students after concatenation: {len(df)}")
#                 subjects_set.update([col for col in df.columns if col not in ['s_no', 'fullname', 'sex', 'indexnumber', 'total', 'avg', 'grade', 'pos', 'div', 'pts']])
#                 all_data.append(df)

#             except Exception as e:
#                 messages.error(request, f"Error processing PDF at {pdf_path}: {str(e)}")
#                 logger.error(f"Error processing PDF {pdf_path}: {str(e)}", exc_info=True)
#                 continue

#         if not all_data:
#             messages.error(request, "No valid data extracted from selected PDFs.")
#             return render(request, 'merge_term_marks_pdfs.html', context)

#         subjects_db = Subject.objects.filter(user=request.user)
#         subjects_db_dict = {s.nameSubject.lower(): s for s in subjects_db}
#         logger.debug(f"Database subjects: {[s.nameSubject for s in subjects_db]}")
#         logger.debug(f"Extracted subjects from PDFs: {subjects_set}")

#         def get_grade(mark):
#             if mark is None or mark == 0:
#                 return '-'
#             for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#                 if mark >= threshold:
#                     return grade
#             return 'F'

#         def get_division(grades_for_division):
#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)
#             if grading.is_advance and num_valid_subjects < 3:
#                 return "Inc", 0
#             elif not grading.is_advance and num_valid_subjects < 7:
#                 return "Inc", 0
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:3 if grading.is_advance else 7]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break
#             return division, total_points

#         for df in all_data:
#             logger.debug(f"Processing DataFrame with {len(df)} students")
#             for _, row in df.iterrows():
#                 indexnumber = str(row['indexnumber']).strip()
#                 # Skip rows where indexnumber is 'nan' or empty
#                 if indexnumber.lower() == 'nan' or not indexnumber:
#                     logger.warning(f"Skipping row with invalid indexnumber: {row.to_dict()}")
#                     continue

#                 if indexnumber not in student_data_dict:
#                     student_data_dict[indexnumber] = {
#                         'fullname': row['fullname'],
#                         'sex': row['sex'],
#                         'indexnumber': indexnumber,
#                         'marks': {},
#                         'total_marks': 0,
#                         'subject_count': 0
#                     }

#                 student = student_data_dict[indexnumber]
                
#                 for subj_name, subject in subjects_db_dict.items():
#                     if subj_name in df.columns:
#                         mark_raw = str(row[subj_name]).strip()
#                         logger.debug(f"Student {row['indexnumber']} - Raw mark for {subj_name}: {mark_raw}")
#                         if mark_raw in ['-', ''] or pd.isna(mark_raw):
#                             mark = 0
#                             grade = '-'
#                         else:
#                             mark_match = re.match(r'(\d+\.?\d*)\s*([A-FS-])?', mark_raw)
#                             if mark_match:
#                                 mark = float(mark_match.group(1)) if mark_match.group(1) else 0
#                                 grade = mark_match.group(2) if mark_match.group(2) else get_grade(mark)
#                                 logger.debug(f"Student {row['indexnumber']} - Parsed mark for {subj_name}: {mark}, Grade: {grade}")
#                             else:
#                                 mark = 0
#                                 grade = '-'
#                                 logger.debug(f"Student {row['indexnumber']} - Failed to parse mark for {subj_name}: {mark_raw}")

#                         if subject.id not in student['marks']:
#                             student['marks'][subject.id] = {
#                                 'subject_id': subject.id,
#                                 'subject_name': subject.nameSubject,
#                                 'mark': mark,
#                                 'grade': grade,
#                                 'is_excluded': subject.id in exclude_subjects,
#                                 'count': 1
#                             }
#                         else:
#                             existing = student['marks'][subject.id]
#                             if mark > 0:
#                                 existing['mark'] = (existing['mark'] * existing['count'] + mark) / (existing['count'] + 1)
#                                 existing['grade'] = get_grade(existing['mark'])
#                                 existing['count'] += 1
#                             else:
#                                 existing['grade'] = '-' if existing['mark'] == 0 else get_grade(existing['mark'])

#         logger.debug(f"Total unique students after processing all PDFs: {len(student_data_dict)}")

#         student_data = []
#         for student in student_data_dict.values():
#             total_marks = 0
#             subject_count = 0
#             marks_list = []
            
#             for mark_info in student['marks'].values():
#                 marks_list.append(mark_info)
#                 if mark_info['mark'] > 0:
#                     total_marks += mark_info['mark']
#                     subject_count += 1

#             student['marks'] = marks_list
#             student['total_marks'] = total_marks
#             student['average_marks'] = total_marks / subject_count if subject_count > 0 else 0
#             student['grade'] = get_grade(student['average_marks'])

#             grades_for_division = [m['grade'] for m in marks_list if not m['is_excluded']]
#             division, total_points = get_division(grades_for_division)
#             student['division'] = division
#             student['total_points'] = total_points
            
#             student_data.append(student)

#         logger.debug(f"Total students in final student_data: {len(student_data)}")

#         student_data.sort(key=lambda x: x['average_marks'], reverse=True)
#         for i, student in enumerate(student_data, 1):
#             student['position'] = i

#         response = HttpResponse(content_type='application/pdf')
#         filename = f"merged_pdfs_{teacherclass.ClassName}_{datetime.now().strftime('%Y%m%d')}.pdf"
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#         elements = []
#         styles = getSampleStyleSheet()
#         header_style = styles['Heading1']
#         subheader_style = styles['Heading2']
#         body_style = styles['BodyText']
#         header_style.alignment = 1
#         subheader_style.alignment = 1
#         body_style.alignment = 1
#         body_style.fontSize = 7

#         elements.append(Paragraph(f"Merged PDFs for {teacherclass.ClassName}", header_style))
#         elements.append(Spacer(1, 8))

#         if not student_data:
#             elements.append(Paragraph("No data available to merge.", body_style))
#         else:
#             overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] + 
#                            [s.nameSubject for s in subjects_db] + 
#                            ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]
            
#             for i, student in enumerate(student_data, 1):
#                 row = [str(i), student['fullname'] or '-', student['sex'] or '-', student['indexnumber'] or '-']
#                 for subject in subjects_db:
#                     mark_info = next((m for m in student['marks'] if m['subject_id'] == subject.id), None)
#                     if mark_info:
#                         mark_display = f"{mark_info['mark']:.2f}" if mark_info['mark'] > 0 else '-'
#                         grade_display = mark_info['grade']
#                         sub_table = Table([[mark_display, grade_display]],
#                                         colWidths=[10, 12], hAlign='CENTER')
#                         sub_table.setStyle(TableStyle([
#                             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                             ('FONTSIZE', (0, 0), (-1, -1), 4),
#                             ('LEADING', (0, 0), (-1, -1), 8),
#                             ('TEXTCOLOR', (1, 0), (1, 0), colors.red if mark_info['grade'] == 'F' else colors.black),
#                         ]))
#                         row.append(sub_table)
#                     else:
#                         row.append('-')
                
#                 row.extend([
#                     f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-',
#                     f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-',
#                     student['grade'],
#                     str(student['position']),
#                     student['division'],
#                     student['total_points'] if student['total_points'] > 0 else '-'
#                 ])
#                 overall_data.append(row)

#             total_columns = len(overall_data[0])
#             base_width = (A4[0] - 30) / total_columns
#             col_widths = ([base_width * 0.5] + [base_width * 3.0] + [base_width * 0.5] + [base_width * 2.0] +
#                           [base_width * 1.0] * len(subjects_db) + [base_width * 0.8] * 6)

#             overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#             overall_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.extend([KeepTogether(overall_table), Spacer(1, 10)])

#             # Individual student reports
#             for i, student in enumerate(student_data):
#                 if i > 0:
#                     elements.append(PageBreak())
                
#                 elements.append(Paragraph(f"Student: {student['fullname'] or 'Unnamed Student'}", subheader_style))
#                 elements.append(Spacer(1, 6))

#                 student_data_table = [['Subject', 'Marks', 'Grade', 'Teacher', 'Signature', 'Status']]
#                 grades_for_division = []

#                 # Only include subjects where the student has a valid mark (mark > 0)
#                 for mark in student['marks']:
#                     if mark['mark'] > 0:  # Only include subjects with non-zero marks
#                         student_data_table.append([
#                             mark['subject_name'] or 'Unnamed',
#                             f"{mark['mark']:.2f}",
#                             mark['grade'],
#                             '',  # Placeholder for Teacher
#                             '',  # Placeholder for Signature
#                             ''   # Placeholder for Status
#                         ])
#                         if not mark['is_excluded']:
#                             grades_for_division.append(mark['grade'])

#                 if len(student_data_table) == 1:
#                     student_data_table.append(['No subjects with marks available', '-', '-', '', '', ''])

#                 student_table = Table(student_data_table, colWidths=[120, 40, 40, 60, 60, 60], splitByRow=True, repeatRows=1)
#                 student_table.setStyle(TableStyle([
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 6),
#                     ('LEADING', (0, 0), (-1, -1), 8),
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ]))
#                 elements.append(student_table)

#                 overall_grade = student['grade']
#                 division, total_points = get_division(grades_for_division)
#                 avg_display = f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-'
#                 total_display = f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-'
#                 points_display = str(total_points) if total_points > 0 else '-'
#                 summary = f"Position: {student['position']} | Avg: {avg_display} | Total: {total_display} | Division: {division} | Points: {points_display}"
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(summary, body_style))

#         elements.append(Spacer(1, 10))
#         elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", body_style))
#         doc.build(elements)
#         return response

#     if class_id:
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['uploads'] = TermMarksUpload.objects.filter(teacherclass=teacherclass, user=request.user)

#     return render(request, 'merge_term_marks_pdfs.html', context)


# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import render, get_object_or_404
# from django.contrib import messages
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet
# from datetime import datetime
# import os
# import tabula
# import pandas as pd
# import re
# from .models import TeacherClass, GradingModel, TermMarksUpload, Subject, Student, ExcludeSubject
# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet
# from datetime import datetime
# import tabula
# import pandas as pd
# import os
# import re
# from django.db.models import Prefetch
# from .models import TeacherClass, GradingModel, ExcludeSubject, TermMarksUpload, Subject, Student

# @login_required
# def ca_based_result(request, class_id=None):
#     # Prefetch related data to reduce database queries
#     classes = TeacherClass.objects.filter(user=request.user).prefetch_related('student_set')
#     grades = GradingModel.objects.filter(user=request.user)

#     context = {
#         'classes': classes,
#         'grades': grades,
#     }

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')

#         if not class_id or not grade_id or not TeacherClass.objects.filter(id=class_id, user=request.user).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}.")
#             return render(request, 'ca_based_result.html', context)

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user)
#         grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['selected_grade_id'] = grade_id

#         # Grading setup
#         if grading.is_advance:
#             exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True))
#             grade_thresholds = {
#                 grading.grade_a: 'A',
#                 grading.grade_b: 'B',
#                 grading.grade_c: 'C',
#                 grading.grade_d: 'D',
#                 grading.grade_e: 'E',
#                 grading.grade_s: 'S',
#                 grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         else:
#             exclude_subjects = set()
#             grade_thresholds = {
#                 grading.grade_a: 'A',
#                 grading.grade_b: 'B',
#                 grading.grade_c: 'C',
#                 grading.grade_d: 'D',
#                 grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#         division_thresholds = [
#             {'max': grading.division_1, 'label': 'I'},
#             {'max': grading.division_2, 'label': 'II'},
#             {'max': grading.division_3, 'label': 'III'},
#             {'max': grading.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         # Fetch term uploads
#         term_uploads = TermMarksUpload.objects.filter(
#             user=request.user,
#             teacherclass=teacherclass,
#             for_merging_pdf=False
#         ).select_related('teacherclass')
#         if not term_uploads.exists():
#             messages.error(request, "No unchecked term marks PDFs available for generating CA-based results.")
#             return render(request, 'ca_based_result.html', context)

#         # Process PDFs with optimized parsing
#         term_data = {}
#         subjects_set = set()
#         for upload in term_uploads:
#             pdf_path = upload.pdf_file.path
#             if not os.path.exists(pdf_path):
#                 messages.error(request, f"PDF file for {upload.term_name} not found at {pdf_path}.")
#                 return render(request, 'ca_based_result.html', context)

#             try:
#                 # Optimize tabula.read_pdf with stream=True for better handling of large PDFs
#                 dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True, stream=True, guess=False)
#                 if not dfs:
#                     messages.error(request, f"No tables found in {upload.term_name} PDF.")
#                     return render(request, 'ca_based_result.html', context)

#                 # Combine all tables into a single DataFrame
#                 df = pd.concat([df.dropna(how='all') for df in dfs], ignore_index=True)
#                 df.columns = df.columns.str.strip()
#                 if all(col not in df.columns for col in ['S/No', 'Student Name', 'Sex', 'Index No']):
#                     messages.error(request, f"Missing required headers in {upload.term_name} PDF.")
#                     return render(request, 'ca_based_result.html', context)

#                 df = df.rename(columns={'S/No': 'S/No', 'Student Name': 'fullName', 'Sex': 'sex', 'Index No': 'indexNumber'})
#                 term_data[upload.term_name] = df
#                 excluded_cols = ['S/No', 'fullName', 'sex', 'indexNumber', 'Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']
#                 subjects_set.update([col for col in df.columns if col not in excluded_cols])
#             except Exception as e:
#                 messages.error(request, f"Error processing PDF for {upload.term_name}: {str(e)}.")
#                 return render(request, 'ca_based_result.html', context)

#         subjects_db = Subject.objects.filter(user=request.user)
#         subjects_map = {s.nameSubject: s for s in subjects_db}  # Cache subjects for faster lookup
#         students = Student.objects.filter(teacherclass=teacherclass).select_related('teacherclass')
#         student_data = []

#         def get_grade(mark):
#             if pd.isna(mark) or mark is None or mark == 0:
#                 return '-'
#             for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#                 if mark >= threshold:
#                     return grade
#             return 'F'

#         def get_division(grades_for_division):
#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)
#             if grading.is_advance and num_valid_subjects < 3:
#                 return "Inc", 0
#             elif not grading.is_advance and num_valid_subjects < 7:
#                 return "Inc", 0
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:3 if grading.is_advance else 7]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break
#             return division, total_points

#         # Process students in batches
#         batch_size = 50
#         for i in range(0, students.count(), batch_size):
#             student_batch = students[i:i + batch_size]
#             for student in student_batch:
#                 student_dict = {'id': student.id, 'fullName': student.fullName, 'sex': student.sex, 'indexNumber': student.indexNumber}
#                 marks_list = []
#                 total_marks = 0
#                 subject_count = 0

#                 for subject_name in subjects_set:
#                     if subject_name not in subjects_map:
#                         continue
#                     subject = subjects_map[subject_name]
#                     marks = []
#                     for term_name, term_df in term_data.items():
#                         student_row = term_df[term_df['indexNumber'] == str(student.indexNumber)]
#                         if not student_row.empty and subject_name in student_row.columns:
#                             mark = student_row[subject_name].iloc[0]
#                             try:
#                                 if isinstance(mark, str):
#                                     numeric_part = re.search(r'^\d+\.?\d*', mark)
#                                     mark = float(numeric_part.group()) if numeric_part else 0
#                                 else:
#                                     mark = float(mark) if pd.notna(mark) else 0
#                                 marks.append(mark)
#                             except:
#                                 marks.append(0)
#                         else:
#                             marks.append(0)

#                     annual_mark = sum(marks)
#                     if annual_mark > 0:
#                         grade = get_grade(annual_mark)
#                         marks_list.append({
#                             'subject_id': subject.id,
#                             'subject_name': subject_name,
#                             'mark': annual_mark,
#                             'grade': grade,
#                             'is_excluded': subject.id in exclude_subjects
#                         })
#                         total_marks += annual_mark
#                         subject_count += 1

#                 student_dict['marks'] = marks_list
#                 student_dict['total_marks'] = total_marks
#                 student_dict['average_marks'] = total_marks / subject_count if subject_count > 0 else 0
#                 student_dict['grade'] = get_grade(student_dict['average_marks'])

#                 grades_for_division = [m['grade'] for m in marks_list if not m['is_excluded']]
#                 division, total_points = get_division(grades_for_division)
#                 student_dict['division'] = division
#                 student_dict['total_points'] = total_points

#                 student_data.append(student_dict)

#         # Sort students by total marks for position
#         student_data.sort(key=lambda x: x['total_marks'], reverse=True)
#         for i, student in enumerate(student_data, 1):
#             student['position'] = i

#         # Generate PDF response
#         response = HttpResponse(content_type='application/pdf')
#         filename = f"ca_based_results_{teacherclass.ClassName}_{datetime.now().strftime('%Y%m%d')}.pdf"
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#         elements = []
#         styles = getSampleStyleSheet()
#         header_style, subheader_style, body_style = styles['Heading1'], styles['Heading2'], styles['BodyText']
#         header_style.alignment = subheader_style.alignment = body_style.alignment = 1
#         body_style.fontSize = 7

#         elements.append(Paragraph(f"CA-Based Results for {teacherclass.ClassName}", header_style))
#         elements.append(Spacer(1, 8))

#         if not student_data:
#             elements.append(Paragraph("No data available for this class from unchecked PDFs.", body_style))
#         else:
#             overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] +
#                            [s.nameSubject for s in subjects_db if s.nameSubject in subjects_set] +
#                            ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]

#             for i, student in enumerate(student_data, 1):
#                 row = [str(i), student['fullName'] or '-', student['sex'] or '-', student['indexNumber'] or '-']
#                 for subject in subjects_db:
#                     if subject.nameSubject in subjects_set:
#                         mark_info = next((m for m in student['marks'] if m['subject_id'] == subject.id), None)
#                         if mark_info:
#                             sub_table = Table([[f"{mark_info['mark']:.2f}", mark_info['grade']]],
#                                             colWidths=[10, 12], hAlign='CENTER')
#                             sub_table.setStyle(TableStyle([
#                                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                                 ('FONTSIZE', (0, 0), (-1, -1), 4),
#                                 ('LEADING', (0, 0), (-1, -1), 8),
#                                 ('TEXTCOLOR', (1, 0), (1, 0), colors.red if mark_info['grade'] == 'F' else colors.black),
#                             ]))
#                             row.append(sub_table)
#                         else:
#                             row.append('-')

#                 row.extend([
#                     f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-',
#                     f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-',
#                     student['grade'],
#                     str(student['position']),
#                     student['division'],
#                     student['total_points'] if student['total_points'] > 0 else '-'
#                 ])
#                 overall_data.append(row)

#             total_columns = len(overall_data[0])
#             base_width = (A4[0] - 30) / total_columns
#             col_widths = ([base_width * 0.5] + [base_width * 3.0] + [base_width * 0.5] + [base_width * 2.0] +
#                           [base_width * 1.0] * len([s for s in subjects_db if s.nameSubject in subjects_set]) +
#                           [base_width * 0.8] * 6)

#             overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#             overall_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.extend([KeepTogether(overall_table), Spacer(1, 10)])

#         # Individual student reports in batches
#         batch_size = 20  # Smaller batch size for PDF generation
#         for i in range(0, len(student_data), batch_size):
#             student_batch = student_data[i:i + batch_size]
#             for j, student in enumerate(student_batch):
#                 if i + j > 0:
#                     elements.append(PageBreak())

#                 elements.append(Paragraph(f"Student: {student['fullName'] or 'Unnamed Student'}", subheader_style))
#                 elements.append(Spacer(1, 6))

#                 student_data_table = [['Subject', 'Marks', 'Grade', 'Teacher', 'Signature', 'Status']]
#                 grades_for_division = []

#                 for mark in student['marks']:
#                     student_data_table.append([
#                         mark['subject_name'] or 'Unnamed',
#                         f"{mark['mark']:.2f}" if mark['mark'] > 0 else '-',
#                         mark['grade'],
#                         '',  # Placeholder for Teacher
#                         '',  # Placeholder for Signature
#                         ''   # Placeholder for Status
#                     ])
#                     if not mark['is_excluded']:
#                         grades_for_division.append(mark['grade'])

#                 if len(student_data_table) == 1:
#                     student_data_table.append(['No subjects with marks available', '-', '-', '', '', ''])

#                 student_table = Table(student_data_table, colWidths=[120, 40, 40, 60, 60, 60], splitByRow=True, repeatRows=1)
#                 student_table.setStyle(TableStyle([
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 6),
#                     ('LEADING', (0, 0), (-1, -1), 8),
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ]))
#                 elements.append(student_table)

#                 overall_grade = student['grade']
#                 division, total_points = get_division(grades_for_division)
#                 avg_display = f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-'
#                 total_display = f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-'
#                 points_display = str(total_points) if total_points > 0 else '-'
#                 summary = f"Position: {student['position']} | Avg: {avg_display} | Total: {total_display} | Division: {division} | Points: {points_display}"
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(summary, body_style))

#         elements.append(Spacer(1, 10))
#         elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", body_style))

#         doc.build(elements)
#         return response

#     return render(request, 'ca_based_result.html', context)
