from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Student, Teacher, School, Subject, Prefix, SchoolAdmin, Set
# Register your models here.
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(School)
admin.site.register(Subject)
admin.site.register(Prefix)
admin.site.register(SchoolAdmin)
admin.site.register(Set)

@admin.register(get_user_model())
class UserAdmin(UserAdmin):
    class Meta:

        model = get_user_model()

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email_confirmed')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff','email_confirmed')
    search_fields = ('email', 'first_name', 'last_name', 'email_confirmed')
    ordering = ('email',)