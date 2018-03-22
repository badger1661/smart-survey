from django.db import models
from django.db.models import OneToOneField, ForeignKey, BooleanField, CharField, URLField, EmailField, IntegerField, ManyToManyField
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
#FOR CUSTOM USER
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class UserManager(UserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    
    abstract = True
    username = None
    email = EmailField(_('email address'), unique=True)
    email_confirmed = BooleanField(default = False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def get_full_name(self):
        fname = self.first_name
        lname = self.last_name
        return '{} {}'.format(fname, lname)

    def is_teacher(self):
        return self.groups.filter(name='Teacher').exists()
    
    def is_student(self):
        return self.groups.filter(name='Student').exists()
    
    def is_admin(self):
        return self.groups.filter(name='Admin').exists()

class Student(models.Model):
    user = OneToOneField(get_user_model(), null = False, related_name = 'Student', on_delete = models.CASCADE)
    school = ForeignKey('School', on_delete = models.CASCADE, null = True)
    
    def __str__(self):
        first_name = self.user.first_name
        school = self.school
        return '{} | {}'.format(school, first_name)

class Teacher(models.Model):
    user = OneToOneField(get_user_model(), null = False, related_name = 'Teacher', on_delete = models.CASCADE)
    prefix = ForeignKey('Prefix', on_delete = models.SET_NULL, null = True)
    school = ForeignKey('School', on_delete = models.CASCADE, null = True)
    subject = ForeignKey('Subject', null = False, on_delete = models.CASCADE)
    verified = BooleanField(default = False)

    def __str__(self):
        first_name = self.user.first_name        
        school = self.school
        return '{} | {}'.format(school, first_name)

class SchoolAdmin(models.Model):
    user = OneToOneField(get_user_model(), null = False, related_name = 'Admin', on_delete = models.CASCADE)
    school = ForeignKey('School', on_delete = models.CASCADE, null = True)

    def __str__(self):
        school_name = self.school.school_name
        return '{} {}'.format(school_name, 'Admin')

class School(models.Model):
    school_name = CharField(max_length = 200)
    email_domain = CharField(max_length = 250)
    website = URLField()
    email_website = URLField()

    def __str__(self):
        return self.school_name

class Subject(models.Model):
    subject_name = CharField(max_length = 200, unique = True)

    def __str__(self):
        return self.subject_name

class Prefix(models.Model):
    prefix = CharField(max_length = 10)

    def __str__(self):
        return self.prefix

class Set(models.Model):
    name = CharField(max_length = 25)
    teacher = ForeignKey(get_user_model(), null = False, on_delete = models.CASCADE)
    students = ManyToManyField(get_user_model(), related_name= 'set_students')

    def __str__(self):
        name = self.name
        teacher = self.teacher.get_full_name()
        return '{} | {}'.format(name, teacher)

    def amount_of_students(self):
        students = self.students
        return students.count()

    def view_set(self):
        return reverse("view_set", kwargs = {'set_id': self.id})
