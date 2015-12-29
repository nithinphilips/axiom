#!/usr/bin/env python3

"""
Converts a PM event record to a CRON expression
"""

import logging
import pytz

from argh import arg
from datetime import timedelta
from dateutil.rrule import *

from .ora_helper import execute, parse_db_url
from .queries import SQL_GET_EVENT, SQL_GET_EVENTS

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

@arg('pm_id', nargs='?', help="PM Schedule ID. Leave blank to show all PM Schedules.")
@arg('--db-url', help="Database TNS connection string.", default="tridata/tridata@localhost:1521:xe")
@arg('--default_count', help="The default number of events to generate for schedules with no end date", default="50")
@arg('--timezone', help="The local timezone", default="US/Eastern")
def eventparser(
        pm_id=None,
        db_url=None,
        default_count=None,
        timezone=None
    ):
    """
    Reads a PM Schedule recurrence rule from TRIRIGA database.
    """

    db = parse_db_url(db_url)
    logging.debug("Using database connection: " + str(db))
    connection = db.get_connection()

    events = get_events(connection, pm_id)

    for event in events:
        print("{}: {}".format(event["PM_ID"], event["PM_NAME"]))
        rrule, description = parse_event(event, timezone=timezone, default_count=default_count)
        print(description)
        print()
        print(str(rrule))
        print()

        for r in rrule:
            coerced = restrict_to_working_calendar(r)
            if r != coerced:
                print(r, " => ", coerced)
            else:
                print(r)

        print()

def get_events(connection, pm_id=None):
    if pm_id:
        rows = execute(SQL_GET_EVENT, connection, {'pm_id': pm_id})
    else:
        rows = execute(SQL_GET_EVENTS, connection)

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

def restrict_to_standard_calendar(expected_date, start_hour=8, end_hour=17):
    """
    Restrict date to TRIRIGA Working Calendar.

    If date is on a weekend, change it to the following Monday.

    If the start hour is before 8 AM, change it to 8:00 AM. 
    The seconds are unaltered to mimic TRIRIGA behavior.
    """

    if expected_date.isoweekday() == 6: # Sat
        expected_date = expected_date + timedelta(hours=48)
        expected_date = expected_date.replace(hour=start_hour, minute=0)
    elif expected_date.isoweekday() == 7: # Sun
        expected_date = expected_date + timedelta(hours=24)
        expected_date = expected_date.replace(hour=start_hour, minute=0)

    # Starts before 8 AM. Change start time to 8 AM
    if expected_date.hour < start_hour:
        expected_date = expected_date.replace(hour=start_hour, minute=0)

    # Starts after 5 PM. Change start time to 8 AM next day
    if expected_date.hour >= end_hour and expected_date.minute > 0:
        expected_date + timedelta(hours=24 - expected_date.hour) # Skip to next day
        expected_date = expected_date.replace(hour=start_hour, minute=0) # Change start hour

    return expected_date

def parse_event(event, timezone="US/Eastern", default_count=5000):

    # The times from database are always naive, without a timezone.
    # Tell python it's UTC, then convert to local TZ.
    local_tz = pytz.timezone(timezone)
    event['EVENTSTARTDATE'] = pytz.utc.localize(event['EVENTSTARTDATE'])
    event['EVENTSTARTDATE'] = local_tz.normalize(event['EVENTSTARTDATE'].astimezone(local_tz))

    event['EVENTENDDATE'] = pytz.utc.localize(event['EVENTENDDATE'])
    event['EVENTENDDATE'] = local_tz.normalize(event['EVENTENDDATE'].astimezone(local_tz))

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

    # 1. Start Date
    dtstart = event['EVENTSTARTDATE'].replace(tzinfo=None)

    # 2. Occurrence Type
    occurrence_type = event['RECURRENCEPATTERNTYPE']

    # 3. Schedule
    if occurrence_type == 'Single Occurrence':
        return [dtstart]

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

        # TODO: Months to Skip
        if monthly_recurrence == 'Day [x] of every [x] month(s)':
            bymonthday  = int(event['MONTHLYDAYOFMONTH'])
            interval = int(event['MONTHLYRECURRENCEMON'])
            description = "MONTHLY: Day {} of every {} month(s). Skip: ?".format(bymonthday, interval)
        elif monthly_recurrence == 'The [First] [Monday] of every [x] month(s)':
            interval = int(event['MONTHLYRECURRENCEMON'])
            byweekday = weekday_map[event['MONTHLYDAYOFWEEK']]
            bysetpos = weekofmonth_map[event['MONTHLYWEEKOFMONTH']]
            description = "MONTHLY: The {} {} of every {} month(s). Skip: ?".format(event['MONTHLYWEEKOFMONTH'], event['MONTHLYDAYOFWEEK'], interval)

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
        raise Exception("Ad hoc expressions are not supported")

    # 4. End Date
    if event['TRIRECURRENCEENDOPTI'] == 'End After':
        count = int(event['EVENTDURATION'])
    elif event['TRIRECURRENCEENDOPTI'] == 'End Date':
        until = event['EVENTENDDATE']
    else:
        count = int(default_count)

    result = rrule(freq, dtstart, interval, wkst, count, until, bysetpos, bymonth,
                   bymonthday, byyearday, byeaster, byweekno, byweekday, byhour,
                   byminute, bysecond, cache)

    return (result, description)
