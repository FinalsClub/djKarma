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

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
import re

# Used to incrementally tally site statistics
# For display on landing page, etc.
# This is more efficient then calculating totals on every request
class SiteStats(models.Model):
    numNotes = models.IntegerField(default=0)
    numStudyGuides = models.IntegerField(default=0)
    numSyllabi = models.IntegerField(default=0)
    numAssignments = models.IntegerField(default=0)
    numExams = models.IntegerField(default=0)

    numCourses = models.IntegerField(default=0)
    numSchools = models.IntegerField(default=0)

    def decrement(self, sender):
        if isinstance(sender, Note):
            self.numNotes -= 1
        elif isinstance(sender, School):
            self.numSchools -= 1



# This class represents a meta-tag of a note
# Used for searching
class Tag(models.Model):
    name = models.CharField(max_length=160)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

# This class will allow us to model different user actions and the 
# karma they should receive. This model will only be altered from the
# admin interface. Every User will have a collection of Reputation Events
# that can be used to re-calculate reputation as our metric changes
class ReputationEventType(models.Model):
    title = models.SlugField(max_length=160, unique=True)
    karma = models.IntegerField(default=0)

# User objects will have a collection of these events
# Used to calculate reputation
class ReputationEvent(models.Model):
    #type is a reserved keyword in python :(
    event = models.ForeignKey(ReputationEventType)
    timestamp = models.DateTimeField(auto_now_add=True)

# Represents a vote cast on a Note
# if up is true, it is an upvote
# else, a downvote
class Vote(models.Model):
    user = models.ForeignKey(User)
    up = models.BooleanField(default=True)

class School(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            # If a new School is being saved, increment SiteStat School count
            SiteStats.numSchools += 1
        super(School, self).save(*args, **kwargs)

post_delete.connect(SiteStats.decrement(sender), sender=School)



class Course(models.Model):
    school = models.ForeignKey(School, blank=True, null=True)
    title = models.CharField(max_length=255)
    field = models.CharField(max_length=255, blank=True)
    academic_year = models.IntegerField(blank=True, null=True)
    #professor = models.ForeignKey()
    def __unicode__(self):
        #Note these must be unicode objects
        return u"%s at %s" % (self.title, self.school)

class Note(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, blank=True, null=True)
    school = models.ForeignKey(School, blank=True, null=True)
    file = models.FileField(upload_to="uploads/notes")
    html = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.datetime.now())
    viewCount = models.IntegerField(default=0)
    votes = models.ManyToManyField(Vote, blank=True, null=True)

    def __unicode__(self):
        #Note these must be unicode objects
        return u"%s at %s" % (self.title, self.course)

    def save(self, *args, **kwargs):
        if(self.html != None):
            self.html = re.escape(self.html)

        super(Note, self).save(*args, **kwargs)

class UserProfile(models.Model):
    """ User objects have the following fields:

        username
        first_name
        last_name
        email
        password
        is_staff
        is_active
        is_superuser
        last_login
        date_joined

        user_profile extends the user to add our extra fields
    """
    ## 1-to-1 relation to user model
    # This field is required
    user = models.ForeignKey(User, unique=True)
    school = models.ForeignKey(School, blank=True, null=True)

    # karma will be calculated based on ReputationEvents
    # it is more efficient to incrementally tally the total value
    # vs summing all ReputationEvents every time karma is needed
    karma = models.IntegerField(default=0)
    reputationEvennts = models.ManyToManyField(ReputationEvent, blank=True, null=True)

    # Optional fields:
    gravatar = models.URLField(blank=True) # Profile glitter
    grad_year = models.CharField(max_length=255, blank=True, null=True)
    fb_id = models.CharField(max_length=255, blank=True, null=True)
    can_upload = models.BooleanField(default=True)
    can_read = models.BooleanField(default=False)
    can_vote = models.BooleanField(default=False)
    can_comment = models.BooleanField(default=False)
    can_moderate = models.BooleanField(default=False)

    #user-submitted notes
    notes = models.ManyToManyField(Note, blank=True, null=True)

def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        UserProfile.objects.create(user=kwargs.get('instance'))

post_save.connect(ensure_profile_exists, sender=User)
