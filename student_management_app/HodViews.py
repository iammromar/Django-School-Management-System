from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from .color_generator import generate_colors
from student_management_app.models import CustomUser, Staffs, Group, Subjects, Students, SessionYearModel, FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport
from .forms import AddStudentForm, EditStudentForm, AddStaffForm, EditStaffForm
from django.db.models import Q


def admin_home(request):
    all_student_count = Students.objects.all().count()
    subject_count = Subjects.objects.all().count()
    group_count = Group.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Course
    # num of groups each staff member has
    # number of students in each group

    group_all = Group.objects.all()
    group_name_list = []
    group_count_list = []
    student_count_list_in_group = []

    for group in group_all:

        students = group.students_set.all().count()
        group_name_list.append(group.group_name)
        student_count_list_in_group.append(students) # needs to be passed
    
    len_group = len(group_name_list)
    group_colors = generate_colors(len_group)

    staff_all = Staffs.objects.all()
    staff_name_group_list = []
    for staff in staff_all:

        groups = staff.group_id.all().count()
        group_count_list.append(groups) # needs to be passed
        staff_name_group_list.append(staff.admin.first_name)

    len_staff_name = len(staff_name_group_list)
    staff_name_colors = generate_colors(len_staff_name)

    
    subject_all = Subjects.objects.all()
    subject_name_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        student_count = subject.students_set.all().count()
        subject_name_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)
    
    subject_colors = generate_colors(len(subject_name_list))
    
    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        group_ids = staff.group_id.all()
        attendance = Attendance.objects.filter(group_id__in=group_ids).count() # should be fixed
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leaves = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leaves+absent)
        student_name_list.append(student.admin.first_name)


    group_ojs = Group.objects.all()

    context={
        "subject_all":subject_all,
        "student_vs_staff": [all_student_count, staff_count],
        "student_vs_staff_lables": ["Tələbələr", "Heyət"],
        "staff_name_group_list": staff_name_group_list,
        "staff_name_colors": staff_name_colors,
        "group_ojs": group_ojs,
        "subject_count": subject_count,
        "group_count": group_count,
        "group_name_list": group_name_list,
        "group_count_list": group_count_list,
        "student_count_list_in_group": student_count_list_in_group,
        "group_colors": group_colors,
        "subject_name_list": subject_name_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "subject_colors": subject_colors,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
        "all_student_count":all_student_count,
        "staff_count": staff_count,
    }

    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    if request.method == "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
        
    form = AddStaffForm()
    context = {
        "form":form
    }
    return render(request, "hod_template/add_staff_template.html", context)


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')

    form = AddStaffForm(request.POST)

    if form.is_valid():
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        address = form.cleaned_data['address']
        group_objs = form.cleaned_data['group_id']

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.save()
            for group_obj in group_objs:
                    user.staffs.group_id.add(group_obj)
            messages.success(request, "Heyət Artırıldı!")
            return redirect('add_staff')

        except:
            messages.error(request, "Heyət Artırarkən Xəta Baş Verdi!")
            return redirect('add_staff')
    messages.error(request, "Heyət Artırarkən Xəta Baş Verdi!")
    return redirect('add_staff')



def manage_staff(request):
    staffs = Staffs.objects.all().order_by('admin__first_name')
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)

def search_staff(request):
    if request.method == "GET":
        if request.GET.get('search'):
            searched = request.GET.get('search')
            search_list = request.GET.get('search').split(' ')
            for search in search_list:
                objs = Staffs.objects.filter(
                    Q(admin__first_name__icontains=search) | Q(admin__last_name__icontains=search)
                    ).distinct()

        else:
            objs = []
            searched = "Heyət Axtar"
        context = {"staffs": objs,
        "searched": searched,
        }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):

    if request.method == "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")

    request.session['staff_id'] = staff_id
    staff = Staffs.objects.get(admin=staff_id)
    form = EditStaffForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = staff.admin.email
    form.fields['username'].initial = staff.admin.username
    form.fields['first_name'].initial = staff.admin.first_name
    form.fields['last_name'].initial = staff.admin.last_name
    form.fields['address'].initial = staff.address
    form.fields['group_id'].initial = staff.group_id.all()

    context = {
        "id": staff_id,
        "username": staff.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):

    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        staff_id = request.session.get('staff_id')
        if staff_id == None:
            return redirect('/manage_staff')

        form = EditStaffForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            group_objs = form.cleaned_data['group_id']
            password = form.cleaned_data['password']

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=staff_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                if password:
                    user.set_password(password)
                user.save()

                # Then Update Staff Table
                staff_model = Staffs.objects.get(admin=staff_id)
                staff_model.address = address
                for group_obj in group_objs:
                    staff_model.group_id.add(group_obj)

                # Delete staff_id SESSION after the data is updated
                del request.session['staff_id']

                messages.success(request, "Heyət Dəyişdirildi!")
                return redirect('/edit_staff/'+staff_id)
            except:
                messages.success(request, "Heyət Dəyişdirilərkən Xəta Baş Verdi!")
                return redirect('/edit_staff/'+staff_id)
        else:
            return redirect('/edit_staff/'+staff_id)


def delete_staff(request, staff_id):
    # staff_obj = Staffs.objects.get(id=staff_id)
    # username = staff_obj.admin.username
    staff = CustomUser.objects.get(id=staff_id)
    try:
        staff.delete()
        messages.success(request, "Heyət Silindi!")
        return redirect('manage_staff')
    except:
        messages.error(request, "Heyət Silinərkən Xəta Baş Verdi!")
        return redirect('manage_staff')




def add_group(request):
    return render(request, "hod_template/add_group_template.html")


def add_group_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        group_name = request.POST.get('group')
        try:
            group_obj = Group(group_name=group_name)
            group_obj.save()
            messages.success(request, "Qrup Artırıldı!")
            return redirect('add_group')
        except:
            messages.error(request, "Qrup Artırılarkən Xəta Baş Verdi!")
            return redirect('add_group')


def manage_group(request):
    groups = Group.objects.all()
    context = {
        "groups": groups
    }
    return render(request, 'hod_template/manage_group_template.html', context)

def search_group(request):
    if request.method == "GET":
        if request.GET.get('search'):
            searched = request.GET.get('search')
            search_list = request.GET.get('search').split(' ')
            for search in search_list:
                objs = Group.objects.filter(
                    Q(group_name__icontains=search)
                    ).distinct()

        else:
            objs = []
            searched = "Qrup Axtar..."
        context = {"groups": objs,
        "searched": searched,
        }
    return render(request, "hod_template/manage_group_template.html", context)

def edit_group(request, group_id):
    group = Group.objects.get(id=group_id)
    context = {
        "group": group,
        "id": group_id
    }
    return render(request, 'hod_template/edit_group_template.html', context)


def edit_group_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        group_id = request.POST.get('group_id')
        group_name = request.POST.get('group')

        try:
            group = Group.objects.get(id=group_id)
            group.group_name = group_name
            group.save()

            messages.success(request, "Qrup Dəyişdirildi!")
            return redirect('/edit_group/'+group_id)

        except:
            messages.error(request, "Qrup Dəyişdirilərkən Xəta Baş Verdi!")
            return redirect('/edit_group/'+group_id)


def delete_group(request, group_id):
    group = Group.objects.get(id=group_id)
    try:
        group.delete()
        messages.success(request, "Qrup Silindi!")
        return redirect('manage_group')
    except:
        messages.error(request, "Qrup Silinərkən Xəta Baş Verdi!")
        return redirect('manage_group')


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)

def search_session(request):
    if request.method == "GET":
        if request.GET.get('search'):
            searched = request.GET.get('search')
            search_list = request.GET.get('search').split(' ')
            for search in search_list:
                objs = SessionYearModel.objects.filter(
                    Q(session_start_year__icontains=search) | Q(session_end_year__icontains=search)
                    ).distinct()

        else:
            objs = []
            searched = "Sessiya Axtar..."
        context = {"session_years": objs,
        "searched": searched,
        }
    return render(request, "hod_template/manage_session_template.html", context)

def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Sessiya İli Artırıldı!")
            return redirect("add_session")
        except:
            messages.error(request, "Sessiya İli Artırılarkən Xəta Baş Verdi")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.save()

            messages.success(request, "Sessiya İli Dəyişdirildi!")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Sessiya İli Dəyişdirilərkən Xəta Baş Verdi!")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Sessiya İli Silindi!")
        return redirect('manage_session')
    except:
        messages.error(request, "Sessiya İli Silinərkən Xəta Baş Verdi!")
        return redirect('manage_session')


def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)




def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            session_year_id = form.cleaned_data['session_year_id']
            group_objs = form.cleaned_data['group_id']
            subject_objs = form.cleaned_data['subject_id']
            gender = form.cleaned_data['gender']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None


            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
                user.students.address = address

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                user.students.session_year_id = session_year_obj

                user.students.gender = gender
                user.students.profile_pic = profile_pic_url
                user.save()
                for subject_obj in subject_objs:
                    user.students.subject_id.add(subject_obj)

                for group_obj in group_objs:
                    user.students.group_id.add(group_obj)

                messages.success(request, "Tələbə Artırıldı!")
                return redirect('add_student')
            except:
                messages.error(request, "Tələbə Artırılarkən Xəta Baş Verdi!")
                return redirect('add_student')
        else:
            return redirect('add_student')


def manage_student(request):
    students = Students.objects.all().order_by('admin__first_name')
    context = {
        "students": students
    }
    return render(request, 'hod_template/manage_student_template.html', context)

def search_student(request):
    if request.method == "GET":
        if request.GET.get('search'):
            searched = request.GET.get('search')
            search_list = request.GET.get('search').split(' ')
            for search in search_list:
                objs = Students.objects.filter(
                    Q(admin__first_name__icontains=search) | Q(admin__last_name__icontains=search)
                    ).distinct()

        else:
            objs = []
            searched = "Tələbə Axtar"
        context = {"students": objs,
        "searched": searched,
        }
    return render(request, "hod_template/manage_student_template.html", context)

def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id

    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = student.admin.email
    form.fields['username'].initial = student.admin.username
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['address'].initial = student.address
    form.fields['group_id'].initial = student.group_id.all()
    form.fields['subject_id'].initial = student.subject_id.all()
    form.fields['gender'].initial = student.gender
    form.fields['session_year_id'].initial = student.session_year_id.id

    context = {
        "id": student_id,
        "username": student.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            password = form.cleaned_data['password']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']
            group_objs = form.cleaned_data['group_id']
            subject_objs = form.cleaned_data['subject_id']


            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                if password:
                    user.set_password(password)
                user.save()

                # Then Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                student_model.session_year_id = session_year_obj

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()

                for subject_obj in subject_objs:
                    user.students.subject_id.add(subject_obj)

                for group_obj in group_objs:
                    user.students.group_id.add(group_obj)
                # Delete student_id SESSION after the data is updated
                del request.session['student_id']

                messages.success(request, "Tələbə Dəyişdirildi!")
                return redirect('/edit_student/'+student_id)
            except:
                messages.success(request, "Tələbə Dəyişdirilərkən Xəta Baş Verdi!")
                return redirect('/edit_student/'+student_id)
        else:
            return redirect('/edit_student/'+student_id)


def delete_student(request, student_id):
    student = CustomUser.objects.get(id=student_id)
    try:
        student.delete()
        messages.success(request, "Tələbə Silindi!")
        return redirect('manage_student')
    except:
        messages.error(request, "Tələbə Sİlinərkən Xəta Baş Verdi!")
        return redirect('manage_student')


def add_subject(request):
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "staffs": staffs
    }
    return render(request, 'hod_template/add_subject_template.html', context)



def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')
        price = request.POST.get('price')
        
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(subject_name=subject_name, price=price, staff_id=staff)
            subject.save()
            messages.success(request, "Fənn Artırıdı!")
            return redirect('add_subject')
        except:
            messages.error(request, "Fənn Artırılarkən Xəta Baş Verdi!")
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)

def search_subject(request):
    if request.method == "GET":
        if request.GET.get('search'):
            searched = request.GET.get('search')
            search_list = request.GET.get('search').split(' ')
            for search in search_list:
                objs = Subjects.objects.filter(
                    Q(subject_name__icontains=search)
                    ).distinct()

        else:
            objs = []
            searched = "F'nn Axtar..."
        context = {"subjects": objs,
        "searched": searched,
        }
    return render(request, "hod_template/manage_subject_template.html", context)

def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        price = request.POST.get('price')
        staff_id = request.POST.get('staff')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name
            subject.price = price

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff

            
            subject.save()

            messages.success(request, "Fənn Dəyişdirildi!")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Fənn Dəyişdirilərkən Xəta Baş Verdi!")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Fənn Silindi!")
        return redirect('manage_subject')
    except:
        messages.error(request, "Fənn Silinərkən Xəta Baş Verdi!")
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.order_by('-created_at').all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    if feedback_reply:
        try:
            feedback = FeedBackStudent.objects.get(id=feedback_id)
            feedback.feedback_reply = feedback_reply
            feedback.save()
            return HttpResponse("True")

        except:
            return HttpResponse("False")
    return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.order_by('-created_at').all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')
    if feedback_reply:
        try:
            feedback = FeedBackStaffs.objects.get(id=feedback_id)
            feedback.feedback_reply = feedback_reply
            feedback.save()
            return HttpResponse("True")

        except:
            return HttpResponse("False")
    return HttpResponse("False")    


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.order_by('-created_at').all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)

def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.order_by('-created_at').all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    groups = Group.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "groups": groups,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    group_id = request.POST.get("group")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    group_model = Group.objects.get(id=group_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(group_id=group_model, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id, "name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profil Dəyişdirildi!")
            return redirect('admin_profile')
        except:
            messages.error(request, "Profil Dəyişdirilərkən Xəta Baş Verdi!")
            return redirect('admin_profile')


