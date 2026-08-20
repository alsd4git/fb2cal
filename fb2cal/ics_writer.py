import calendar
import os
from datetime import datetime, timedelta, timezone

from dateutil.relativedelta import relativedelta
from ics import Calendar, Event
from ics.grammar.parse import ContentLine

from .__init__ import __github_short_url__, __status__, __version__
from .logger import Logger
from .utils import generate_facebook_profile_url_permalink

""" Write Birthdays to an ICS file """


class ICSWriter:
    def __init__(self, contacts):
        self.logger = Logger("fb2cal").getLogger()
        self.contacts = contacts

    def generate(self):
        c = Calendar()
        c.scale = "GREGORIAN"
        c.method = "PUBLISH"
        c.creator = f"fb2cal v{__version__} ({__status__}) [{__github_short_url__}]"
        c.extra.append(
            ContentLine(name="X-WR-CALNAME", value="Facebook Birthdays (fb2cal)")
        )
        c.extra.append(ContentLine(name="X-PUBLISHED-TTL", value="PT12H"))
        c.extra.append(ContentLine(name="X-ORIGINAL-URL", value="/events/birthdays/"))

        # Keep the existing naive date representation while making the clock
        # source explicit and deterministic across host time zones.
        cur_date = datetime.now(timezone.utc).replace(tzinfo=None)

        for contact in self.contacts:
            # Don't add extra 's' if name already ends with 's'
            formatted_username = (
                f"{contact.name}'s" if contact.name[-1] != "s" else f"{contact.name}'"
            )
            formatted_username = f"{formatted_username} Birthday"

            # Set date components
            day = contact.birthday_day
            month = contact.birthday_month
            year = contact.birthday_year

            # The birth year may not be visible due to privacy settings
            # In this case, calculate the year as this year or next year based on if its past current month or not
            if year is None:
                year = (
                    cur_date.year
                    if contact.birthday_month >= cur_date.month
                    else (cur_date + relativedelta(years=1)).year
                )

            # Feb 29 special case:
            # If event year is not a leap year, use Feb 28 as birthday date instead
            if (
                contact.birthday_month == 2
                and contact.birthday_day == 29
                and not calendar.isleap(year)
            ):
                day = 28

            # Format date components as needed
            month = f"{month:02}"
            day = f"{day:02}"

            # Event meta data
            e = Event()

            e.uid = contact.id
            e.name = formatted_username
            e.created = cur_date
            e.description = (
                f"{contact}\n{generate_facebook_profile_url_permalink(contact)}"
            )
            e.begin = f"{year}-{month}-{day} 00:00:00"
            e.make_all_day()
            e.duration = timedelta(days=1)
            e.extra.append(ContentLine(name="RRULE", value="FREQ=YEARLY"))

            c.events.add(e)

        self.birthday_calendar = c

    def write(self, ics_file_path):
        # Remove blank lines
        ics_str = "".join([line.rstrip("\n") for line in self.birthday_calendar])

        self.logger.info("Saving ICS file to local file system...")

        directory = os.path.dirname(ics_file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(ics_file_path, mode="w", encoding="UTF-8") as ics_file:
            ics_file.write(ics_str)
        os.chmod(ics_file_path, 0o600)
        self.logger.info(
            f"Successfully saved ICS file to {os.path.abspath(ics_file_path)}"
        )

    def get_birthday_calendar(self):
        return self.birthday_calendar
