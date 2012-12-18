#!/usr/bin/python
# -*- coding:utf8 -*-
"""
Administration configuration.
    This enables us to specify and customize
    the interface of the django admin panel.
"""
# Copyright (C) 2012  FinalsClub Foundation

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from models import UserProfile
import models

# Register the database models described in model
# present them to show up in admin interface
admin.site.register(models.School)
admin.site.register(models.DriveAuth)
admin.site.register(models.Course)
admin.site.register(models.Instructor)
admin.site.register(models.Note)
admin.site.register(models.Tag)
admin.site.register(models.ReputationEvent)
admin.site.register(models.ReputationEventType)
admin.site.register(models.SiteStats)
admin.site.register(models.Level)
admin.site.register(models.Vote)
admin.site.register(models.UsdeSchool)
admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, ]


admin.site.register(User, UserProfileAdmin)
