from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from models import UserProfile
import models

admin.site.register(models.School)
admin.site.register(models.Course)
admin.site.register(models.Note)
admin.site.register(models.Tag)
admin.site.register(models.ReputationEventType)
admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, ]

admin.site.register(User, UserProfileAdmin)
