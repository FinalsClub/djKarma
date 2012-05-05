The KarmaNotes Django Experiment
================================

What needs to be done:
----------------------

### Proper Search ###
+ Currently notes.views.search returns a union of all tags entered


### Initial Data in Autocomplete ###
+ Currently, the Autocomplete fields do not reflect initial-value populating. Until this is remedied the profile page form will not be autocomplete (because the most common case is the user all ready has their profile info entered)

#### Static pages ####

 + Find andrew's about & legal page text and put them in git
 + Finalize static page template
 + Add statics to extend static page template

#### Uploads ####

 + pass list of tags, courses, professors, schools to the upload form. 
    With caching this should not be expensive
    This is so we can tab-complete everything that already exists
 + If we can't autocomplete to text we already have, accept it in the JS and POST the response
 + on return, check if exists, if it doesn't create it (create an abstract logic for this)
    + Create course on return
    + Create tag on return
    + Create professor on return

#### tmpls ####

 + Convert base template to use bootstrap grid
 + adapt the upload page to a span-6
 + adapt search page to span-8 (centered?)
 + Add text explaining the landing/upload page
 + lightboxes
    + Find and report how bootstrap does lightboxes / modal dialogs
    + Create login and register lightboxes

#### Upload FC archive ####
TODO: Document steps required, location of current archive


Dependencies
------------

 + Python2.7
 + django1.4
 + Solr3.6.0


To install python package dependencies run:

    pip install -r requirements.txt

TODO: add deployment dependcies

Deployment
----------

1. checkout the git repository, we use `/var/www/djKarma` and will refer to this as the root of the repo
2. install requirements with `sudo pip install -r requirements.txt`
3. Create the database if a new deployment with `./manage.py syncdb` If this is not a new deployment, see the section below on database migrations. NOTE: You can't create a superuser BEFORE loading the fixtures.
4. If a new deployment install the initial data (schools, courses, sample data, a SiteStat object, and ReputationEventTypes). `./manage.py loaddata ./fixtures/fixtures.json`. 
5. Create superuser. `./manage.py createsuperuser

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
./manage.py syncdb # if you do not do this `run_gunicorn` will not be a command option
```
### Deploying Solr ###

1) You can generate the schema from the django application (once Haystack is installed and setup) by running ./manage.py build_solr_schema. 
2) Take the output from that command and place it in apache-solr-1.4.1/example/solr/conf/schema.xml. 
3) Restart Solr.

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

