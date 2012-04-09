from django.conf.urls import patterns, include, url
import notes.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Be mindful of overly broad url patterns
    # Prior, ^notes was pre-empting ^notesOfSchool/
    # Remember the trailing $ to avoid partial match
    url(r'^note/(\d{1,99})$', 'notes.views.note'),
    url(r'^notes$', 'notes.views.all_notes'),
    url(r'^searchBySchool$', 'notes.views.searchBySchool'),
    url(r'^notesOfSchool/(\d{1,99})', 'notes.views.notesOfSchool'),
    url(r'^$', 'notes.views.home'),

    # url(r'^KNotes/', include('KNotes.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
