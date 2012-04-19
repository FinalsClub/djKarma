# Copyright (C) 2012  FinalsClub Foundation
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from models import UserProfile
import models

admin.site.register(models.School)
admin.site.register(models.Course)
admin.site.register(models.Instructor)
admin.site.register(models.File)
admin.site.register(models.Tag)
admin.site.register(models.ReputationEventType)
admin.site.register(models.SiteStats)
admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, ]

admin.site.register(User, UserProfileAdmin)
