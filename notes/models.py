from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
import re

class School(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=160)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

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
    karma = models.IntegerField(default=0)

    # Optional fields:
    gravatar = models.URLField(blank=True) # Profile glitter
    grad_year = models.CharField(max_length=255, blank=True, null=True)
    fb_id = models.CharField(max_length=255, blank=True, null=True)
    can_upload = models.BooleanField()
    can_read = models.BooleanField()
    can_vote = models.BooleanField()
    can_comment = models.BooleanField()
    can_moderate = models.BooleanField()

    #user-submitted notes
    #notes = models.ManyToManyField(Note, blank=True, null=True)

def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        UserProfile.objects.create(user=kwargs.get('instance'))

post_save.connect(ensure_profile_exists, sender=User)
