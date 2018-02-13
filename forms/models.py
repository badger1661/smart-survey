from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Model, TextField, CharField, \
                            ForeignKey, DateField, \
                            BooleanField, IntegerField,\
                            OneToOneField, ManyToManyField
from users.models import Set
from django.contrib.auth import get_user_model
from django.conf import settings
import logging
logger = logging.getLogger(__name__) 
# Create your models here

class Form(models.Model):
    teacher = ForeignKey(get_user_model(), on_delete = models.CASCADE)
    title = CharField(max_length = 50)
    description = TextField()
    date_created = DateField(auto_now = False, auto_now_add = True)
    questions = TextField()
    additionalcomment = BooleanField(default = True)
    setID = ForeignKey(Set, on_delete = models.CASCADE)
    duplicate = BooleanField(default = False)
    parent = ForeignKey('Form', null = True, blank = True, on_delete = models.CASCADE)
    #iteration = IntegerField(default = 0, null = False)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("view_form", kwargs = {'form_id': self.id})

    def view_replies(self):
        return reverse("view_replies", kwargs = {'form_id': self.id})

    def answer_form(self):
        return(reverse("reply", kwargs ={'form_id': self.id}))

class Question(models.Model):
    question_text = CharField(max_length = 240)
    
    def __str__(self):
        return self.question_text

class AdditionalComment(models.Model):
    form = ForeignKey('Form', related_name = 'form_comment', on_delete = models.CASCADE)
    student = ForeignKey(get_user_model(), on_delete = models.CASCADE)
    text = CharField(max_length = 300)
    
    def __str__(self):
        student = self.student.get_full_name()
        form = self.form.title
        return '{} | {}'.format(student, form)

class Answer(models.Model):
    form = ForeignKey('Form', on_delete = models.CASCADE)
    student = ForeignKey(get_user_model(), on_delete = models.CASCADE)
    position = IntegerField()
    score = IntegerField()

    def __str__(self):
        form = self.form.title
        student = self.student.get_full_name()
        position = self.position
        return "{} | {} | {}".format(form, student, position)
# class Answer(models.Model):
#     student = ForeignKey(get_user_model(), on_delete = models.CASCADE)
#     form = ForeignKey('Form', on_delete = models.CASCADE)
#     date_created = DateTimeField(auto_now = False, auto_now_add = True)

# class Score(models.model):
#     position = IntegerField()
#     score = IntegerField()
#     Answer = ForeignKey('')s