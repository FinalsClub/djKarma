from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Course(models.Model):
    title = models.CharField()
    #professor = models.ForeignKey()
    field = models.CharField(blank=True)
    academic_year = models.IntegerField(blank=True, null=True)

class School(models.Model):
    name = models.CharField()
    location = models.CharField(blank=True, null=True)

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
    grad_year = models.CharField(blank=True, null=True)
    fb_id = models.CharField(blank=True, null=True)
    can_upload = models.BooleanField()
    can_read = models.BooleanField()
    can_vote = models.BooleanField()
    can_comment = models.BooleanField()
    can_moderate = models.BooleanField()

def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        UserProfile.objects.create(user=kwargs.get('instance'))

post_save.connect(ensure_profile_exists, sender=User)
