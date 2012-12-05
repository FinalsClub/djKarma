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

#from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_reset_done
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.views import password_reset_complete

from haystack.query import SearchQuerySet

admin.autodiscover()
# Example SearchQuerySet fed to Haystack's SearchView
sqs = SearchQuerySet().highlight()

# Be mindful of overly broad url patterns
# Remember the trailing $ to avoid partial match

urlpatterns = patterns('',

    #   ---------------------------------------------------
    # Test url patterns
    url(r'^404$', 'notes.views.e404', name='404'),
    # captcha test
    url(r'^captcha$', 'notes.views.captcha', name='captcha'),

    #   ---------------------------------------------------
    # Static pages
    url(r'^$', 'notes.views.home', name='home'),
    url(r'^about$', 'notes.views.about', name='about'),
    url(r'^dashboard$', 'notes.views.dashboard', name='dashboard'),
    url(r'^terms$', 'notes.views.terms', name='terms'),
    url(r'^jobs$', 'notes.views.jobs', name='jobs'),

    #   ---------------------------------------------------
    ## Personal pages
    # Karma events
    url(r'^getting-started$', 'notes.views.getting_started', name='getting-started'),
    url(r'^karma-events$', 'notes.views.karma_events', name='karma-events'),
    url(r'^profile$', 'notes.views.profile', name='profile'),

    #   ---------------------------------------------------
    # Search
    url(r'^search/', 'notes.views.search'),
    url(r'^multisearch/', 'notes.views.multisearch'),

    #   ---------------------------------------------------
    ## Ajax endpoints
    # Editing ajax points
    url(r'^editProfile$', 'notes.views.editProfile', name='editProfile'),
    url(r'^editFileMeta$', 'notes.views.editFileMeta', name='editFileMeta'),
    url(r'^editCourseMeta$', 'notes.views.editCourseMeta', name='editCourseMeta'),
    # Ajax File Upload
    url(r'^ajax-upload$', 'notes.views.import_uploader', name="ajax_upload"),
    # File meta data submission
    url(r'^filemeta$', 'notes.views.fileMeta', name='fileMeta'),
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
    url(r'^create-course', 'notes.views.create_course', name='create-course'),
    url(r'^add-course', 'notes.views.add_course_to_profile', name='add-course'),
    url(r'^drop-course', 'notes.views.drop_course', name='drop-course'),
    # Add Course, School forms
    url(r'^add', 'notes.views.addModel', name='add'),
    # Edit course

    #   ---------------------------------------------------
    ## Browsing schools, courses and files
    url(r'^browse/schools$', 'notes.views.browse_schools', name='browse-schools'),
    # TODO: change these routes so they are unique regardless of path query for reverse()
    url(r'^b/(?P<school_query>[^/]+)/(?P<course_query>[^/]+)/(?P<file_id>\d{1,9999})/(?P<action>[^/]+)$', 'notes.views.nurl_file'),
    url(r'^b/(?P<school_query>[^/]+)/(?P<course_query>[^/]+)/(?P<file_id>\d{1,9999})$', 'notes.views.nurl_file', name='nurl_file'),
    url(r'^b/(?P<school_query>[^/]+)/(?P<course_query>[^/]+)$', 'notes.views.b_school_course', name='browse-course'),
    # Browse the courses of one school
    url(r'^b/(?P<school_query>[^/]+)$', 'notes.views.browse_courses', name='browse-courses'),

    # useful only for direct linking to file, and for ajaxuploader reverse url lookup
    url(r'^file/(?P<note_pk>\d{1,9999})$', 'notes.views.file', name='file'),

    url(r'^browse$', 'notes.views.browse', name='browse'),

    #   ---------------------------------------------------
    # Auth
    # This logout allows us to pass a redirect:
    # <a href="{% url auth_logout_next /some/location %}">Logout</a>
    #url(r'^logout/(?P<next_page>.*)/$', 'django.contrib.auth.views.logout', name='auth_logout_next'),
    url(r'^accounts/confirm/(?P<confirmation_code>[^/]+)$', 'notes.views.confirm_email', name='confirm_email'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    # accepts the username that invited
    url(r'^accounts/register/(?P<invite_user>[0-9A-Fa-f]*)$', 'notes.views.register', name='register_account'),
    url(r'', include('social_auth.urls')),
    url(r'^accounts/password/reset/$', password_reset, {'template_name': 'registration/password_reset.html', 'post_reset_redirect': '/accounts/password/reset/done/'}, name='password_reset'),
    url(r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {'template_name': 'registration/password_reset.html',  'post_reset_redirect': '/'}, name='password_reset_confirm'),
    url(r'^accounts/password/reset/done/?$', password_reset_done, {'template_name': 'registration/password_reset_done.html'}),
    url(r'^accounts/password/reset/confirm/?$', password_reset_confirm, {'template_name': 'registration/password_reset_confirm.html'}),
    url(r'^accounts/password/reset/complete/?$', password_reset_complete, {'template_name': 'registration/password_reset_complete.html'}),
    #url(r'^accounts/password/reset/$', password_reset, {}),

    # admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^oauth2callback', 'notes.views.gdrive_oauth_handshake'),
)
    # Ajax requests from search page to populate 'Browse by School and Course' accordion
    # Not being used and might be depricated
    #url(r'^browseBySchool/$', 'notes.views.searchBySchool', name='browse'),
    # TODO: change these routes so they are unique regardless of path query for reverse()
    #url(r'^browse/(?P<school_query>[^/]+)$', 'notes.views.browse_courses', name='browse-courses'), # This is a duplicate
    #url(r'^course/(?P<course_query>[^/]+)$', 'notes.views.browse_one_course', name='browse-course'),
    # latest browse views, must come last because they are greedy
    #url(r'^schools$', 'notes.views.browse_schools', name='browse-schools'),
    # Note View
    #url(r'^file/(?P<note_pk>\d{1,99})/(?P<action>[^/]+)$', 'notes.views.file'),
