The KarmaNotes Django Experiment
================================

Dependencies
------------

 + Python2.7
 + django1.4
 + Solr3.6.0
 + django-celery2.5.5


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
6. Start celery task server (see Note)

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
#### add this line to your postgres install's /etc/postgresql/9.1/main/pg_hba.conf ####
local   karmanotes      djkarma                                 md5
sudo service postgresql restart
./manage.py syncdb # if you do not do this `run_gunicorn` will not be a command option
```
### Deploying Solr ###

1. You can generate the schema from the django application (once Haystack is installed and setup) by running ./manage.py build_solr_schema. 
2. Take the output from that command and place it in apache-solr-1.4.1/example/solr/conf/schema.xml. 
3. Restart Solr.

### Celery Task Server ###


The celery task server asynchronously handles the Google Documents API processing so the main django server remains responsive. When a document is uploaded via /upload, the django app (specifically the custom django-ajax-uploader backend) will ask the celery server to upload the document (now on the local server) to Google and await their response. The code which the celery server executes is actually located in ./notes/tasks.py

TODO: The new upload process works in two requests. One for the actual file, and a second for the file's meta data. If a file is processed but no meta data is submitted, the file needs to be marked specially. Currently, this behavior allows files without any meta data to appear wherever the site's files are displayed. Secondly, we need to create an avenue for a user to re-visit these incomplete uploads and enter meta data at their convenience. Only when this has happened should the files be displayed as normal.

To install and run the celery task server:

1. Ensure django-celery is installed per the requirements
2. Place the celery init.d script (./packaging/celeryd) in /etc/init.d/
3. Place the celery config file (./packaging/celeryconfig) in /etc/default
4. Make an unprivileged, non-password-enabled user and group to run celery
        useradd celery
        
5. make a spot for the logs and the pid files
        mkdir /var/log/celery
        mkdir /var/run/celery
        chown celery:celery /var/log/celery
        chown celery:celery /var/run/celery
6. chmod +x /etc/init.d/celeryd
7. run /etc/init.d/celeryd start


Note on Database migrations
---------------------------

I've installed South to help ease database migrations whenever the models.py file is altered.
South's workflow is as follows for changes to the 'notes' app:

To initialize South:

New project:

1. ./manage.py schemamigration notes --initial

Existing project:

1. ./manage.py convert_to_south notes


To perform migrations with South:

1. Alter models.py as needed
2. ./manage.py schemamigration notes --auto
3. ./manage.py migrate notes

Note on Creating a Development DB from Production DB
----------------------------------------------------

If you'd like to copy the current production database and use it during your development:

### ON PRODUCTION MACHINE: ###

1. ssh into production project root
2. Note the git state of the production project (with git log or likewise). NOTE: ignore merges performed by system users (Author will be a system user, not a GitHub user).
3. python manage.py dumpdata notes --exclude notes.userprofile > ~/dumps.json. Transfer dumps.json to development machine.

### ON DEVELOPMENT MACHINE: ###

4. checkout the commit corresponding to the production project state
5. Make sure south is commented out in settings.INSTALLED_APPS
5. manage.py syncdb (do NOT create superuser when prompted)
6a. IF syncdb loads fixtures, manage.py createsuperuser
6b. ELSE manage.py loaddata ./path/to/fixtures.json (or initial_data.json. The name's changed throughout the project history). Then manage.py createsuperuser
7. manage.py loaddata ~/dumps.json 

8. Now un-comment south from settings.INSTALLED_APPS and manage.py syncdb
9. manage.py convert_to_south notes
10. git pull origin master
11. manage.py schemamigration notes --auto
11a. if schemamigration prompts you for a default value. i.e: 
	
		Added field owner on notes.File
		? The field 'File.type' does not have a default specified, yet is NOT NULL.
 		? Since you are making this field nullable, you MUST specify a default
 		? value to use for existing rows. Would you like to:
 		?  1. Quit now, and add a default to the field in models.py
 		?  2. Specify a one-off value to use for existing columns now
 		?  3. Disable the backwards migration by raising an exception.
 		? Please select a choice: 2
 	
 	Simply enter 2 and enter a one-off value (In this case 'N' for Note) if you understand the data model. Else specify 3. In development, losing the ability to backwards migrate is not a big deal.

12) manage.py migrate notes


Note on Google Documents API
----------------------------

 To authorize the Google Documents script to act on behalf of the target google account, verfication will have to be granted by visiting:

 https://accounts.google.com/DisplayUnlockCaptcha

 In my testing I haven't yet had the oauth token expire, but I'll have to investigate further.


Style compilation
-----------------
To recompile css from the less source files, install the latest Node js, which comes with the npm package manager and install 'less'

# TODO automate this process, either with a make script or as a django ./manage.py command

less source files live in `djKarma/static/less` To recompile `style.css`, you must install lessc

    sudo npm install -g less

You will now have the command lessc available to you. run this command from the root of the project repo

    lessc ./static/less/styles.less ./static/css/styles.css
