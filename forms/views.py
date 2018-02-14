from django.shortcuts import render
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from .models import Form, Question, AdditionalComment, Answer
from users.models import Set
import logging
logger = logging.getLogger(__name__)


from django.http import JsonResponse, HttpResponse
import json
# Create your views here.

class create_form(LoginRequiredMixin, View):
    login_url = '/login/'

    template_name = 'form/create_form.html'

    #RETURN HTML PAGE
    def get(self, request):
        sets = Set.objects.filter(teacher = request.user)
        args = {'sets': sets}
        return render(request, self.template_name, args)
    
    def post(self, request):
        #GET REQUIRED ATTRIBUTES
        title = request.POST.get('title', None)
        description = request.POST.get('description', None)
        questions = request.POST.get('questions', None)
        comments = request.POST.get('comments', None)
        setid = request.POST.get('setid', None)
        set_ = Set.objects.get(pk = setid)
        if comments == 'true':
            comments = True
        else:
            comments = False

        #GET QUESTION TEXT INTO PYTHON LIST
        questions = json.loads(questions)
        question_ids = []

        for question in questions:
            #CHECK IF QUESTION EXISTS IN DATABASE, IF NOT MAKE A NEW ONE AND PUT ID IN QUESTIONS_IDS
            try:
                questionid = Question.objects.get(question_text = question).id
                question_ids.append(questionid)
            except ObjectDoesNotExist:
                question = Question(question_text = question)
                question.save()
                question_ids.append(question.id)

        #TURN QUESTION_IDS INTO JSON STRING FOR STORAGE IN TEXTFIELD
        json_string = json.dumps(question_ids)
        
        #CREATE FORM OBJECT
        form = Form(title=title,
                    description = description,
                    teacher = request.user,
                    questions = json_string,
                    additionalcomment = comments,
                    setID = set_,
                    )
        form.save()

        url = '/form/{}/'.format(int(form.id))
        args = {'url': url}
        
        return JsonResponse(args)


@login_required
def view_form(request, form_id=None):

    #CHECK VALID URL
    if form_id == None:
        return HttpResponse("<html><body>no id passed</body></html>")
    else:
        #CHECK IF THE FORM EXISTS
        try:
            form_ = Form.objects.get(id = form_id)
            if request.user != form_.teacher:
                return HttpResponse("<html><body>Not permitted to view this page</body></html>")
                
        except ObjectDoesNotExist:
            return HttpResponse("<html><body>form does not exist</body></html>")
        
        #IF FORM IS A DUPLICATE, GET PARENT'S ID AND CALL SAME VIEW WITH PARENTS ID INSTEAD
        if form_.duplicate == True:
            form_id = form_.parent.id
            return redirect('view_form', form_id=form_id)

        #GET ALL CHILDREN FORMS
        forms = Form.objects.filter(parent = form_)
        forms = forms.order_by("date_created")
        
        #Put the parent and children into one list
        p_and_c_forms = [form_]
        for form in forms:
            p_and_c_forms.append(form)

        #FIND OUT HOW MANY RESPONSES
        new_forms = []
        

        #LOAD QUESTIONS INTO A PYTHON LIST FROM JSON DICTIONARY
        question = json.loads(form_.questions)

        for form in p_and_c_forms:
            answers = len(Answer.objects.filter(form = form))

            #GET AMOUNT OF RESPONSES BY DIVIDING AMOUNT OF ANSWER OBJECTS FOR EACH
            #FORM BY THE AMOUNT OF QUESTIONS THE FORM HAS
            responses = answers//len(question)
            form.responses = responses
            new_forms.append(form)

        #LIST OF QUESTIONS FOR DEMO FORM
        questions = []
        for question_id in range(len(question)):
            q = Question.objects.get(pk = question[question_id])
            q.position = question_id + 1
            questions.append(q)

        args = {'form': form_,
                'forms': new_forms,
                'questions': questions}

        return render(request, 'form/view_form.html', args)

@login_required
def view_replies(request, form_id = None):
    if form_id == None:
        return HttpResponse("<html><body>No id passed.</body></html>")
    else:
        try:
            form = Form.objects.get(pk = form_id)
            if form.teacher != request.user:
                return HttpResponse("<html><body>not allowed to view this form.</body></html>")
        except ObjectDoesNotExist:
                return HttpResponse("<html><body>This form doesn't exist.</body></html>")
    
    questions = []
    question_ids =  json.loads(form.questions)
    
    #GET QUESTIONS FROM A LIST OF IDS
    for id_ in question_ids:
        question = Question.objects.get(pk = id_)
        questions.append(question)

    set_sent_to = form.setID
    students = set_sent_to.students.all()
    #GET INDUVIDUAL RESPONSES
    induvidual_answers = []
    replied = []

    #GET STUDENTS ANSWERS AND ADDITIONALCOMMENT IF IT EXISTS AND PUT IT INTO A LIST
    for student in range(len(students)):
        answers_ = Answer.objects.filter(form = form, student = students[student]).order_by("position")
        answers_with_question = []

        if len(answers_) > 0:
            replied.append(students[student])
            
            for ans_ in range(len(answers_)):
                a = answers_[ans_]
                a.question = questions[ans_]
                answers_with_question.append(a)

            ans = ['temp', answers_with_question]

            if form.additionalcomment:
                try:
                    comment = AdditionalComment.objects.get(form = form, student = students[student])
                    ans.append(comment)
                except ObjectDoesNotExist:
                    pass
            induvidual_answers.append(ans)

    not_replied = []
    for student in students:
        if student not in replied:
            not_replied.append(student)

    ##ASIGN APPROPRIATE ID FOR TEMPLATE RENDERING
    for a in range(len(induvidual_answers)):
        induvidual_answers[a][0] = a + 1

    #GET COLLECTIVE RESPONSES
    collective_responses = []

    #GET QUESTIONS
    for question in range(len(questions)):
        questions[question].position = question
        #USED FOR CHAT IDS
        questions[question].name = chr(question + 65)

    #TOTAL UP AMOUNT OF RATING OCCURANCES
    for question in questions:
        to_append = [question]
        answers = Answer.objects.filter(form=form, position = question.position)
        scores = {1: 0,
                  2: 0,
                  3: 0,
                  4: 0,
                  5: 0}
        for answer in answers:    
            if answer.score in scores:
                scores[answer.score] += 1
            else:
                scores[answer.score] = 1
        
        scores = [scores[1], scores[2], scores[3], scores[4], scores[5]]
        to_append.append(scores)
        collective_responses.append(to_append)
    
    #print(collective_responses)

    args = {'form': form,
            'induvidual_answers': induvidual_answers,
            'collective_responses': collective_responses,
            'amount_of_responses': len(induvidual_answers),
            'replied': replied,
            'not_replied': not_replied,
    }

    return render(request, 'form/view_replies.html', args)
     
class reply(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'form/reply.html'
    
    #Checks if the user has already responded to the form or if user is a teacher
    def check(self, form_id, user):
        if user.is_student():
            form = Form.objects.get(pk = form_id)
            try:
                answers = Answer.objects.filter(form = form, student = user)
            except ObjectDoesNotExist:
                pass
            if answers:
                return True
        else:
            return True
            

    def get(self, request, form_id=None):
        #VARIOUS CHECKS TO SEE IF USURE CAN REPLY
        if form_id == None:
            return HttpResponse("<html><body>no id passed</body></html>")
        else:
            try:
                form = Form.objects.get(pk = form_id)
                if self.check(form_id, request.user):
                    return HttpResponse("<html><body>You have already replied to this form</body></html>")
                #GET QUESTIONS INTO PYTHON LIST
                questions = []
                question_ids =  json.loads(form.questions)

                #GET QUESTION OBJECTS
                for id_ in question_ids:
                    question = Question.objects.get(pk = id_)
                    questions.append(question)  

                #ADD QUESTION NUMBERS FOR RENDERING
                for question in range(len(questions)):
                    q = questions[question]
                    q.position = question + 1

                args = {'form': form,
                        'questions': questions}
                return render(request, self.template_name, args)

            except ObjectDoesNotExist:
                return HttpResponse("<html><body>form does not exist</body></html>")       
                


    
    def post(self, request, form_id=None):
        if self.check(form_id, request.user):
            return HttpResponse("<html><body>You have already replied to this form</body></html>")
        form = Form.objects.get(pk = form_id)

        answers = request.POST.get('results', None)
        answers = json.loads(answers)
        if form.additionalcomment == True:
            comment = request.POST.get('comment')

        answers = [int(answer) for answer in answers]
        for i in range(0, len(answers)):
            answer = Answer(form = form,
                            student = request.user,
                            position = i,
                            score = answers[i],
                            )
            answer.save()
       # SORT OUT ADDING THE COMMENTS
        if form.additionalcomment == True:
            additionalcomment = AdditionalComment(text = comment,
                                                  form = form,
                                                  student = request.user)
            additionalcomment.save()
        
        return JsonResponse({})

def compare_form(request, form_one = None, form_two = None):
    user = request.user
    try:
        form_one = Form.objects.get(pk = form_one)
        form_two = Form.objects.get(pk = form_two)
    except ObjectDoesNotExist:
        return HttpResponse("<html><body>One or both of those surveys don't exit!</body></html>")

    if (form_one.teacher or form_two.each) != user:
        return HttpResponse("<html><body>One or both of those surveys weren't created by you!</body></html>")

    if form_one.duplicate == True and form_two.duplicate == True:
        if form_one.parent != form_two.parent:
            return HttpResponse("<html><body>These surveys aren't identical!</body></html>")
    elif form_one.duplicate == False:
        if form_two.parent != form_one:
            return HttpResponse("<html><body>These surveys aren't identical!</body></html>")
    elif form_two.duplicate == False:
        if form_one.parent != form_one:
            return HttpResponse("<html><body>These surveys aren't identical!</body></html>")
    else:
        return HttpResponse("<html><body>These surveys aren't identical!</body></html>")

    forms = [form_one, form_two]
    questions = []
    question_ids =  json.loads(form_one.questions)
    
    #GET QUESTIONS FROM A LIST OF IDS
    for id_ in question_ids:
        question = Question.objects.get(pk = id_)
        questions.append(question)

    #
    for question in range(len(questions)):
        questions[question].position = question
        #USED FOR CHAT IDS
        questions[question].name = chr(question + 65)

    responses = []

    for question in questions:
        to_append = [question]
        ratings = []
        for form in forms:
            
            answers = Answer.objects.filter(form=form, position = question.position)
            scores = {1: 0,
                      2: 0,
                      3: 0,
                      4: 0,
                      5: 0}
            for answer in answers:    
                if answer.score in scores:
                    scores[answer.score] += 1
                else:
                    scores[answer.score] = 1
            
            scores = [scores[1], scores[2], scores[3], scores[4], scores[5]]

            ratings.append(scores)
            
        to_append.append(ratings)
    
        responses.append(to_append)
    print(responses)
    args = {
            'form_one': form_one,
            'form_two': form_two,
            'responses': responses,
    }

    return render(request, 'form/compare_form.html', args)

def resend_form(request):
    form_id = request.POST.get('id', None)
    form = Form.objects.get(pk = form_id)
    
    #DUPLICATE FORM
    new_form = Form(
                    teacher = form.teacher,
                    title = form.title,
                    description = form.description,
                    questions = form.questions,
                    additionalcomment = form.additionalcomment,
                    setID = form.setID,
                    duplicate = True,
                    parent = form,
                    )
    new_form.save()
    
    return JsonResponse({})

def remind(request):
    ids = request.POST.get('ids', None)
    ids = json.loads(ids)
    ids = [int(id_) for id_ in ids]
    form_id = request.POST.get('form_id', None)

    try:
        form = Form.objects.get(pk = form_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': True,})

    emails = []
    for id_ in ids:
        try:
            student = get_user_model().objects.get(pk = id_).email
            emails.append(student)
        except ObjectDoesNotExist:
            pass
    
    current_site = get_current_site(request)
    subject = 'Activate your SmartSurvey account'
    message = render_to_string('email/surveys_pending.html', {
        'domain': current_site.domain,
        },
        emails
        )
    send_mass_mail(message)

    return JsonResponse({})
    