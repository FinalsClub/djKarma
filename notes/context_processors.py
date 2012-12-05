""" Collection of TEMPLATE_CONTEXT_PROCESSORS
    These wrap a request object, and make variables available to render() by 
    adding variables to the response dictionary.  The result is an extra
    variable available in the template. Examples include `{{ STATIC_URL }}`
    in the `django.core.context_processors`.
"""

import datetime
def datetime_today(request):
    """ TEMPLATE_CONTEXT_PROCESSOR that makes the template variable 
        `{{ today }}` available

        :request: django httprequest object
        :returns: dictionary containing today's date
    """
    return {'today': datetime.date.today().strftime('%m/%d/%Y')}
