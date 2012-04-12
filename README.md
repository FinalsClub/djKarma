The KarmaNotes Django Experiment
--------------------------------

What must be accomplished this weekend
======================================


models.py:

 + notes schema                   DONE
 + user\_profile hooked up (add to settings.py)
 + schools and courses need to be fkey'd correctly DONE
 * Optional: karma and karma\_actions

views.py:

 + splashpage	DONE
 + view all notes by school and course 	DONE

./templates:

 + simple base.html template for header DONE
 + index.html for splashpage with current KN logo frontpage as-is DONE
 + new notes.html template for rendering a list of notes
 + new note.html template for rendering a note and it's metadata

users:

 + login

Note on Database migrations
============================

I've installed South to help ease database migrations whenever the models.py file is altered.
South's workflow is as follows for changes to the 'notes' app:

1) Alter models.py as needed
2) ./manage.py schemamigration notes --auto
3) ./manage.py migrate notes

Note on Google Documents API
============================

 To authorize the Google Documents script to act on behalf of the target google account, verfication will have to be granted by visiting:

 https://accounts.google.com/DisplayUnlockCaptcha

 In my testing I haven't yet had the oauth token expire, but I'll have to investigate further.


Priorities for Tuesday
======================
1. tags         DONE
2. prettier, design
3. users
4. profile page and 

add 10 things tomorrow, 100 things friday
