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

from haystack.query import SearchQuerySet

admin.autodiscover()
# Example SearchQuerySet fed to Haystack's SearchView
sqs = SearchQuerySet().highlight()

# Be mindful of overly broad url patterns
# Remember the trailing $ to avoid partial match

urlpatterns = patterns('',

    url(r'^404$', 'notes.views.e404', name='404'),
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
    url(r'^your-courses$', 'notes.views.your_courses', name='your-courses'),

    url(r'^browse/schools$', 'notes.views.browse_schools', name='browse-schools'),
    # TODO: change these routes so they are unique regardless of path query for reverse()
    url(r'^browse/(?P<school_query>[^/]+)$', 'notes.views.browse_courses', name='browse-courses'),
    url(r'^course/(?P<course_query>[^/]+)$', 'notes.views.browse_one_course', name='browse-course'),

    # User Profile
    url(r'^profile$', 'notes.views.profile', name='profile'),
    # User Profile Ajax submit
    url(r'^editProfile$', 'notes.views.editProfile', name='editProfile'),

    # Note View
    url(r'^file/(?P<note_pk>\d{1,99})$', 'notes.views.file', name='file'),
    url(r'^file/(?P<note_pk>\d{1,99})/(?P<action>[^/]+)$', 'notes.views.file'),

    url(r'^editFileMeta$', 'notes.views.editFileMeta', name='editFileMeta'),
    # Browse

    # Search
    url(r'^search/', 'notes.views.search'),

    # Ajax requests from search page to populate 'Browse by School and Course' accordion
    url(r'^browseBySchool/$', 'notes.views.searchBySchool', name='browse'),
    url(r'^browseByCourse/(\d{1,99})$', 'notes.views.notesOfCourse'),

    # Ajax Voting
    url(r'^vote/(\d{1,9999})$', 'notes.views.vote'),

    # Ajax requests from upload usher. Text input to model get / create
    url(r'^smartModelQuery$', 'notes.views.smartModelQuery'),

    # Ajax requests from note upload form for autocomplete fields
    url(r'^courses$', 'notes.views.courses'),
    url(r'^schools$', 'notes.views.schools'),
    url(r'^instructors$', 'notes.views.instructors'),
    url(r'^simple-autocomplete/', include('simple_autocomplete.urls')),

    # Ajax request to add a course to a user's profile
    url(r'^add-course', 'notes.views.add_course_to_profile', name='add-course'),

    # Add Course, School forms
    url(r'^add', 'notes.views.addModel', name='add'),

    # Edit course
    url(r'^editCourseMeta$', 'notes.views.editCourseMeta', name='editCourseMeta'),

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

    # latest browse views, must come last because they are greedy
    url(r'^schools$', 'notes.views.browse_schools', name='browse-schools'),
    # TODO: change these routes so they are unique regardless of path query for reverse()
    url(r'^b/(?P<school_query>[^/]+)/(?P<course_query>[^/]+)/(?P<file_id>\d{1,9999})/(?P<action>[^/]+)$', 'notes.views.nurl_file'),
    url(r'^b/(?P<school_query>[^/]+)/(?P<course_query>[^/]+)/(?P<file_id>\d{1,9999})$', 'notes.views.nurl_file', name='nurl_file'),
    url(r'^b/(?P<school_query>[^/]+)/(?P<course_query>[^/]+)$', 'notes.views.b_school_course', name='browse-course'),
    # Browse the courses of one school
    url(r'^b/(?P<school_query>[^/]+)$', 'notes.views.browse_courses', name='browse-courses'),
)
