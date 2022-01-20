import datetime
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from portal import get_collections
from portal.models import Archive

class Command(BaseCommand):
    help = 'Show which member highlights will display in which months.'

    def handle(self, *args, **options):
        members = Archive.objects.filter(is_member=True).exclude(finding_aid_prefix='BMRC').order_by('order')
    
        today = datetime.date.today()
    
        d = datetime.datetime(
            today.year,
            today.month,
            1
        )
        for m in range(len(members)):
            member = Archive.featured_archive_by_date(d)
            print('{} {}'.format(d.year, d.month))
            print('{} {}'.format(member.order, member.name))
            print('')
            if d.month < 12:
                d = datetime.datetime(
                    d.year,
                    d.month + 1,
                    1
                )
            else:
                d = datetime.datetime(
                    d.year + 1,
                    1,
                    1
                )
