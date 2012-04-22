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

1. checkout the git repository, we use `/var/www/djKarma` and will refer to this as the root of the repo
2. install requirements with `sudo pip install -r requirements.txt`
3. Create the database if a new deployment with `./manage.py syncdb` If this is not a new deployment, see the section below on database migrations
4. If a new deployment install the initial data (schools, courses, sample data, and a SiteStat object) `./manage.py loaddata ./notes/fixtures.json`

 + TODO: short desc of how to install and deploy on a deployment server, what server packages need to be running/installed, but not how to install them

### Deployment database ###
To initially deploy the postgres backup on a fresh debian based system:
```
sudo apt-get install postgresql-9.1 python-psycopg2
sudo passwd postgres
sudo su postgres
sudo -u postgres createuser -P djkarma
psql template1
create database karmanotes owner djkarma encoding 'UTF8';
# add this line to your postgres install's /etc/postgresql/9.1/main/pg_hba.conf
local   karmanotes      djkarma                                 md5
sudo service postgresql restart
```

Note on Database migrations
---------------------------

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

