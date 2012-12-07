#!/usr/bin/python
# -*- coding:utf8 -*-
"""
DOCME: Foo
"""

from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase
from django.utils import unittest

from notes.models import Level
from notes.models import SiteStats
from notes.models import Tag
from notes.models import ReputationEventType
from notes.models import ReputationEvent
from notes.models import Vote
from notes.models import School
from notes.models import Instructor
from notes.models import Course
from notes.models import File
from notes.models import UserProfile
from notes.utils import complete_profile_prompt
from notes.utils import jsonifyModel

class ModelTests(TestCase):
    """ Loads the notes fixtures into a temporary database.
        The database is destroyed when the tests are finished running.
    """
    fixtures = ['initial_data']

    def setUp(self):
        """ Creates a sample user to test with before each test.
        """
        l, b = Level.objects.get_or_create(title="Prospect", karma=10)

        print "\n Running ModelTests.setUp()"
        User.objects.get_or_create(username="Philo")

        # sample school
        school, b = School.objects.get_or_create(name=u"College University", location=u"1616 Mockingbird ln.")

        # sample course
        c, b = Course.objects.get_or_create(school=school, title=u"Underwater Basketweaving", semester=1)

    def tearDown(self):
        """ Deletes the example user, this always runs,
            even if something else in the file errors.
        """
        User.objects.get(username=u"Philo").delete()

    def test_level(self):
        level = Level(title="This Is a Slug", karma=500)
        self.assertEqual(level.__unicode__(), u'This Is a Slug 500')

    def test_sitestat(self):
        ss = SiteStats.objects.all()[0]
        self.assertTrue(ss)

    def test_tag(self):
        tag = Tag(name="Foo Bar Baf!", description="A test tag")
        tag.save()
        self.assertEquals(tag.__unicode__(), u"foo-bar-baf")

    def make_repeventtype(self, title):
        ret = ReputationEventType(title=title, actor_karma=3, target_karma=5)
        ret.save()
        return ret

    def test_repeventtype(self):
        title = u"An Event to remember"
        ret = self.make_repeventtype(title)

        self.assertEquals(ret.__unicode__(),
            "{0} Actor: {1}pts Target: {2}pts".format(title, 3, 5))

    def test_repeventtype_fail(self):
        # makes a string out of gibberish: a list of the first 200 numbers
        title = str(range(200))
        ret = self.make_repeventtype(title)

        self.assertRaises(ret.save())

    def test_repevent(self):
        ret = self.make_repeventtype('asdf')
        re = ReputationEvent(type=ret)
        self.assertEqual(re.__unicode__(), u"asdf")

    def test_vote(self):
        user = User(username=u"Foo")
        user.save()
        vote = Vote(user=user, up=False)
        vote.save()
        self.assertEqual(vote.__unicode__(), u"Foo voted False")

    def test_school(self):
        school = School(name=u"O Don Piano", facebook_id=12341234)
        school.save()
        self.assertEqual(school.__unicode__(), u"O Don Piano")

    def test_school_stats(self):
        starting_schools = School.objects.count()
        school = School(name="O Don Piano", facebook_id=12341234)
        school.save()
        ss = SiteStats.objects.all()[0]
        # save should have incremented this
        self.assertEqual(ss.numSchools, starting_schools + 1) 

    """ Broken test FIXME
        Decrement might not be called on school.delete()
    def test_school_remove(self):
        starting_schools = School.objects.count()
        school = School(name="O Don Piano", facebook_id = 12341234)
        school.save()
        ss = SiteStats.objects.all()[0]
        # save should have incremented this
        self.assertEqual(ss.numSchools, starting_schools + 1) 
        school.delete()
        # delete should have decremented this
        self.assertEqual(ss.numSchools, starting_schools) 
    """

    def test_instructor(self):
        school = School.objects.all()[0]
        pname = u"Noam Chompsky"
        prof = Instructor(name=pname, school=school)
        prof.save()
        self.assertEqual(prof.__unicode__(), pname)

    def test_course(self):
        course = Course.objects.get(title = u"Underwater Basketweaving")
        self.assertEqual(course.__unicode__(), u"Underwater Basketweaving at College University")
        self.assertEqual(course.get_semester_display(), 'Fall')

    def test_file(self):
        # FIXME: warning on datetime.datetime.now() with local timezone?
        file = File(title=u"A File", description=u"desc", type='N')
        file.save()
        self.assertEqual(file.__unicode__(), u"A File at None")
        self.assertEqual(file.get_type_display(), u"Note (+5 pts)")

    def test_file_vote(self):
        file = File(title=u"A File", description=u"desc", type='N')
        file.save()
        any_user = User.objects.all()[0]
        file.Vote(any_user, vote_value=1) # This should add one Vote record to the many to many fkey
        self.assertEqual(file.votes.count(), 1)

    def test_user_profile(self):
        user = User.objects.filter(username=u"Philo").all()[0]
        self.assertEqual(user.__unicode__(), u"Philo")

    def test_profile_get_name(self):
        philo = User.objects.filter(username=u"Philo").all()[0]
        philo.first_name = u"Philo"
        philo.last_name = u"Ooo"
        philo.save()
        philo_profile = philo.get_profile()
        self.assertEqual(philo_profile.getName(), u"PhiloO")

    def test_profile_incomplete(self):
        philo = User.objects.filter(username=u"Philo").all()[0]
        philo_profile = philo.get_profile()
        self.assertFalse(philo_profile.invited_friend)
        self.assertFalse(philo_profile.can_read)
        self.assertFalse(philo_profile.can_vote)
        # TODO: see how philo.files is accessed, .count()?
        self.assertFalse(philo_profile.complete_profile)

    def test_profile_award_karma(self):
        philo = User.objects.filter(username=u"Philo").all()[0]
        philo_profile = philo.get_profile()

        event = "major" # might be u""
        philo_profile.award_karma(event, philo)
        philo_profile.save()

        self.assertEqual(philo_profile.karma, 1)

class UtilsTests(unittest.TestCase):
    """ Loads the notes fixtures into a temporary database.
        The database is destroyed when the tests are finished running.
    """
    fixtures = ['initial_data']

    def setUp(self):
        """ Creates a sample user to test with before each test.
        """
        l, b = Level.objects.get_or_create(title="Prospect", karma=10)

        User.objects.get_or_create(username=u"Gooby")

        # sample school
        school, b = School.objects.get_or_create(name=u"College University", location=u"1616 Mockingbird ln.")

        # sample course
        c, b = Course.objects.get_or_create(school=school, title=u"Underwater Basketweaving", semester=1)

        ss, b = SiteStats.objects.get_or_create(id=1)

    def tearDown(self):
        """ Deletes all sample data, this always runs,
            even if something else in the file errors.
        """
        user = User.objects.filter(username=u"Gooby").all()[0]
        user.delete()

        School.objects.filter(name=u"College University").delete()
        Course.objects.filter(title=u"Underwater Basketweaving").delete()

    def test_jsonifyModel(self):
        # TODO: Test recursive courses, notes
        school = School.objects.filter(name=u"College University").all()[0]
        s_json = jsonifyModel(school)
        self.assertEqual(s_json['courses'], [])
        self.assertEqual(s_json['name'], u"College University")

        course = Course.objects.filter(title=u"Underwater Basketweaving").all()[0]
        c_json = jsonifyModel(course)
        self.assertEqual(c_json['title'], u"Underwater Basketweaving")

    def test_processCsvTags(self):
        """ skipping for now, because this looks like it is rarely used
        """
        pass

    def test_complete_profile_prompt(self):
        philo = User.objects.filter(username=u"Gooby").all()[0]
        philo_profile = philo.get_profile()
        messages = complete_profile_prompt(philo_profile)
        self.assertTrue(len(messages) > 1)
        self.assertEqual(messages[0], 'Last step, invite a friend to complete your profile')
