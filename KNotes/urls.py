# urls.py is part of Karma Notes
# Copyright (C) 2012  FinalsClub Foundation

from django.conf.urls import patterns, include, url
from django.contrib import admin

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
    # Ajax requests from note upload form for autocomplete fields
    url(r'^courses$', 'notes.views.courses'),
    url(r'^schools$', 'notes.views.schools', name='schools'),
    url(r'^accredited-schools$', 'notes.views.accredited_schools'),
    url(r'^instructors$', 'notes.views.instructors'),
    # Ajax request to add a course to a user's profile
    url(r'^create-course', 'notes.views.create_course', name='create-course'),
    url(r'^add-course', 'notes.views.add_course_to_profile', name='add-course'),
    url(r'^drop-course', 'notes.views.drop_course', name='drop-course'),
    # Add Course, School forms
    url(r'^add', 'notes.views.addModel', name='add'),
    # Edit course

    #   ---------------------------------------------------
    ## Browsing schools, courses and files
    #url(r'^browse/schools$', 'notes.views.browse_schools', name='browse-schools'),
    # TODO: change these routes so they are unique regardless of path query for reverse()
    url(r'^b/(?P<school_query>[^/]+)/(?P<course_query>[^/]+)/(?P<file_id>\d{1,9999})/(?P<action>[^/]+)$', 'notes.views.nurl_file'),
    url(r'^b/(?P<school_query>[^/]+)/(?P<course_query>[^/]+)/(?P<file_id>\d{1,9999})$', 'notes.views.nurl_file', name='nurl_file'),
    url(r'^b/(?P<school_query>[^/]+)/(?P<course_query>[^/]+)$', 'notes.views.b_school_course', name='browse-course'),
    # Browse the courses of one school
    url(r'^b/(?P<school_query>[^/]+)$', 'notes.views.school', name='school'),

    # useful only for direct linking to file, and for ajaxuploader reverse url lookup
    url(r'^file/(?P<note_pk>\d{1,9999})$', 'notes.views.file', name='file'),
    url(r'^raw/(?P<note_pk>\d{1,9999})$', 'notes.views.raw_file', name='raw-file'),

    url(r'^browse$', 'notes.views.browse', name='browse'),
    url(r'^browse/courses$', 'notes.views.courses', name='browse-courses'),
    url(r'^browse/notes$', 'notes.views.notes', name='browse-notes'),
    url(r'^browse/schools$', 'notes.views.schools', name='browse-schools'),

    #   ---------------------------------------------------
    # Auth
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
