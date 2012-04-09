The KarmaNotes Django Experiment
--------------------------------

What must be accomplished this weekend
======================================


models.py:

 + notes schema
 + user\_profile hooked up (add to settings.py)
 + schools and courses need to be fkey'd correctly
 * Optional: karma and karma\_actions

views.py:

 + XXX splashpage
 + XXX view all notes by school and course

./templates:

 + simple base.html template for header
 + XXX index.html for splashpage with current KN logo frontpage as-is
 + new notes.html template for rendering a list of notes
 + new note.html template for rendering a note and it's metadata

users:

 + login

 Note on Google Documents API
 ============================

 To authorize the Google Documents script to act on behalf of the target google account, verfication will have to be granted by visiting:

 https://accounts.google.com/DisplayUnlockCaptcha

 In my testing I haven't yet had the oauth token expire, but I'll have to investigate further.
