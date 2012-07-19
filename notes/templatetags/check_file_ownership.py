from django.contrib.auth.models import User
from django import template

register = template.Library()


@register.filter(name='ownedBy')
def ownedBy(file, user_pk):
    """ Returns True if the given file is owned by the user
        with pk=user_pk. False otherwise
    """
    if file.owner == User.objects.get(pk=user_pk) or User.objects.get(pk=user_pk).get_profile().files.filter(pk=file.pk).exists():
        return True
    return False
