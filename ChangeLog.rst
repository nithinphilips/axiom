Change Log
==========
Axiom Change Log

Version 0.2.1
-------------
* FIX: cx_Oracle.InterfaceError: Unable to acquire Oracle environment handle.
  The oracle library is now embedded in the axiom.exe executable.

Version 0.2.0
-------------
* Support for skipping months in MONTHLY schedules
* Support for Ad-hoc schedules.
* Support for *Also Schedule On* dates.
* Support for *Exclude Dates*.
* Users can now specify a list of PMs to report on. Leave blank to report on all PMs.
* Axiom will check associated service plan and automatically group tasks by
  planned start date when the grouping rule is *Create Task For Each
  Asset/Location*. When tasks are grouped the aggregate task *count* is displayed
  in the details table instead of the task ID.
* Add a new column to the details table that compares only the date portion.
* FIX: Resolve issues with timezone being wrong when date is changed by working
  calendar to fall IN or OUT of a DST period.
* FIX: The first task was overwritten by table header.
* FIX: When expected occurrences ended before tasks, an exception was thrown.
  Now Axiom will use a dummy date (Jan 1, 1970) and show all tasks.
* FIX: Do not display error when a PM schedule has no tasks.

Version 0.1.0
-------------
* First release
