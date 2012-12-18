import csv
from itertools import izip

from django.core.management.base import BaseCommand
from notes.models import UsdeSchool

    
class Command(BaseCommand):
    args = '<filename>'
    help = ("""Import USDE csv file. add schools to the UsdeSchool model. 
        Assumes the following header: 
        Institution_ID,Institution_Name,Institution_Address,Institution_City,Institution_State,Institution_Zip,Institution_Phone,Institution_OPEID,Institution_IPEDS_UnitID,Institution_Web_Address,Campus_ID,Campus_Name,Campus_Address,Campus_City,Campus_State,Campus_Zip,Campus_IPEDS_UnitID,Accreditation_Type,Agency_Name,Agency_Status,Program_Name,Accreditation_Status,Accreditation_Date_Type,Periods,Last Action"""
    )

    def parse_school_csv(self, filename):
        """parse a csv file, and return a list of dictionaries
        """
        headers = False
        schools = []

        with open(filename) as f:

            reader = csv.reader(f)
            headers = reader.next()
            for row in reader:
                schools.append(row)

        headers = [s.lower() for s in headers]

        return [ dict(izip(headers,school)) for school in schools ]

    def handle(self, *args, **kwargs):

        if len(args) < 1: 
            self.stdout.write('Provide a filename\n')
            return

        filename = args[0]

        school_dicts = self.parse_school_csv(filename)

        self.stdout.write('Importing from list of %d schools\n' % len(school_dicts))

        count = 0
        for s in school_dicts:
            print "\n      ^      \n\n"
            try:
                print "\t%s" % s['institution_id']
                usde_school = UsdeSchool.objects.get(institution_id=s['institution_id'])
            except UsdeSchool.DoesNotExist:
                print "\t"
                print "\t%s" % s['institution_id']
                print "\t%s" % s['institution_name']

                count += 1
                usde_school = UsdeSchool()
                usde_school.institution_id = s['institution_id']
                usde_school.institution_name = s['institution_name'] 
                usde_school.institution_address = s['institution_address'] 
                usde_school.institution_city = s['institution_city']
                usde_school.institution_state = s['institution_state']
                usde_school.institution_zip = s['institution_zip']
                usde_school.institution_phone = s['institution_phone']
                usde_school.institution_opeid = s['institution_opeid']
                usde_school.institution_ipeds_unitid = s['institution_ipeds_unitid']
                usde_school.institution_web_address = s['institution_web_address']
                # usde_school.campus_id = s['campus_id']
                # usde_school.campus_name = s['campus_name']
                # usde_school.campus_address = s['campus_address']
                # usde_school.campus_city = s['campus_city']
                # usde_school.campus_state = s['campus_state']
                # usde_school.campus_zip = s['campus_zip']
                # usde_school.campus_ipeds_unitid = s['campus_ipeds_unitid']
                # usde_school.accreditation_type = s['accreditation_type']
                # usde_school.agency_name = s['agency_name']
                # usde_school.agency_status = s['agency_status']
                # usde_school.program_name = s['program_name']
                # usde_school.accreditation_status = s['accreditation_status']
                # usde_school.accreditation_date_type = s['accreditation_date_type']
                # usde_school.periods = s['periods']
                # usde_school.last_action = s['last action'] #space in key handled manually
                usde_school.save()

        self.stdout.write('Imported %d unique schools\n' % count)








