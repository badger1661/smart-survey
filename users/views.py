from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.utils import six
from django.contrib.auth import login
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required

import logging
logger = logging.getLogger(__name__)

import json

from .models import Student, Teacher, School, Subject, SchoolAdmin, Set
#from reviews.models import Form
from .forms import StudentRegister, TeacherRegister, SetCreate

from forms.models import Form, Answer
# Create your views here.

def activate(request, uidb64, token):
    #Try get user based on token
    try:
        id_ = force_text(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=id_)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    #If user exists change confirmed and is_active attribute to True
    if user is not None and account_activation_token.check_token(user, token):

        groups = user.groups.all()
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('profile')
    else:
        return render(request, 'email/invalid_token.html')

def send_confirmation_email(request, user):
    #gets all the info for verification email
    current_site = get_current_site(request)
    subject = 'Activate your SmartSurvey account'
    message = render_to_string('email/email_activation.html', {
        'name': user.get_full_name(),
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        })
    user.email_user(subject, message)

def student_registration(request):
    #Student Registration

    if request.method == 'POST':
        form = StudentRegister(request.POST)
        #Gets school object from email domain.        
        school_domain = form['email'].value().split('@')[1]
        try:
            school = School.objects.get(email_domain = school_domain)
        except ObjectDoesNotExist:
            pass
            
        if form.is_valid() and school:
            user, Student = form.save()
            Student.school = school
            Student.save()
            user.groups.add(Group.objects.get(name='Student'))
            #user.is_active to stop users logging in without confirming their emails
            user.is_active = False
            user.save()

            #Sends confirmation link.
            send_confirmation_email(request, user)

            args = {'email': user.email,
                    'link': user.Student.school.email_website,}
            return render(request, 'email/token_sent.html', args)

        else:
            args = {'form': form,}
            return render(request, 'users/students.html', args)
            
    else:
        form = StudentRegister()
        args = {'form': form,}
        return render(request, 'users/students.html', args)

def teacher_registration(request):
    #Teacher Registration
    
    if request.method == 'POST':
        form = TeacherRegister(request.POST)
        #Gets school object from email domain.
        email = form['email'].value().split('@')[1]
        try:
            school = School.objects.get(email_domain = email)
        except ObjectDoesNotExist:
            #add custom error message here
            pass
        if form.is_valid():
            user, Teacher = form.save()
            Teacher.school = school
            Teacher.save()
            user.groups.add(Group.objects.get(name='Teacher'))
            #user.is_active to stop users logging in without confirming their emails
                      
            user.is_active = False
            user.save()
            #Sends confirmation link.
            send_confirmation_email(request, user)
            
            args = {'email': user.email,
                    'link': user.Teacher.school.email_website}
            
            return render(request, 'email/token_sent.html', args)
        
        else:
            args = {'form': form,}
            return render(request, 'users/teachers.html', args)

    else:
        form = TeacherRegister
        args = {'form':form,}
        return render(request, 'users/teachers.html', args)

@login_required(login_url='/login/')
def confirm_teacher(request):
    id_ = request.POST.get('teacherID', None)
    delete = request.POST.get('delete', False)
    user = get_user_model().objects.get(pk = id_)
    teacher = Teacher.objects.get(user = user)

    if delete == 'True':
        user.delete()
    else:
        teacher.verified = True
        teacher.save()
    args = {}
    return JsonResponse(args)

class create_set(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'users/create_set.html'

    #If get request
    def get(self, request):
        if request.is_ajax():
            #Gets all students that are part of the teachers school
            keyword = request.GET.get('keyword', None).lower()
            teacher_school = Teacher.objects.get(user = request.user).school
            students = Student.objects.filter(school = teacher_school)
            student_list = []
            #Filters students against the keyword
            for student in students:
                if keyword in student.user.get_full_name().lower() or keyword in student.user.email.lower():
                    to_add = [student.user.get_full_name(), student.user.email, student.user.id]
                    student_list.append(to_add)
            args = {'students': student_list}

            return JsonResponse(args)
        else:
            return render(request, self.template_name)

    #If post request
    def post(self, request):
        #Gets the student IDs and turns it into a list
        student_ids = request.POST.get('student_ids', None)
        student_ids = json.loads(student_ids)

        name = request.POST.get('name', None)

        form = SetCreate(request.POST)
        #Creates the Set Object
        if form.is_valid():
            instance = form.save(commit = False)
            instance.name = name
            teacher = request.user
            instance.teacher = teacher
            instance.save()
            #Adds all the students by getting their user object by id.
            for id_ in student_ids:
                user = get_user_model().objects.get(pk = id_)
                instance.students.add(user)
                instance.save()
        else:
            print('heyos') 
        
        url = '/class/{}/'.format(instance.id)
        args = {'url': url}

        return JsonResponse(args)

@login_required(login_url='/login/')
def view_set(request, set_id):
    #Gets the set object
    try:
        set_ = Set.objects.get(id = set_id)
    except ObjectDoesNotExist:
        return HttpResponse("<html><body>That Class doesnt exist</body></html>")
        
    #teacher = set_.teacher
    user = request.user
    #Checks if the client is the Sets teacher
    if user != set_.teacher:
        return HttpResponse("<html><body>Not permitted to view that set</body></html>")

    students = set_.students.all()
    print(students)
    forms = Form.objects.filter(teacher = user, setID = set_, duplicate = False)
    for form in forms:
        resends = Form.objects.filter(parent = form)
        form.times_sent = len(resends) + 1

    args = {'set': set_,
            'forms': forms,
            'teachers_name': user.get_full_name(),
            'students': students}

    return render(request, 'users/view_set.html', args)

def add_students(request):
    student_ids = request.POST.get('student_ids', None)
    student_ids = json.loads(student_ids)
    set_id = request.POST.get('set_id', None)

    try:
        set_ = Set.objects.get(pk = set_id)
    except ObjectDoesNotExist:
        return JsonResponse({})

    for id_ in student_ids:
        try:
            user = get_user_model().objects.get(pk = id_)
            set_.students.add(user)
            set_.save()
        except ObjectDoesNotExist:
            pass

    return JsonResponse({})


@login_required(login_url='/login/')
def delete_from_class(request):
    student_id = request.POST.get('id', None)
    set_id = request.POST.get('set_id')

    try:
        student = get_user_model().objects.get(pk = student_id)
        set_ = Set.objects.get(pk = set_id)
    except ObjectDoesNotExist:
        return JsonResponse({'success': 'invalid id'})
    args = {}
    if request.user == set_.teacher:
        set_.students.remove(student)
        args["success"] = True
    else:
        args["success"] = False
    return JsonResponse(args)


@login_required(login_url='/login/')
def profile(request):
    #Gets the user
    user = request.user
    
    args = {'user': user}
    print(user.is_teacher())

    logger.debug(user.is_teacher())

    if user.is_teacher():
        #Gets the teachers Forms and their Sets and checks if they're verified
        teacher = Teacher.objects.get(user = user)
        forms = Form.objects.filter(teacher = user, duplicate = False)
        sets = Set.objects.filter(teacher = user)
        new_form_list = []
        for form in forms:
            resends = Form.objects.filter(parent = form)
            form.times_sent = len(resends) + 1
            new_form_list.append(form)

        args['teacher'] = Teacher.objects.get(user = user)
        args['verified'] = teacher.verified
        args['forms'] = new_form_list
        args['sets'] = sets
        return render(request, 'users/teacher_profile.html', args)
    
    elif user.is_student():
        student = Student.objects.get(user = user)
        sets = Set.objects.filter(students__id=user.id)
        forms = []
        for set_ in sets:
            forms_ = Form.objects.filter(setID = set_)
            for form in forms_:
                answers = Answer.objects.filter(form = form, student = user)
                if len(answers) == 0:
                    forms.append(form)

        args = {'forms': forms,
        }
        return render(request, 'users/student_profile.html', args)

    elif user.is_admin():
        admin_object = SchoolAdmin.objects.get(user = user)
        school = School.objects.get(school_name = admin_object.school.school_name)
        school_teachers = Teacher.objects.filter(school = school, verified = False)

        for teacher in school_teachers:
            if teacher.user.email_confirmed == False:
                user = teacher.user
                school_teachers = school_teachers.exclude(user = user)

        #print(school_teachers)
        args = {'teachers': school_teachers,
                'admin': admin_object}
        return render(request, 'users/admin_profile.html', args)

    else:
        return HttpResponse("<html><body>No profile for you</body></html>")
