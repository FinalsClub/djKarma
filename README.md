The KarmaNotes Django Experiment
================================

What needs to be done:
----------------------


views.py:

 + TODO: make list of routes we know that we have to implement

users:

 + TODO: find user interaction cases we haven't added yet

./templates:

 + Base template
 + Profile page

Lightboxes (lightboxen)

 + Login

Upload

 + create course on file upload
 + create user on file upload
 + create school on file upload
   + create approved flag on school model, only show in UI once admin approves school


Dependencies
------------

 + Python2.7
 + django1.4


To install python package dependencies run:

    pip install -r requirements.txt

TODO: add deployment dependcies

Deployment
----------

 + TODO: short desc of how to install and deploy on a deployment server, what server packages need to be running/installed, but not how to install them

Note on Database migrations
----------------------------

I've installed South to help ease database migrations whenever the models.py file is altered.
South's workflow is as follows for changes to the 'notes' app:

To initialize South:

New project:

1) ./manage.py schemamigration notes --initial

Existing project:

1) ./manage.py convert_to_south notes


To perform migrations with South:

1) Alter models.py as needed
2) ./manage.py schemamigration notes --auto
3) ./manage.py migrate notes

Note on Google Documents API
----------------------------

 To authorize the Google Documents script to act on behalf of the target google account, verfication will have to be granted by visiting:

 https://accounts.google.com/DisplayUnlockCaptcha

 In my testing I haven't yet had the oauth token expire, but I'll have to investigate further.

