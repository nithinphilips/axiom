#!/cygdrive/c/Python27/python.exe

"""
Produce a report to validate PM Schedules
"""

import logging
import pytz
import xlsxwriter

from argh import arg
from argh.exceptions import CommandError
from tqdm import tqdm
from xlsxwriter.utility import xl_rowcol_to_cell

from .ora_helper import execute, parse_db_url
from .pmeventparser import get_events, parse_event, restrict_to_working_calendar, localize_date
from .queries import SQL_GET_PMSCHEDS, SQL_GET_TASKS

xlFormats = dict()

def safe_xl_ws_name(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    if len(value) >= 32:
        value = value[0:31]
    return value

@arg('-d', '--db-url', help="Database connection string. USERNAME/PASSWORD@HOST:PORT:SID or USERNAME/PASSWORD@HOST:PORT/SERVICE_NAME", default="tridata/tridata@localhost:1521:xe")
@arg('-z', '--timezone', help="The local timezone", default="US/Eastern")
@arg('-u', '--site-url', help="The URL to TRIRIGA. It will be used to generate links to records.", default="http://localhost:9080")
@arg('-f', '--outputfile', help="The output file name.", default="axiom.xlsx")
@arg('-s', '--strip-time', help="Remove time component from dates before comparing.", default=False)
@arg('-w', '--working-calendar', choices=['8to5','24/7'], help="Choose a working calendar", default="8to5")
@arg('-v', '--verbosity', choices=range(0,3), help="Choose how much output to print to console", default=0)
def schedulevalidator(
        db_url=None,
        timezone=None,
        site_url=None,
        outputfile=None,
        strip_time=None,
        working_calendar=None,
        verbosity=None
    ):
    """
    Produces a report to verify PM Schedules in TRIRIGA.

    Example:

        axiom --db-url=tridata/tridata@localhost:1521:xe --site-url=http://localhost:9080 --timezone=US/Eastern

    """

    if site_url.endswith("/"):
        site_url = site_url[:-1]

    db = parse_db_url(db_url)
    logging.debug("Using database connection: " + str(db))
    connection = db.get_connection()

    # Get ALL PM Schedules
    pms = execute(SQL_GET_PMSCHEDS, connection)

    if len(pms) <= 0:
        raise CommandError("No PM Schedules found in {}".format(db))

    workbook = xlsxwriter.Workbook(outputfile)
    index_worksheet = workbook.add_worksheet(name="Index")

    xlFormats['bad'] = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    xlFormats['good'] = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    xlFormats['header'] = workbook.add_format({'bold': True, 'text_wrap': True})
    xlFormats['rrule'] = workbook.add_format({'text_wrap': True, 'valign': 'top'})

    # Validate each one
    for pm in tqdm(pms):
        try:
            validate_pm(pm['TRIIDTX'],
                        pm['TRINAMETX'],
                        workbook,
                        connection,
                        timezone,
                        strip_time,
                        working_calendar,
                        verbosity)
        except Exception as e:
            logging.exception("Unable to validate a PM. Ignore and continue.")

        if verbosity > 0:
            print()

    populate_index_worksheet(index_worksheet, pms, site_url)
    workbook.close()

def populate_index_worksheet(worksheet, pms, site_url):

    # Widen the columns to make the text clearer.
    worksheet.set_column('A:A', 9)
    worksheet.set_column('B:B', 50)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 13)
    worksheet.set_column('E:E', 13)
    worksheet.set_column('F:F', 13)

    for i, pm in enumerate(pms, start=1):
        url = site_url + "/pc/notify/link?recordId=" + str(pm["SPEC_ID"])

        table_name = "Table" + pm["TRIIDTX"]

        worksheet.write(i, 0, pm["TRIIDTX"])
        worksheet.write(i, 1, pm["TRINAMETX"])
        worksheet.write(i, 2, pm["TRIPMTYPECLASSCL"])
        worksheet.write(i, 3, '=COUNTIF({}[Valid?], "OK")'.format(table_name))
        worksheet.write(i, 4, '=COUNTIF({}[Valid?], "ERROR")'.format(table_name))
        formula = "={}+{}".format(xl_rowcol_to_cell(i, 3), xl_rowcol_to_cell(i, 4))
        worksheet.write(i, 5, formula)
        worksheet.write_url(i, 6,
                            url="internal:{}!A1".format(pm["TRIIDTX"]),
                            string="Details",
                            tip="View details about " + pm["TRIIDTX"])
        worksheet.write_url(i, 7,
                            url=url,
                            string="View",
                            tip="View record " + pm["TRIIDTX"] + " in TRIRIGA")

        cellA = xl_rowcol_to_cell(i, 3, row_abs=True, col_abs=True)
        cellB = xl_rowcol_to_cell(i, 5, row_abs=True, col_abs=True)
        worksheet.conditional_format(i, 3, i, 5, {'type': 'formula',
                                                  'criteria': "={}={}".format(cellA, cellB),
                                                  'format': xlFormats['good']})


    worksheet.add_table(0, 0, i, 7, { 'style': 'Table Style Light 11',
                                      'columns': [
                                          {'header': 'PM ID'},
                                          {'header': 'PM Schedule'},
                                          {'header': 'Recurrence'},
                                          {'header': 'Valid'},
                                          {'header': 'Invalid'},
                                          {'header': 'Total'},
                                          {'header': 'Details'},
                                          {'header': 'View'},
                                     ]})

    worksheet.activate()

def validate_pm(pm_id, pm_name, workbook, connection, timezone, strip_time=False, working_calendar="8to5", verbosity=1):

    event = get_events(connection, pm_id=pm_id, timezone=timezone)

    if len(event) <= 0:
        raise Exception("No recurrence pattern found for PM: {} {}.".format(pm_id, pm_name))
    elif len(event) > 1:
        logging.warn("More than one recurrence patterns found for PM: {} {}. Using the first one.".format(pm_id, pm_name))

    event = event[0]

    rrule, description = parse_event(event)

    if verbosity >= 1:
        print(pm_id + ": " + pm_name)

    if verbosity >= 2:
        print(description)
        print(str(rrule))

    tasks = execute(SQL_GET_TASKS, connection, {'pm_id': pm_id })

    total = 0
    ok_count = 0

    local_tz = pytz.timezone(timezone)

    worksheet = workbook.add_worksheet(name=safe_xl_ws_name(pm_id))

    # Widen columns
    worksheet.set_column(2, 2, 24)
    worksheet.set_column(3, 3, 24)

    worksheet.merge_range(0, 0, 0, 3, "{}: {}".format(pm_id, pm_name), xlFormats['header'])
    worksheet.merge_range(1, 0, 1, 3, description, xlFormats['rrule'])
    worksheet.merge_range(2, 0, 2, 3, str(rrule), xlFormats['rrule'])

    worksheet.write_url(0, 5,
                        url="internal:Index!A1",
                        string="Index",
                        tip="Return to Index page")

    worksheet.set_row(2, 30)

    rrule_itr = iter(rrule)
    for i, item in enumerate(tasks, start=4):
        expected_date = next(rrule_itr)

        item['TRIPLANNEDSTARTDT'] =  localize_date(item['TRIPLANNEDSTARTDT'], local_tz)

        actual_date = item['TRIPLANNEDSTARTDT']

        coerced_date = restrict_to_working_calendar(expected_date, working_calendar)
        # The order of execution is important.
        # ``restrict_to_working_calendar`` method may change the date to fall
        # IN or OUT of DST period. This will change the TZ offset.
        expected_date = local_tz.localize(expected_date)
        coerced_date = local_tz.localize(coerced_date)

        if expected_date != coerced_date:
            logging.debug("Coerce date: {} => {}".format(expected_date, coerced_date))

        expected_date = coerced_date

        if strip_time:
            # Strip off time
            expected_date = expected_date.date()
            actual_date = actual_date.date()

        ok = expected_date == actual_date

        if ok:
            ok_count = ok_count + 1
        total = total + 1

        formula = '=IF({}={},"OK","ERROR")'.format(xl_rowcol_to_cell(i, 2),
                                                   xl_rowcol_to_cell(i, 3))

        worksheet.write(i, 0, item["TASK_ID"])
        worksheet.write(i, 1, item["TASK_STATUS"])
        worksheet.write(i, 2, str(actual_date))
        worksheet.write(i, 3, str(expected_date))
        worksheet.write(i, 4, formula)

    worksheet.conditional_format(4, 4, i, 4, {'type': 'text',
                                              'criteria': "containing",
                                              'value': "ERROR",
                                              'format': xlFormats['bad']})

    worksheet.add_table(4, 0, i, 4, { 'style': 'Table Style Light 13',
                                      'name': 'Table' + pm_id,
                                      'columns': [
                                          {'header': 'Task ID'},
                                          {'header': 'Status'},
                                          {'header': 'Planned Start Date'},
                                          {'header': 'Expected Date'},
                                          {'header': 'Valid?'},
                                     ]})

    if verbosity >= 1:
        print("{} OK. {} Error. Total {}".format(ok_count, total - ok_count, total))

if __name__ == "__main__":
    main()

