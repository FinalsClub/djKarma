# urls.py is part of Karma Notes
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

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from haystack.views import SearchView, search_view_factory
from haystack.forms import ModelSearchForm
from haystack.query import SearchQuerySet

from notes.models import School

# Example SearchQuerySet fed to Haystack's SearchView
sqs = SearchQuerySet().highlight()

# Be mindful of overly broad url patterns
# Remember the trailing $ to avoid partial match

urlpatterns = patterns('',
    # captcha test
    url(r'^captcha$', 'notes.views.captcha', name='captcha'),
    # Landing page.
    url(r'^$', 'notes.views.home', name='home'),
    url(r'^about$', 'notes.views.about', name='about'),
    url(r'^terms$', 'notes.views.terms', name='terms'),

    # Ajax File Upload
    url(r'^ajax-upload$', 'notes.views.import_uploader', name="ajax_upload"),

    # File meta data submission
    url(r'^filemeta$', 'notes.views.fileMeta', name='fileMeta'),

    # Karma events 
    url(r'^karma-events$', 'notes.views.karma_events', name='karma-events'),

    url(r'^getting-started$', 'notes.views.getting_started', name='getting-started'),

    # User Profile
    url(r'^profile$', 'notes.views.profile', name='profile'),
    # User Profile Ajax submit
    url(r'^editProfile$', 'notes.views.editProfile', name='editProfile'),

    # Note View
    url(r'^file/(\d{1,99})$', 'notes.views.file', name='file'),
    # Browse

    # Custom Haystack Search Test
    url(r'^search/', 'notes.views.search'),

    # Ajax requests from search page to populate 'Browse by School and Course' accordion
    url(r'^browseBySchool/$', 'notes.views.searchBySchool', name='browse'),
    url(r'^browseByCourse/(\d{1,99})$', 'notes.views.notesOfCourse'),

    # Ajax Voting
    url(r'^vote/(\d{1,99})$', 'notes.views.vote'),

    # Ajax requets from upload usher. Text input to model get / create
    url(r'^smartModelQuery$', 'notes.views.smartModelQuery'),

    # Ajax requests from note upload form for autocomplete fields
    url(r'^courses$', 'notes.views.courses'),
    url(r'^schools$', 'notes.views.schools'),
    url(r'^instructors$', 'notes.views.instructors'),
    url(r'^simple-autocomplete/', include('simple_autocomplete.urls')),

    # Add Course, School forms
    url(r'^add', 'notes.views.addModel', name='add'),

    # Auth
    # This logout allows us to pass a redirect:
    # <a href="{% url auth_logout_next /some/location %}">Logout</a>
    #url(r'^logout/(?P<next_page>.*)/$', 'django.contrib.auth.views.logout', name='auth_logout_next'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    # accepts the username that invited
    url(r'^accounts/register/(?P<invite_user>[0-9A-Fa-f]*)$', 'notes.views.register', name='register_account'),
    url(r'', include('social_auth.urls')),

    # admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # admin:
    url(r'^admin/', include(admin.site.urls)),
)
