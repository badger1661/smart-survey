from django.contrib import admin
from .models import Form, Question, AdditionalComment, Answer

# Register your models here.

class FormAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'date_created', 'id']
    search_fields = ['title', 'teacher', 'date_created', 'id']

    class Meta:
        model = Form
admin.site.register(Form, FormAdmin)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'id']
    search_fields = ['question_text', 'id']

    class Meta:
        model = Question
admin.site.register(Question, QuestionAdmin)

admin.site.register(AdditionalComment)
admin.site.register(Answer)

