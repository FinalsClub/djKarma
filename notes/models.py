# Copyright (C) 2012  FinalsClub Foundation

import datetime
import hashlib
import re

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.template.defaultfilters import slugify

from social_auth.backends.facebook import FacebookBackend
from social_auth.signals import socialauth_registered


class Level(models.Model):
    """ Define User Levels
        Each slug title is related to a minimum karma level
    """
    title = models.SlugField(max_length=255)
    karma = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%s %d" % (self.title, self.karma)


class SiteStats(models.Model):
    """ Used to incrementally tally site statistics
        For display on landing page, etc.
        This is more efficient then calculating totals on every request
        Upon installing the app we should initialize ONE instance of SiteStats
        The increment/decrement methods will act only on the first instance (pk=1)
    """
    # TODO: make this class name singular
    numNotes = models.IntegerField(default=0)
    numStudyGuides = models.IntegerField(default=0)
    numSyllabi = models.IntegerField(default=0)
    numAssignments = models.IntegerField(default=0)
    numExams = models.IntegerField(default=0)

    numCourses = models.IntegerField(default=0)
    numSchools = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%d Notes, %d Guides, %d Syllabi, %d Assignments, %d Exams for %d total Courses at %d Schools" % (self.numNotes, self.numStudyGuides, self.numSyllabi, self.numAssignments, self.numExams, self.numCourses, self.numSchools)


def decrement(sender, **kwargs):
    """ Decrease the appropriate stat given a Model
        Called in Model save() and post_delete() (not delete() due to queryset behavior)
    """
    # TODO, impement this as a method on the SiteStat object, rather than in the global scope of models
    stats = SiteStats.objects.get(pk=1)
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


def increment(sender, **kwargs):
    """ Increment the appropriate stat given a Model
        Called in Model save() and post_delete() (not delete() due to queryset behavior)
    """
    # TODO, modify decrement to increment or decrement based on a passed flag, rather than duplicating this if else logic
    stats = SiteStats.objects.get(pk=1)
    #print stats.numNotes
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


class Tag(models.Model):
    """ This class represents a meta-tag of a note
        Used for searching
    """
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


class Vote(models.Model):
    """ Represents a vote cast on a Note
        if up is true, it is an upvote
        else, a downvote
    """
    user = models.ForeignKey(User)
    up = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s voted %s" % (self.user, str(self.up))


class School(models.Model):
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(null=True)
    location    = models.CharField(max_length=255, blank=True, null=True)

    # Facebook keeps a unique identifier for all schools
    facebook_id = models.BigIntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('browse-courses', [str(self.slug)])

    def save(self, *args, **kwargs):
        # If a new School is being saved, increment SiteStat School count
        if not self.pk:
            increment(self)
        if not self.slug:
            # FIXME: make this unique
            # TODO: add a legacy slugs table that provide redirects to new slug pages
            self.slug = slugify(self.name)
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
    school          = models.ForeignKey(School, blank=True, null=True)
    title           = models.CharField(max_length=255)
    slug            = models.SlugField(max_length=100, null=True)
    url             = models.URLField(max_length=511, blank=True)
    field           = models.CharField(max_length=255, blank=True, null=True)
    semester        = models.IntegerField(choices=SEMESTERS, blank=True, null=True)
    academic_year   = models.IntegerField(blank=True, null=True, default=datetime.datetime.now().year)
    instructor      = models.ForeignKey(Instructor, blank=True, null=True)

    def __unicode__(self):
        # Note: these must be unicode objects
        return u"%s" % (self.title)

    @models.permalink
    def get_absolute_url(self):
        return ('browse-course', [str(self.school.slug), str(self.slug)])

    def save(self, *args, **kwargs):
        # If a new Course is being saved, increment SiteStat Course count
        if not self.pk:
            increment(self)
        if not self.slug:
            # FIXME: make this unique
            # TODO: add a legacy slugs table that provide redirects to new slug pages
            self.slug = slugify(self.title)
        super(Course, self).save(*args, **kwargs)

    class Meta:
        # sort by "the date" in descending order unless
        # overridden in the query with order_by()
        ordering = ['title']

# On Course delete, decrement numCourses
post_delete.connect(decrement, sender=Course)


class File(models.Model):

    # FIXME: list of tuples can't be addressed, dicts can
    # FILE_TYPES['N']
    FILE_TYPES = (
        ('N', 'Note'),
        ('S', 'Syllabus'),
        ('E', 'Exam'),
        ('G', 'Study Guide'),
        ('A', 'Assignment'),
    )

    # Relate self.type to reputationEventType
    # FIXME: only karma for one variation of essay and study-guide
    KARMA_TYPES = {
        'N': 'lecture-note',
        'S': 'syllabus',
        'E': 'exam-or-quiz',
        'G': 'mid-term-study-guide',
        'A': 'essay-medium'
    }

    # Display point values in upload form
    # TODO: Tie this to ReputationEventType
    FILE_PTS = (
        ('N', 'Note (+5 pts)'),
        ('S', 'Syllabus (+10 pts)'),
        ('E', 'Exam (+10 pts)'),
        ('G', 'Study Guide (+25 pts)'),
        ('A', 'Assignment (+5 pts)'),
    )

    title       = models.CharField(max_length=255)
    description = models.TextField(max_length=511)
    course      = models.ForeignKey(Course, blank=True, null=True, related_name="files")
    school      = models.ForeignKey(School, blank=True, null=True)
    file        = models.FileField(upload_to="uploads/notes")
    html        = models.TextField(blank=True, null=True)
    tags        = models.ManyToManyField(Tag, blank=True, null=True)
    timestamp   = models.DateTimeField(default=datetime.datetime.now())
    viewCount   = models.IntegerField(default=0)
    votes       = models.ManyToManyField(Vote, blank=True, null=True)
    numUpVotes  = models.IntegerField(default=0)
    numDownVotes = models.IntegerField(default=0)
    type        = models.CharField(blank=True, null=True, max_length=1, choices=FILE_PTS, default='N')
    # User who uploaded the document
    owner       = models.ForeignKey(User, blank=True, null=True, related_name='notes')
    # has the html content been escaped?
    # This is to assure we don't double escape characters
    cleaned     = models.BooleanField(default=False)
    # on metadata save, award karma and set this flag
    awarded_karma = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s at %s" % (self.title, self.course)

    @models.permalink
    def get_absolute_url(self):
        return ('nurl_file', [str(self.school.slug), str(self.course.slug), str(self.pk)])

    def save(self, *args, **kwargs):

        # If this is a new file, increment SiteStat
        if not self.pk:
            increment(self)

        print "awarded_karma: %s, self.owner: %s" % (self.awarded_karma, self.owner)
        if not self.awarded_karma and self.owner is not None:
            # FIXME: award karma based on submission type
            if self.type in self.KARMA_TYPES:
                karma_event = self.KARMA_TYPES[self.type]
            else:
                #Default note type
                karma_event = 'lecture-note'
            user_profile = self.owner.get_profile()
            user_profile.awardKarma(karma_event, school=self.school, course=self.course, user=self.owner)
            self.awarded_karma = True

        # Escape html field only once
        if(self.html is not None and not self.cleaned):
            # TODO: Check this security
            self.html = re.escape(self.html)
            self.cleaned = True

        if self.course and self.owner:
            # if course and owner, add course to owner's courses
            user_profile = self.owner.get_profile()
            user_profile.courses.add(self.course)
            user_profile.save()

        super(File, self).save(*args, **kwargs)

    def ownedBy(self, user_pk):
        """ Returns true if the user owns or has "paid" for this file
        """
        # If the file is in the user's collection, or the user owns the file
        if self.owner == User.objects.get(pk=user_pk) or User.objects.get(pk=user_pk).get_profile().files.filter(pk=self.pk).exists():
            return True
        return False

    def Vote(self, voter, vote_value=0):
        """ Calls UserProfile.awardKarma
            with the appropriate ReputationEventType slug title("upvote", "downvote")
            and target user (if downvote)
            upvote - vote_value=1 , downvote - vote_value=-1
        """
        print "Creating Vote object. voter: " + str(voter) + " value: " + str(vote_value)
        # Abort of note vote_value provided, or voter is not a User object
        if int(vote_value) == 0 or not isinstance(voter, User):
            print "invalid vote value or voter"
            return
        if int(vote_value) == 1:
            this_vote = Vote.objects.create(user=voter, up=True)
            print "upvote created: " + str(this_vote)
            # Increment the file's upvote counter
            self.numUpVotes += 1
            # Award karma corresponding to "upvote" ReputationEventType to file owner
            if self.owner is not None:
                self.owner.get_profile().awardKarma(event="upvote")
            # Add this vote to the file's collection
            self.votes.add(this_vote)
        elif int(vote_value) == -1:
            this_vote = Vote.objects.create(user=voter, up=False)
            print "downvote created: " + str(this_vote)
            # Increment the file's downvote counter
            self.numDownVotes += 1
            # "Award" negative karma coresponding to "downvote" ReputationEventType to file owner
            # and negative karma corresponding to "downvote" target user to downvoter
            if self.owner is not None:
                self.owner.get_profile().awardKarma(event="downvote", target_user=voter)
            # Add this vote to the file's collection
            self.votes.add(this_vote)
        self.save()


# On File delete, decrement appropriate stat
post_delete.connect(decrement, sender=File)


class ReputationEventType(models.Model):
    """ This class will allow us to model different user actions and the
        karma they should receive. This model will only be altered from the
        admin interface. Every User will have a collection of Reputation Events
        that can be used to re-calculate reputation as our metric changes
    """
    title = models.SlugField(max_length=160, unique=True)
    # Karma on person committing action. i.e: User who casts downvote
    actor_karma = models.IntegerField(default=0)
    # Karma on person targeted by action. i.e: User who receives downvote
    target_karma = models.IntegerField(default=0)

    def __unicode__(self):
        #Note these must be unicode objects
        return u"%s Actor: %spts Target: %spts" % (self.title, self.actor_karma, self.target_karma)


class ReputationEvent(models.Model):
    """ User objects will have a collection of these events
        Used to calculate reputation
    """
    # TODO: add a fkey to UserProfile and other logic
    type    = models.ForeignKey(ReputationEventType)
    timestamp = models.DateTimeField(auto_now_add=True)

    # optional fkeys to related models. used for displaying activity for user/school/course
    user        = models.ForeignKey(User, blank=True, null=True, related_name='actor') # FIXME: rename actor_user
    target      = models.ForeignKey(User, blank=True, null=True, related_name='target')
    file        = models.ForeignKey(File, blank=True, null=True)
    course      = models.ForeignKey(Course, blank=True, null=True)
    school      = models.ForeignKey(School, blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.type.title)


class UserProfile(models.Model):
    """ User objects have the following fields:

        username, first_name last_name email password
        is_staff is_active is_superuser last_login date_joined

        user_profile extends the user to add our extra fields
    """
    # TODO: At some point, split our our UserProfile into a separate app, \
    #       so it may be shared between projects and to limit the size of this file
    user = models.ForeignKey(User, unique=True)
    school = models.ForeignKey(School, blank=True, null=True)

    alias = models.CharField(max_length=16, blank=True, null=True)

    # Has a user finished setting up their profile?
    complete_profile    = models.BooleanField(default=False)
    invited_friend      = models.BooleanField(default=False)

    # karma will be calculated based on ReputationEvents
    # it is more efficient to incrementally tally the total value
    # vs summing all ReputationEvents every time karma is needed
    karma = models.IntegerField(default=0)
    reputationEvents = models.ManyToManyField(ReputationEvent, blank=True, null=True)

    # Optional fields:
    # TODO: update this when User.save() is run, check if gravatar has an image for their email
    gravatar = models.CharField(max_length=100, blank=True)  # gravatar hash make urls in function
    # the cached versions of self.get_picture
    picture_url_large = models.CharField(max_length=255, default='/static/img/avatar_large.png')
    picture_url_small = models.CharField(max_length=255, default='/static/img/avatar_small.png')

    grad_year = models.CharField(max_length=255, blank=True, null=True)
    fb_id = models.CharField(max_length=255, blank=True, null=True)
    can_upload = models.BooleanField(default=True)
    can_read = models.BooleanField(default=False)
    can_vote = models.BooleanField(default=False)
    can_comment = models.BooleanField(default=False)
    can_moderate = models.BooleanField(default=False)

    # user-submitted files and those the user has "paid for"
    files = models.ManyToManyField(File, blank=True, null=True)

    # courses a user is currently, or has been enrolled
    courses = models.ManyToManyField(Course, null=True, blank=True)

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

    def __unicode__(self):
        #Note these must be unicode objects
        return u"%s at %s" % (self.user.username, self.school)

    def getLevel(self):
        """ Determine the current level of the user
            based on their karma and the Levels.
            Returns a dictionary of
            [current_level] -> Level
            [next_level] -> Next Level

        """
        response = {}
        levels = Level.objects.all().order_by('karma')
        for (counter, level) in enumerate(levels):
            if self.karma < level.karma:
                if counter > 0:
                    response['next_level'] = level
                    response['current_level'] = levels[counter - 1]
                else:
                    # If the user has not surpassed the first level
                    response['current_level'] = level
                    response['next_level'] = levels[counter + 1]
                break
        if not 'next_level' in response:
            response['current_level'] = levels[len(levels) - 1]
        return response

    def get_picture(self, size='small'):
        """ get the url of an appropriately size image for a user
            :size:  if size is set to anything but small, it will return a 180px image
                    if size = default of 'small' then it will return a 50px image
            returns a facebook url if the user has a fb_id
            returns a gravatar url if the user has an image there
            returns a placeholder url if the user has neither
        """
        # TODO: get and use default user icon if none, use gravatar's 404 function
        #
        small_default = u'/static/img/avatar-180.png'
        large_default = u'/static/img/avatar-50.png'
        if self.fb_id:
            url = u"https://graph.facebook.com/{0}/picture".format(self.user.username)
            if size == 'small':
                return url
            else:
                return url + u'?type=large'
        else:
            if not self.gravatar:
                gravatar_hash = update_gravatar(self)  # FIXME
            else:
                gravatar_hash = self.gravatar
            url = u"https://secure.gravatar.com/avatar/{0}".format(gravatar_hash)
            if size == 'small':
                return u'{0}?s=50&d={1}'.format(url, small_default)
            else:
                return u'{0}?s=180d={1}'.format(url, large_default)

    # Get the "name" of this user for display
    # If no first_name, user username
    def getName(self):
        """ Generate the front-facing username for this user.
            Prefer user-supplied alias first,
            Second, username given on standard account signup
            Lastly, first name last initial (from social login)
        """
        # TODO make a template tag of this
        if self.alias and self.alias != "":
            return self.alias
        if self.user.first_name:
            if self.user.last_name:
                # First name + Last name initial
                return self.user.first_name + self.user.last_name[0].upper()
            else:
                # First name
                return self.user.first_name
        else:
            # As last resort, use username
            # Could be user entered username, fb username, or a
            # gibberish name if fb acct used w/out username (rare, bc fb gives first,last name)
            return self.user.username

    def awardKarma(self, event, target_user=None, school=None, course=None, user=None):
        """ Award user karma given a ReputationEventType slug title
            and add a new ReputationEvent to UserProfile.reputationEvents
            Does not call UserProfile.save() because it is used in
            The UserProfile save() method

            :event: is the slug title corresponding to a ReputationEventType
            :target_user: is a User object corresponding to the target (if applicable)
            :school: is a School object (optional)
            :course: a Course object (optional)
            :user: a User object (optional), for recalling username when showing other's karmaevents
            returns True or False

        """
        try:
            ret = ReputationEventType.objects.get(title=event)
            self.karma += ret.actor_karma
            if target_user:
                target_profile = target_user.get_profile()
                target_profile.karma += ret.target_karma
                target_profile.save()
            # Generate new ReputationEvent, add to UserProfile
            event = ReputationEvent.objects.create(type=ret)
            # if school or course are passed, save fkeys on the event
            if school:
                event.school = school
            if course:
                event.course = course
            if user:
                event.user = user
            event.save()  # FIXME: might be called on UserProfile.save()
            print "event.id: %s" % event.id

            self.reputationEvents.add(event)
            # Don't self.save(), because this method is called
            # from UserProfile.save()
            return True
        except:
            return False

    def addFile(self, File):
        """ Called by notes.views.upload after saving File
            Generates the appropriate ReputationEvent, and modifies
            the user's karma
        """
        # Set File.owner to the user
        File.owner = self.user
        File.save()
        # Add this file to the user's collection
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

    def save(self, *args, **kwargs):
        """ Check if school, grad_year fields have been set
            Automatically called on UserProfile post_save
        """
        # If there is not a gravatar hash, and the user registered by email
        # make a gravatar hash
        if not self.gravatar and not self.fb_id:
            self.gravatar = hashlib.md5(self.user.email.lower()).hexdigest()

        # Regenerate the picture_urls for easy access
        self.picture_url_large = self.get_picture('large')
        self.picture_url_small = self.get_picture('small')

        # Grad year was set for the first time, award karma
        #print (self.grad_year == "")
        if self.grad_year != "" and not self.submitted_grad_year:
            print "grad year submitted"
            self.submitted_grad_year = True
            self.awardKarma('profile-grad-year')

        # School set for first time, award karma
        if self.school is not None and not self.submitted_school:
            print "submitted school!"
            self.submitted_school = True
            self.awardKarma('profile-school')

        # Add read permissions if Prospect karma level is reached
        if not self.can_read and self.karma >= Level.objects.get(title='Prospect').karma:
            self.can_read = True

        # Add vote permissions if Prospect karma level is reached
        #if self.can_vote == False and self.karma >= Level.objects.get(title='Prospect').karma:
        #    self.can_vote = True

        # TODO: Add other permissions...

        super(UserProfile, self).save(*args, **kwargs)


############################## ##############################
#
# Model extra utilities
#
############################## ##############################

def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        UserProfile.objects.create(user=kwargs.get('instance'))

post_save.connect(ensure_profile_exists, sender=User)


def facebook_extra_data(sender, user, response, details, **kwargs):
    """
    This is triggered after a django_social_auth returns a user's data.
    This should save data to the UserProfile object, including username and school
    TODO: we may need to create schools based on what facebook returns

    see: http://django-social-auth.readthedocs.org/en/latest/signals.html
    """
    # TODO: This should live in util, on the UserProfile object or in a generic app
    user_profile = user.get_profile()
    user.email = response.get('email')
    user.save()

    user_profile.fb_id = response.get('id')
    #user_profile.gravatar = hashlib.md5(user.email.lower()).hashdigest()

    # take the user's school, save it to the UserProfile if found
    # create a new School if not
    # note this only takes the most recent school from a user's education history
    # FIXME: add a selector for which ofschool from their education history to use
    user_school = response.get('education')[-1]
    fb_school_name = user_school['school']['name']
    fb_school_id = user_school['school']['id']
    user_profile.school, created = School.objects.get_or_create(
            name=fb_school_name,
            facebook_id=fb_school_id)
    user_profile.save()

socialauth_registered.connect(facebook_extra_data, sender=FacebookBackend)
