The KarmaNotes Django Experiment
================================

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


Style compilation
-----------------
To recompile css from the less source files, install the latest Node js, which comes with the npm package manager and install 'less'
TODO: Flesh our this after fixing issue #6
