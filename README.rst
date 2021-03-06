Axiom
=====
Axiom produces a report that can be used to verify if TRIRIGA-generated PM
Schedules are correct. Our customers have noticed that tririga occasionally
creates *duplicates*, *skips scheduled tasks* and otherwise acts inconsistently
when creating tasks from PM Schedules. Axiom can be used to quickly check for
any anomalies.

Getting Started
---------------
Windows Users
~~~~~~~~~~~~~
An installer is available for Windows. Download it from the `Releases
<https://github.com/nithinphilips/axiom/releases>`_ section.  Once installed,
you will have the ``axiom`` command available in your Command Prompt.

All Other Platforms
~~~~~~~~~~~~~~~~~~~
Install Python 3.4. Download the source and install Axiom and its
dependencies::

    python setup.py install

Usage
-----
Simplest use case::

    axiom

This will run the tool against ``localhost:1521:xe`` with all the default
options. If there are no errors, Axiom will not produce any output on the
console. It will create a file (see `The Excel File`_) called ``axiom.xlsx``
in the current directory.

To specify a database::

    axiom --db-url=tridata/tridata@remotedb:1521:orcl --site-url=http://localhost:9080

You can report on a selected set of PM Schedules by passing in the PM Schedule ID::

    axiom --db-url=tridata/tridata@remotedb:1521:orcl \
          --site-url=http://localhost:9080 \
          1000001 1000002

To see all available arguments, run::

    axiom --help

The Excel File
--------------
The output of Axiom is an Excel file. By default it is named ``axiom.xlsx``.
You may change the file name using the ``--outputfile`` (``-f``) flag.

The excel file will have 2 or more worksheets. The first worksheet is always
called *Index*. This sheet summarizes the individual PM Schedules. You can use
the links in the Index worksheet to see more details about individual PM
Schedules.

The **Valid** column shows the number of tasks that Axiom has identified as
correctly dated. **Invalid** column shows the tasks that are not dated
correctly. If the *Valid* count is equal to *Total* count, the *Valid*,
*Invalid* and *Total* cells will be colored green.

The **Task Grouping?** column will indicate whether this PM Schedule is
configured to create a single task for all assets/locations or multiple tasks.
If Task Grouping is Yes, Axiom will group the tasks by Planned Start Date.  You
can see the number of tasks with the same Planned Start date by looking at the
**Task Count** column in the detail worksheet.

Click on the *View* link to open the PM Schedule in TRIRIGA. This will only
work if you specified the site url with the ``--site-url`` (``-u``) flag.

To see detailed validation results for a PM Schedule, click on the *Details*
link. This will take you to the appropriate detail worksheet. This sheet will
display all the tasks associated to the PM Schedule. The **Planned Start Date**
from the work task is compared against an **Expected Date** to see if the
generated task has the correct start date. The results are displayed in the
**Valid?** column.

The **Expected Date** is generated by independently interpreting the PM Event
record associated to a PM Schedule. We use the `python-dateutil
<https://dateutil.readthedocs.org/en/latest/rrule.html>`_ library to turn the
recurrence rules into a series of dates. All the dates are handled in a time-zone
aware manner. By default the time-zone is *US/Eastern*. Use the ``--timezone``
(``-z``) flag to change it to your locale. For USA, *US/Pacific*, *US/Mountain*
and *US/Central* are the common ones.

If your environment has mixed timezones and the time offsets are causing
issues, you can omit the time component by specifying the ``--strip-time``
(``-s``) flag. This way only the dates are compared.

We also apply *Working Calendar Rules* to the expected date. Working calendar
rules are predefined in Axiom. You can choose one using the
``--working-calendar`` (``-w``) flag. Allowed choices are ``8to5`` and
``24/7``. These calendars try to mimic common TRIRIGA calendar rules. *8to5*
will cause any dates before 8 AM local time to be changed to 8 AM. Any dates
after 5 PM will be changed to 8 AM the next day. Note that the Axiom calendar
does not handle the 1 hour lunch period present in TRIRIGA's ``DEFAULT``
calendar. You can only choose a single working calendar per invocation.

The ``8to5`` working calendar rules do not allow tasks to be scheduled on
weekends. The Planned Start Dates that fall on Saturdays or Sundays will be
changed to the following Monday at 8 AM. If you create a DAILY task, you may
notice duplicates because of this. Run Axiom with ``--debug`` and ``-v 2``
flags to see how the dates are changed by the working calendar rules. This
mimics TRIRIGA's behavior.

Use the ``24/7`` calendar to avoid any working calendar restrictions.

Known Issues
------------
* The starting datetime is not the first recurrence instance, unless it does
  fit in the specified rules. This may cause the Axiom generated dates to
  deviate from TRIRIGA generated ones.
* Axiom uses python-dateutil to generate dates. It implements the iCalendar
  specification. Read `the specification <https://www.ietf.org/rfc/rfc2445.txt>`_
  and `the implementation notes <https://labix.org/python-dateutil>`_ if you
  have questions about Axiom's behavior.
* Working calendar rules are applied after a date is generated from the
  recurrence rules. This could cause dates to duplicate. For example, a DAILY
  schedule will generate occurances for Sat and Sun. When the working calendar
  rules are applied, the Sat and Sun dates will be changed to the following
  Mon, resulting in 3 tasks for Monday. This is how TRIRIGA behaves with the
  DEFAULT 8 to 5 calendar.
* Axiom does not support shadowing.

Building Windows Installer
--------------------------
Windows installer can be built on Windows machines. You will need Python 3.4
(Windows version) and the ``pyinstaller`` package (version 2.0).

From the project root run::

    make installer

This will build the binaries and installer.

License
-------
.. code::

    Axiom. Verify TRIRIGA PM Schedules.
    Copyright (C) 2016 Nithin Philips

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
