#!/usr/bin/python
# -*- coding:utf8 -*-
"""
Profile Tasks.
    A ProfileTask is an object that contains a message, and a condition.
    ProfileTasks are things to be accomplished by a User after they register to
    complete their profile.  When all of the checks pass True, then the
    profile_complete flag may be set on the User object, and this module will
    not be checked again.

    A ProfileTask might be extended to add the following:

    karma_reward:   What kind of karma reward a user recieves after passing the
                    check (function)
    relevance:      If this ProfileTask applies to a User Example: AddedUsername
                    isn't required if the user registers from Facebook
"""
class AddedUsername():
    message = u"What should we call you? Add a username on the left"
    div_id = u"add-username-alert"
    karma = 4
    # Tag the div corresponding to this alert so it can be hidden
    # without page reload

    def check(self, user_profile):
        if user_profile.user.username != None:
            return True
        else:
            return False

class InvitedFriend():
    message = u"Last step, invite a friend to complete your profile"
    div_id = u"invite-friend-alert"
    karma = 5

    def check(self, user_profile):
        # where invited_friend is a boolean
        return user_profile.invited_friend

class AddedSchool():
    message = u"To get the most out of KarmaNotes, you need to add your school."
    div_id = u"add-school-alert"
    karma = 5

    def check(self, user_profile):
        if user_profile.school != None:
            return True
        else:
            return False

class AddedGradYear():
    message = u"Choose the year you are graduating from the dropdown under Profile on the left"
    div_id = u"add-gradyear-alert"
    karma = 3

    def check(self, user_profile):
        if user_profile.grad_year != None:
            return True
        else:
            return False

class UploadedFile():
    message = u"Share your first file with other users of KarmaNotes"
    div_id = u"upload-a-file"
    karma = u"5-10"

    def check(self, user_profile):
        if len(user_profile.files.all()) >= 1:
            return True
        return False

tasks = [ AddedUsername, AddedGradYear, AddedSchool, InvitedFriend, UploadedFile ]
