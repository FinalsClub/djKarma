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
import notes.views

from django.contrib import admin
admin.autodiscover()

# Be mindful of overly broad url patterns
# Remember the trailing $ to avoid partial match

urlpatterns = patterns('',

    # Landing page.
    url(r'^$', 'notes.views.home'),

    # About page
    url(r'^about$', 'notes.views.about'),

    # Upload page (Note Upload Form)
    url(r'^upload$', 'notes.views.uploadUsher', name='upload'),

     # Browse by School / Search by Tag view
    url(r'^browse$', 'notes.views.browse'),

    # User Profile
    url(r'^profile$', 'notes.views.profile', name='profile'),

    # Note View
    url(r'^file/(\d{1,99})$', 'notes.views.note'),

    # Haystack Search
    # url(r'^haysearch/', include('haystack.urls')),

    # Ajax requests from search page to populate 'Browse by School and Course' accordion
    url(r'^searchBySchool$', 'notes.views.searchBySchool'),
    url(r'^notesOfCourse/(\d{1,99})$', 'notes.views.notesOfCourse'),

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
    url(r'^add', 'notes.views.addCourseOrSchool', name='add'),

    # Auth
    # This logout allows us to pass a redirect:
    # <a href="{% url auth_logout_next /some/location %}">Logout</a>
    #url(r'^logout/(?P<next_page>.*)/$', 'django.contrib.auth.views.logout', name='auth_logout_next'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/register/$', 'notes.views.register', name='register'),
    url(r'', include('social_auth.urls')),


    # View all notes (unused)
    # url(r'^notes$', 'notes.views.all_notes'),

    # admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # admin:
    url(r'^admin/', include(admin.site.urls)),
)
