from django.contrib import admin

from .models import SignUp


class SignUpAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name', 'username', 'email',)
    search_fields = ('username',)


admin.site.register(SignUp, SignUpAdmin)
