from django.core.management.base import BaseCommand
from notes.models import File, UserProfile
from django.contrib.auth.models import User

class Command(BaseCommand):
    args = 'none'
    help = 'Assigns File.owner fields by determining user who first uploaded file'

    def handle(self, *args, **options):
        length = len(File.objects.all())
        count = 0
        default_user = -1
        while default_user != 0 and not User.objects.filter(pk=default_user).exists():
            default_user = raw_input("Enter a default user_pk to assign if no user candidates are found for a file.\n" +
                "Enter 0 to leave file.owner null if no candidate found : ")
            default_user = int(default_user)
        for file in File.objects.all():
            do_save = False
            if file.owner == None:
                potential_owners = file.userprofile_set.all()
                self.stdout.write('File: %s , Owner candidates: \n' % (file.title))
                if len(potential_owners) == 0:
                    self.stdout.write('> None. ')
                    if default_user != 0:
                        file.owner = User.objects.get(pk=default_user)
                        self.stdout.write('Assigning default user (pk=%s)\n' % default_user)
                        do_save = True
                    else:
                        self.stdout.write('\n')
                else:
                    for candidate in potential_owners:
                        self.stdout.write('> %s \n' % candidate.get_name())
                    self.stdout.write(' > Assigning first candidate \n')
                    file.owner = potential_owners[0].user
                    do_save = True
                #self.stdout.write('Populated academic year for  %s \n' % course.title)
            if do_save:
                count += 1
                file.save()

        self.stdout.write('\n Set File.owner for %d / %d files \n' % (count, length))
