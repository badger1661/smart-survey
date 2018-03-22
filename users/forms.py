from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Student, Teacher, Subject, Prefix, Set, School
from django.core.exceptions import ObjectDoesNotExist

class StudentRegister(UserCreationForm):
    email = forms.EmailField(required = True)

    def __init__(self, *args, **kwargs):
        super(StudentRegister, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'example@example.com'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Password'

    class Meta:
        model = get_user_model()

        fields = (
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2'            
        )    
    
    def clean_email(self):
        original_email = self.cleaned_data.get('email')
        domain = original_email.split('@')[1] 
        try:
            school = School.objects.get(email_domain = domain)
        except ObjectDoesNotExist:
            raise forms.ValidationError('School not found, check your email') 

        return original_email

    def save(self):
        user = super(StudentRegister, self).save()

        student = Student(user = user)
                          

        student.save()

        return user, student

class TeacherRegister(UserCreationForm):
    email = forms.EmailField(required = True)
    prefix = forms.ModelChoiceField(queryset= Prefix.objects.all().order_by('prefix'), required = True)
    subject = forms.ModelChoiceField(queryset= Subject.objects.all().order_by('subject_name'), required = True)

    def __init__(self, *args, **kwargs):
        super(TeacherRegister, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'example@example.com'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Password'

    class Meta:
        model = get_user_model()

        fields = (
            'email',
            'prefix',
            'first_name',
            'last_name',
            'subject',
            'password1',
            'password2'  
        )

    def clean_email(self):
        original_email = self.cleaned_data.get('email')
        domain = original_email.split('@')[1] 
        try:
            school = School.objects.get(email_domain = domain)
        except ObjectDoesNotExist:
            raise forms.ValidationError('School not found, check your email') 

        return original_email

    def save(self):
        user = super(TeacherRegister, self).save()

        teacher = Teacher(user = user,
                          prefix=self.cleaned_data['prefix'],        
                          subject=self.cleaned_data['subject'])
        teacher.save()

        return user, teacher

class SetCreate(forms.ModelForm):
    class Meta:
        model = Set
        fields = ()