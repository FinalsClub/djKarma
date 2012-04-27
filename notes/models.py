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
from django.db.models.signals import post_save, post_delete
import datetime
import re
from django.template.defaultfilters import slugify


# Define User Levels
# Each slug title is related to a minimum karma level
class Level(models.Model):
    title = models.SlugField(max_length=255)
    karma = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%s %d" % (self.title, self.karma)


# Used to incrementally tally site statistics
# For display on landing page, etc.
# This is more efficient then calculating totals on every request
# Upon installing the app we should initialize ONE instance of SiteStats
# The increment/decrement methods will act only on the first instance (pk=1)
class SiteStats(models.Model):
    numNotes = models.IntegerField(default=0)
    numStudyGuides = models.IntegerField(default=0)
    numSyllabi = models.IntegerField(default=0)
    numAssignments = models.IntegerField(default=0)
    numExams = models.IntegerField(default=0)

    numCourses = models.IntegerField(default=0)
    numSchools = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%d Notes, %d Guides, %d Syllabi, %d Assignments, %d Exams for %d total Courses at %d Schools" % (self.numNotes, self.numStudyGuides, self.numSyllabi, self.numAssignments, self.numExams, self.numCourses, self.numSchools)


# Decrease the appropriate stat given a Model
# Called in Model save() and post_delete() (not delete() due to queryset behavior)
def decrement(sender, **kwargs):
    stats = SiteStats.objects.get(pk=1)
    print stats.numNotes
    if isinstance(sender, File):
        if sender.type == 'N':
            stats.numNotes -= 1
        elif sender.type == 'G':
            stats.numStudyGuides -= 1
        elif sender.type == 'S':
            stats.numSyllabi -= 1
        elif sender.type == 'A':
            stats.numAssignments -= 1
        elif sender.type == 'E':
            stats.numExams -= 1
    elif isinstance(sender, School):
        stats.numSchools -= 1
    elif isinstance(sender, Course):
        stats.numCourses -= 1
    stats.save()


# Increment the appropriate stat given a Model
# Called in Model save() and post_delete() (not delete() due to queryset behavior)
def increment(sender, **kwargs):
    stats = SiteStats.objects.get(pk=1)
    print stats.numNotes
    if isinstance(sender, File):
        print sender.type
        if sender.type == 'N':
            stats.numNotes += 1
        elif sender.type == 'G':
            stats.numStudyGuides += 1
        elif sender.type == 'S':
            stats.numSyllabi += 1
        elif sender.type == 'A':
            stats.numAssignments += 1
        elif sender.type == 'E':
            stats.numExams += 1
    elif isinstance(sender, School):
        stats.numSchools += 1
    elif isinstance(sender, Course):
        stats.numCourses += 1
    stats.save()


# This class represents a meta-tag of a note
# Used for searching
class Tag(models.Model):
    #Ensure no tag by same name exist
    name = models.SlugField(max_length=160)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        #Ensure slugs are properly formatted
        # "This Equals" -> "this-equals"
        self.name = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)


# This class will allow us to model different user actions and the
# karma they should receive. This model will only be altered from the
# admin interface. Every User will have a collection of Reputation Events
# that can be used to re-calculate reputation as our metric changes
class ReputationEventType(models.Model):
    title = models.SlugField(max_length=160, unique=True)
    # Karma on person committing action. i.e: User who casts downvote
    actor_karma = models.IntegerField(default=0)
    # Karma on person targeted by action. i.e: User who receives downvote
    target_karma = models.IntegerField(default=0)

    def __unicode__(self):
        #Note these must be unicode objects
        return u"%s Actor: %spts Target: %spts" % (self.title, self.actor_karma, self.target_karma)


# User objects will have a collection of these events
# Used to calculate reputation
class ReputationEvent(models.Model):
    type = models.ForeignKey(ReputationEventType)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s" % (self.type.title)


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
        # If a new School is being saved, increment SiteStat School count
        if not self.pk:
            increment(self)
        super(School, self).save(*args, **kwargs)

# On School delete, decrement numSchools
post_delete.connect(decrement, sender=School)


class Instructor(models.Model):
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School, blank=True, null=True)

    def __unicode__(self):
        #Note these must be unicode objects
        return u"%s" % (self.name)


class Course(models.Model):
    SEMESTERS = (
    (1, 'Fall'),
    (2, 'Winter'),
    (3, 'Spring'),
    (4, 'Summer'),
    )
    school = models.ForeignKey(School, blank=True, null=True)
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=511)
    field = models.CharField(max_length=255, blank=True, null=True)
    semester = models.IntegerField(choices=SEMESTERS, blank=True, null=True)
    academic_year = models.IntegerField(blank=True, null=True)
    instructor = models.ForeignKey(Instructor, blank=True, null=True)

    def __unicode__(self):
        #Note these must be unicode objects
        return u"%s at %s" % (self.title, self.school)

    def save(self, *args, **kwargs):
        # If a new Course is being saved, increment SiteStat Course count
        if not self.pk:
            increment(self)
        super(Course, self).save(*args, **kwargs)

# On Course delete, decrement numCourses
post_delete.connect(decrement, sender=Course)


class File(models.Model):

    FILE_TYPES = (
    ('N', 'Note'),
    ('S', 'Syllabus'),
    ('E', 'Exam'),
    ('G', 'Study Guide'),
    ('A', 'Assignment'),
    )

    # Display point values in upload form
    # TODO: Tie this to ReputationEventType
    FILE_PTS = (
    ('N', 'Note (+5 pts)'),
    ('S', 'Syllabus (+10 pts)'),
    ('E', 'Exam (+10 pts)'),
    ('G', 'Study Guide (+25 pts)'),
    ('A', 'Assignment (+5 pts)'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(max_length=511)
    course = models.ForeignKey(Course, blank=True, null=True)
    school = models.ForeignKey(School, blank=True, null=True)
    file = models.FileField(upload_to="uploads/notes")
    html = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.datetime.now())
    viewCount = models.IntegerField(default=0)
    votes = models.ManyToManyField(Vote, blank=True, null=True)
    numUpVotes = models.IntegerField(default=0)
    numDownVotes = models.IntegerField(default=0)
    type = models.CharField(max_length=1, choices=FILE_PTS)

    # has the html content been escaped?
    # This is to assure we don't double escape characters
    cleaned = models.BooleanField(default=False)

    def __unicode__(self):
        #Note these must be unicode objects
        return u"%s at %s" % (self.title, self.course)

    def save(self, *args, **kwargs):

        # If this is a new file, increment SiteStat
        if not self.pk:
            increment(self)

        # Escape html field only once
        if(self.html != None and not self.cleaned):
            # TODO: Check this security
            self.html = re.escape(self.html)
            self.cleaned = True

        super(File, self).save(*args, **kwargs)

# On File delete, decrement appropriate stat
post_delete.connect(decrement, sender=File)


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
    reputationEvents = models.ManyToManyField(ReputationEvent, blank=True, null=True)

    # Optional fields:
    gravatar = models.URLField(blank=True)  # Profile glitter
    grad_year = models.CharField(max_length=255, blank=True, null=True)
    fb_id = models.CharField(max_length=255, blank=True, null=True)
    can_upload = models.BooleanField(default=True)
    can_read = models.BooleanField(default=False)
    can_vote = models.BooleanField(default=False)
    can_comment = models.BooleanField(default=False)
    can_moderate = models.BooleanField(default=False)

    #user-submitted files and those the user has "paid for"
    files = models.ManyToManyField(File, blank=True, null=True)

    # Keep record of if user has added school / grad_year
    # Filling out these fields awards karma
    # Disallow rewarding karma for re-entering these fields
    # While stil allowing user to switch school /year
    submitted_school = models.BooleanField(default=False)
    submitted_grad_year = models.BooleanField(default=False)
    # TODO: On post_save, check to see if school, grad year not NOne
    # set appropriate Bool True and award karma points

    # TODO: store all reputation-related activity
    # To a separate file

    # Award user karma given a ReputationEventType slug title
    # and add a new ReputationEvent to UserProfile.reputationEvents
    # event is the slug title corresponding to a ReputationEventType
    # target_user is a User object corresponding to the target (if applicable)
    # Does not call UserProfile.save() because it is used in 
    # The UserProfile save() method
    def awardKarma(self, event, target_user=None):
        try:
            ret = ReputationEventType.objects.get(title=event)
            self.karma += ret.actor_karma
            if target_user:
                target_profile = target_user.get_profile()
                target_profile.karma += ret.target_karma
                target_profile.save()
            # Generate new ReputationEvent, add to UserProfile
            event = ReputationEvent.objects.create(type=ret)
            self.reputationEvents.add(event)
            # Don't self.save(), because this method is called
            # from UserProfile.save()
            return True
        except:
            return False

    # Called by notes.views.upload after saving File
    # Generates the appropriate ReputationEvent, and modifies
    # the user's karma
    def addFile(self, File):
        # Associate this file with the user
        self.files.add(File)
        # Generate a reputation event
        title = ""
        if File.type == 'N':
            title = 'lecture-note'
        elif File.type == 'G':
            title = 'mid-term-study-guide'
        elif File.type == 'S':
            title = 'syllabus'
        elif File.type == 'A':
            title = 'assignment'
        elif File.type == 'E':
            title = 'exam-or-quiz'

        # Remember to load all ReputationEventTypes with
        # python manage.py loaddata ./fixtures/data.json
        repType = ReputationEventType.objects.get(title=title)
        repEvent = ReputationEvent.objects.create(type=repType)
        self.reputationEvents.add(repEvent)

        # Assign user points as prescribed by ReputationEventType
        self.karma += repType.actor_karma
        self.save()


    # Check if school, grad_year fields have been set
    # Automatically called on UserProfile post_save
    def save(self, *args, **kwargs):
        # Grad year was set for the first time, award karma
        if self.grad_year != None and not self.submitted_grad_year:
            self.submitted_grad_year = True
            self.awardKarma('profile-grad-year')

        # School set for first time, award karma
        if self.school != None and not self.submitted_school:
            print "submitted school!"
            self.submitted_school = True
            self.awardKarma('profile-school')

        # Add read permissions if Prospect karma level is reached
        if self.can_read == False and self.karma >= Level.objects.get(title='Prospect').karma:
            self.can_read = True

        # Add vote permissions if Prospect karma level is reached
        #if self.can_vote == False and self.karma >= Level.objects.get(title='Prospect').karma:
        #    self.can_vote = True

        # TODO: Add other permissions...

        super(UserProfile, self).save(*args, **kwargs)


def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        UserProfile.objects.create(user=kwargs.get('instance'))

post_save.connect(ensure_profile_exists, sender=User)
