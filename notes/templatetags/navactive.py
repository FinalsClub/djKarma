from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def navactive(request, urls):
    """ Template tag for highlighting active navbar links
        `class="{{ navactive request URL.name }}"`
        :request: a django request object, required for looking up current url
        :urls:  the list of url names that should highlight this URL
    """
    if request.path in ( reverse(url) for url in urls.split() ):
        return "active" # class name for currently active link
    else:
        return ""
