#!/usr/bin/env python3

"""
Converts a PM event record to a CRON expression
"""

import logging
import pytz
import pprint

from argh import arg
from datetime import timedelta
from dateutil.rrule import *

from .ora_helper import execute, parse_db_url
from .queries import SQL_GET_EVENT, SQL_GET_EVENTS, SQL_GET_INCLUDES, SQL_GET_EXCLUDES

month_map = {
    'January'   : 1,
    'February'  : 2,
    'March'     : 3,
    'April'     : 4,
    'May'       : 5,
    'June'      : 6,
    'July'      : 7,
    'August'    : 8,
    'September' : 9,
    'October'   : 10,
    'November'  : 11,
    'December'  : 12
}

month_map_rev = {
  1  : 'January',
  2  : 'February',
  3  : 'March',
  4  : 'April',
  5  : 'May',
  6  : 'June',
  7  : 'July',
  8  : 'August',
  9  : 'September',
  10 : 'October',
  11 : 'November',
  12 : 'December',
}

weekday_map = {
    'Sunday'    : SU,
    'Monday'    : MO,
    'Tuesday'   : TU,
    'Wednesday' : WE,
    'Thursday'  : TH,
    'Friday'    : FR,
    'Saturday'  : SA
}

weekofmonth_map = {
    'First'  : 1,
    'Second' : 2,
    'Third'  : 3,
    'Fourth' : 4,
    'Last'   : -1
}

@arg('pm_id', nargs='?', help="PM Schedule ID. Leave blank to show all PM Schedules.", default=None)
@arg('-d', '--db-url', help="Database TNS connection string.", default="tridata/tridata@localhost:1521:xe")
@arg('-t', '--count', help="The default number of events to generate for schedules with no end date", default="50")
@arg('-z', '--timezone', help="The local timezone", default="US/Eastern")
@arg('-w', '--working-calendar', choices=['8to5','24/7'], help="Choose a working calendar", default="8to5")
@arg('-v', '--verbosity', choices=range(0,3), help="Choose how much output to print to console", default=0)
def eventparser(
        pm_id,
        db_url=None,
        count=None,
        timezone=None,
        working_calendar=None,
        verbosity=None
    ):
    """
    Reads a PM Schedule recurrence rule from TRIRIGA database.
    """

    db = parse_db_url(db_url)
    logging.debug("Using database connection: " + str(db))
    connection = db.get_connection()

    local_tz = pytz.timezone(timezone)
    events = get_events(connection, pm_id, timezone=timezone)

    for event in events:
        print("{}: {}".format(event["PM_ID"], event["PM_NAME"]))
        rrule, description = parse_event(event, default_count=count)
        print(description)
        print()
        print(rrule_str(rrule))
        print()

        for occurance in rrule:
            coerced = restrict_to_working_calendar(occurance, working_calendar=working_calendar)

            coerced = local_tz.localize(coerced)
            occurance = local_tz.localize(occurance)

            if occurance != coerced:
                print(occurance, " => ", coerced)
            else:
                print(occurance)

        print()

def get_events(connection, pm_id=None, timezone="US/Eastern"):

    # The times from database are always naive, without a timezone.
    # Tell python it's UTC, then convert to local TZ.
    local_tz = pytz.timezone(timezone)

    if pm_id:
        rows = execute(SQL_GET_EVENT, connection, {'pm_id': pm_id})
    else:
        rows = execute(SQL_GET_EVENTS, connection)

    # Get includes and excludes
    for event in rows:
        event['EVENTSTARTDATE'] = localize_date(event['EVENTSTARTDATE'], local_tz)
        event['EVENTENDDATE'] = localize_date(event['EVENTENDDATE'], local_tz)

        includes = execute(SQL_GET_INCLUDES, connection, {'event_spec_id': event["EVENT_SPEC_ID"]})
        excludes = execute(SQL_GET_EXCLUDES, connection, {'event_spec_id': event["EVENT_SPEC_ID"]})

        for inc in includes:
            inc['INC_STARTDT'] = localize_date(inc['INC_STARTDT'], local_tz)

        for excl in excludes:
            excl['EXCL_STARTDT'] = localize_date(excl['EXCL_STARTDT'], local_tz)
            excl['EXCL_ENDDT'] = localize_date(excl['EXCL_ENDDT'], local_tz)

        event["_INCLUDES"] = includes
        event["_EXCLUDES"] = excludes

    if not rows:
        raise Exception("PM Schedule '{}' was not found.".format(pm_name))

    return rows

def restrict_to_working_calendar(expected_date, working_calendar="8to5"):
    """
    Restrict date to TRIRIGA Working Calendar.
    """

    working_calendar = working_calendar.lower()

    if working_calendar == "8to5":
        return restrict_to_standard_calendar(expected_date, start_hour=8, end_hour=17)
    elif working_calendar == "24/7":
        return expected_date

def restrict_to_standard_calendar(expected_date, start_hour=8, end_hour=17, verbose=False):
    """
    Restrict date to TRIRIGA Working Calendar.

    If date is on a weekend, change it to the following Monday.

    If the start hour is before 8 AM, change it to 8:00 AM.
    The seconds are unaltered to mimic TRIRIGA behavior.
    """

    if verbose:
        print("{} < {} = {}".format(expected_date.hour, start_hour, expected_date.hour < start_hour))

    # Starts before 8 AM. Change start time to 8 AM
    if expected_date.hour < start_hour:
        if verbose:
            print("Starts before 8 AM. Change start time to 8 AM")
        expected_date = expected_date.replace(hour=start_hour, minute=0)

    if verbose:
        print("{} >= {} and {} > 0 = {}".format(expected_date.hour, end_hour, expected_date.minute, expected_date.hour >= end_hour and expected_date.minute > 0))

    # Starts after 5 PM. Change start time to 8 AM next day
    if expected_date.hour > end_hour or (expected_date.hour == end_hour and expected_date.minute > 0):
        if verbose:
            print("Starts after 5 PM. Change start time to 8 AM next day")
        expected_date = expected_date + timedelta(hours=24 - expected_date.hour) # Skip to next day
        expected_date = expected_date.replace(hour=start_hour, minute=0) # Change start hour

    if expected_date.isoweekday() == 6: # Sat
        expected_date = expected_date + timedelta(hours=48)
        expected_date = expected_date.replace(hour=start_hour, minute=0)
    elif expected_date.isoweekday() == 7: # Sun
        expected_date = expected_date + timedelta(hours=24)
        expected_date = expected_date.replace(hour=start_hour, minute=0)

    return expected_date


def localize_date(naiveutcdate, timezone):
    """
    Localize a naive UTC date.
    """
    utcdate = pytz.utc.localize(naiveutcdate)
    localdate = timezone.normalize(utcdate.astimezone(timezone))
    return localdate

def parse_event(event, default_count=5000, verbosity=1):
    """
    """

    if verbosity >= 2:
        logging.debug(pprint.pformat(event))

    freq=None
    dtstart=None
    interval=1
    wkst=None
    count=None
    until=None
    bysetpos=None
    bymonth=None
    bymonthday=None
    byyearday=None
    byeaster=None
    byweekno=None
    byweekday=None
    byhour=None
    byminute=None
    bysecond=None
    cache=False

    description = None

    skip_months = []

    # 1. Start Date
    dtstart = event['EVENTSTARTDATE'].replace(tzinfo=None)

    # 2. Occurrence Type
    occurrence_type = event['RECURRENCEPATTERNTYPE']

    # 3. Schedule
    if occurrence_type == 'Single Occurrence':
        description = "Single occurrence on " + str(dtstart)
        ruleset = rruleset()
        ruleset.rdate(dtstart)
        # Return here because we don't need to check the rest of the values
        # They may be undefined
        return (ruleset, description)

    elif occurrence_type == 'DAILY':
        freq = DAILY

        daily_recurrence = event['TRIRECURRENCEDAILYOP']

        description = "DAILY: " + daily_recurrence

        if daily_recurrence == 'Every [x] day(s)':
            interval  = int(event['DAILYRECURRENCEDAYS'])
            description = "DAILY: Every {} day(s)".format(interval)
        elif daily_recurrence == 'Every weekday':
            byweekday  = [MO,TU,WE,TH,FR]
        elif daily_recurrence == 'Every weekend day':
            byweekday  = [SA,SU]

    elif occurrence_type == 'WEEKLY':
        freq = WEEKLY
        interval = int(event['WEEKLYRECURRENCEWEEKS'])
        byweekday = []

        if event['WEEKLYSUNDAY'] == 'TRUE':
            byweekday.append(SU)
        if event['WEEKLYMONDAY'] == 'TRUE':
            byweekday.append(MO)
        if event['WEEKLYTUESDAY'] == 'TRUE':
            byweekday.append(TU)
        if event['WEEKLYWEDNESDAY'] == 'TRUE':
            byweekday.append(WE)
        if event['WEEKLYTHURSDAY'] == 'TRUE':
            byweekday.append(TH)
        if event['WEEKLYFRIDAY'] == 'TRUE':
            byweekday.append(FR)
        if event['WEEKLYSATURDAY'] == 'TRUE':
            byweekday.append(SA)

        description = "WEEKLY: Recur every {} week(s) on {}".format(interval, byweekday)

    elif occurrence_type == 'MONTHLY':
        freq = MONTHLY

        monthly_recurrence = event['TRIRECURRENCEMONTHLY']

        if event['TRIJANUARYBL'] == 'TRUE':
            skip_months.append(1)
        if event['TRIFEBRUARYBL'] == 'TRUE':
            skip_months.append(2)
        if event['TRIMARCHBL'] == 'TRUE':
            skip_months.append(3)
        if event['TRIAPRILBL'] == 'TRUE':
            skip_months.append(4)
        if event['TRIMAYBL'] == 'TRUE':
            skip_months.append(5)
        if event['TRIJUNEBL'] == 'TRUE':
            skip_months.append(6)
        if event['TRIJULYBL'] == 'TRUE':
            skip_months.append(7)
        if event['TRIAUGUSTBL'] == 'TRUE':
            skip_months.append(8)
        if event['TRISEPTEMBERBL'] == 'TRUE':
            skip_months.append(9)
        if event['TRIOCTOBERBL'] == 'TRUE':
            skip_months.append(10)
        if event['TRINOVEMBERBL'] == 'TRUE':
            skip_months.append(11)
        if event['TRIDECEMBERBL'] == 'TRUE':
            skip_months.append(12)

        # TODO: Months to Skip
        if monthly_recurrence == 'Day [x] of every [x] month(s)':
            bymonthday  = int(event['MONTHLYDAYOFMONTH'])
            interval = int(event['MONTHLYRECURRENCEMON'])
            description = "MONTHLY: Day {} of every {} month(s). Skip: {}".format(bymonthday, interval, list(map(month_map_rev.get, skip_months)))
        elif monthly_recurrence == 'The [First] [Monday] of every [x] month(s)':
            interval = int(event['MONTHLYRECURRENCEMON'])
            byweekday = weekday_map[event['MONTHLYDAYOFWEEK']]
            bysetpos = weekofmonth_map[event['MONTHLYWEEKOFMONTH']]
            description = "MONTHLY: The {} {} of every {} month(s). Skip: {}".format(event['MONTHLYWEEKOFMONTH'], event['MONTHLYDAYOFWEEK'], interval, list(map(month_map_rev.get, skip_months)))

    elif occurrence_type == 'YEARLY':
        freq = YEARLY

        yearly_recurrence = event['TRIRECURRENCEYEARLYO']

        if yearly_recurrence == 'Every [May] [1]':
            bymonthday = int(event['YEARLYDAYOFMONTH'])
            bymonth = month_map[event['YEARLYMONTH']]
            description = "YEARLY: Every {} {}".format(event['YEARLYMONTH'], event['YEARLYDAYOFMONTH'])
        elif yearly_recurrence == 'The [First] [Monday] of [May]':
            bymonth = month_map[event['YEARLYMONTH']]
            byweekday = weekday_map[event['YEARLYDAYOFWEEK']]
            bysetpos = weekofmonth_map[event['YEARLYWEEKOFMONTH']]
            description = "YEARLY: The {} {} of {}".format(event['YEARLYWEEKOFMONTH'], event['YEARLYDAYOFWEEK'], event['YEARLYMONTH'])

    elif occurrence_type == 'Ad hoc':
        description = "Ad hoc"
        ruleset = rruleset()
        for inc in event['_INCLUDES']:
            ruleset.rdate(inc['INC_STARTDT'].replace(tzinfo=None))

        # Return here because we don't need to check the rest of the values
        # They may be undefined
        return (ruleset, description)

    # 4. End Date
    end_option = event['TRIRECURRENCEENDOPTI']
    logging.debug("End Option: " + end_option)
    if end_option == 'End After':
        count = int(event['EVENTDURATION'])
    elif end_option == 'End Date':
        until = event['EVENTENDDATE']

    if (count and count <= 0) or not until:
        count = int(default_count)

    result = rrule(freq, dtstart, interval, wkst, count, until, bysetpos, bymonth,
                   bymonthday, byyearday, byeaster, byweekno, byweekday, byhour,
                   byminute, bysecond, cache)


    ruleset = rruleset()
    ruleset.rrule(result)

    # Also Schedule On
    for inc in event['_INCLUDES']:
        logging.debug("Also schedule on: " + str(inc['INC_STARTDT']))
        ruleset.rdate(inc['INC_STARTDT'].replace(tzinfo=None))

    # Exclusion ranges
    for excl in event['_EXCLUDES']:
        excl_start = excl['EXCL_STARTDT'].replace(tzinfo=None)
        excl_end = excl['EXCL_ENDDT'].replace(tzinfo=None)

        # Adjust excl_start time portion to match the main rule time
        if excl_start.hour >= dtstart.hour:
            # The exclusion start after the mail rule. Skip to next day
            excl_start = excl_start + timedelta(hours=24)
            excl_start = excl_start.replace(hour=dtstart.hour,
                                            minute=dtstart.minute,
                                            second=dtstart.second,
                                            microsecond=dtstart.microsecond)
        else:
            excl_start = excl_start.replace(hour=dtstart.hour,
                                            minute=dtstart.minute,
                                            second=dtstart.second,
                                            microsecond=dtstart.microsecond)

        logging.debug("Exclusion start changed from {} to {}".format(excl['EXCL_STARTDT'], excl_start))

        logging.debug("Exclude from {} to {}".format(excl_start, excl_end))
        exclusion_rule = rrule(DAILY, dtstart=excl_start, until=excl_end)
        ruleset.exrule(exclusion_rule)


    logging.debug(result)

    if len(skip_months) > 0:
        # Skip all days in the SKIP months. The time has to match the include
        # rule times.
        skip_months_rule = rrule(DAILY, dtstart=dtstart, bymonth=skip_months)
        logging.debug(skip_months_rule)
        ruleset.exrule(skip_months_rule)

    return (ruleset, description)


def rrule_str(rules):
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

    file_str = StringIO()

    if isinstance(rules, rruleset):
        file_str.write("Include Rules:\n")
        for arule in rules._rrule:
            file_str.write(str(arule) + "\n")

        file_str.write("\nInclude Dates:\n")
        for arule in rules._rdate:
            file_str.write(str(arule) + "\n")

        file_str.write("\nExclude Rules:\n")
        for arule in rules._exrule:
            file_str.write(str(arule) + "\n")

        file_str.write("\nExclude Dates:\n")
        for arule in rules._exdate:
            file_str.write(str(arule) + "\n")
    else:
        file_str.write(str(rules))

    return file_str.getvalue()

