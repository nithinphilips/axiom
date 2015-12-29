SQL_GET_PMSCHEDS = """
SELECT
    SCHED.TRIIDTX,
    SCHED.SPEC_ID,
    SCHED.TRINAMETX,
    SCHED.TRIREQUESTCLASSTX,
    SCHED.TRIPMSCHEDULETYPELI,
    SCHED.TRIPMTYPECLASSCL
FROM
    T_TRIPMSCHEDULE SCHED
WHERE SCHED.TRISTATUSCL IN ('Active', 'Processing')
ORDER BY
    SCHED.TRIIDTX
"""

SQL_GET_TASKS = """
SELECT
    SCHED.TRINAMETX,
    SCHED.TRIREQUESTCLASSTX,
    SCHED.TRIPMSCHEDULETYPELI,
    SCHED.TRIPMTYPECLASSCL,
    TO_DATE('1970-01-01', 'YYYY-MM-DD') + TASK.TRIPLANNEDSTARTDT / 86400000 as TRIPLANNEDSTARTDT,
    TASK.TRINAMETX AS TASK_NAME,
    TASK.TRIIDTX AS TASK_ID,
    TASK.TRISTATUSCL AS TASK_STATUS
FROM
    T_TRIPMSCHEDULE SCHED
LEFT OUTER JOIN IBS_SPEC_ASSIGNMENTS ASSN
ON
    SCHED.SPEC_ID = ASSN.SPEC_ID
AND
    ASSN.ASS_TYPE = 'Schedule For'
AND
    ASSN.ASS_SPEC_TEMPLATE_ID = 10008284
LEFT OUTER JOIN T_TRIWORKTASK TASK
ON
    TASK.SPEC_ID = ASSN.ASS_SPEC_ID
WHERE SCHED.TRIIDTX = :pm_id
ORDER BY
    TASK.TRIPLANNEDSTARTDT"""


SQL_GET_EVENT = """
SELECT
    SCHED.TRIIDTX AS PM_ID,
    SCHED.TRINAMETX AS PM_NAME,
    EVENT.WEEKLYWEDNESDAY WEEKLYWEDNESDAY,
    EVENT.WEEKLYTUESDAY WEEKLYTUESDAY,
    EVENT.WEEKLYTHURSDAY WEEKLYTHURSDAY,
    EVENT.WEEKLYSUNDAY WEEKLYSUNDAY,
    EVENT.WEEKLYSATURDAY WEEKLYSATURDAY,
    EVENT.WEEKLYREGENERATETASK WEEKLYREGENERATETASK,
    EVENT.WEEKLYRECURRENCEWEEKS WEEKLYRECURRENCEWEEKS,
    EVENT.WEEKLYMONDAY WEEKLYMONDAY,
    EVENT.WEEKLYFRIDAY WEEKLYFRIDAY,
    EVENT.STATUS STATUS,
    EVENT.RECURRENCESTARTDATE RECURRENCESTARTDATE,
    EVENT.RECURRENCEPATTERNTYPE RECURRENCEPATTERNTYPE,
    EVENT.RECURRENCEID2 RECURRENCEID2,
    EVENT.NOOFOCCURRENCESBEFOR NOOFOCCURRENCESBEFOR,
    EVENT.NOENDDATE NOENDDATE,
    EVENT.NAME1 NAME1,
    EVENT.MONTHLYWEEKOFMONTH MONTHLYWEEKOFMONTH,
    EVENT.MONTHLYREGENERATETAS MONTHLYREGENERATETAS,
    EVENT.MONTHLYRECURRENCEMON MONTHLYRECURRENCEMON,
    EVENT.MONTHLYDAYOFWEEK MONTHLYDAYOFWEEK,
    EVENT.MONTHLYDAYOFMONTH MONTHLYDAYOFMONTH,
    EVENT.ENDDATE ENDDATE,
    EVENT.TRIUSERMESSAGETX TRIUSERMESSAGETX,
    EVENT.TRIUSERMESSAGEFLAGTX TRIUSERMESSAGEFLAGTX,
    EVENT.TRIADVANCEDBL TRIADVANCEDBL,
    EVENT.TRICAPACITYNU TRICAPACITYNU,
    EVENT.TRIBUILDINGTX TRIBUILDINGTX,
    EVENT.TRIRECURRENCEYEARLYO TRIRECURRENCEYEARLYO,
    EVENT.TRIRECURRENCEWEEKLYO TRIRECURRENCEWEEKLYO,
    EVENT.TRIRECURRENCEMONTHLY TRIRECURRENCEMONTHLY,
    EVENT.TRIRECURRENCEENDOPTI TRIRECURRENCEENDOPTI,
    EVENT.TRIRECURRENCEDAILYOP TRIRECURRENCEDAILYOP,
    EVENT.TRIREQUESTEDFORTX TRIREQUESTEDFORTX,
    EVENT.TRIREQUESTEDFORTXOBJID TRIREQUESTEDFORTXOBJID,
    EVENT.TRILANGUAGELI TRILANGUAGELI,
    EVENT.TRIOFFSETDATEDURATIO TRIOFFSETDATEDURATIO,
    EVENT.TRIMAYBL TRIMAYBL,
    EVENT.TRIFEBRUARYBL TRIFEBRUARYBL,
    EVENT.TRIDECEMBERBL TRIDECEMBERBL,
    EVENT.TRIOCTOBERBL TRIOCTOBERBL,
    EVENT.TRIJULYBL TRIJULYBL,
    EVENT.TRIAUGUSTBL TRIAUGUSTBL,
    EVENT.TRISEPTEMBERBL TRISEPTEMBERBL,
    EVENT.TRIJUNEBL TRIJUNEBL,
    EVENT.TRIAPRILBL TRIAPRILBL,
    EVENT.TRINOVEMBERBL TRINOVEMBERBL,
    EVENT.TRIMARCHBL TRIMARCHBL,
    EVENT.TRIJANUARYBL TRIJANUARYBL,
    EVENT.TRIEXCLUDEMONTHSLA TRIEXCLUDEMONTHSLA,
    EVENT.SUBJECT SUBJECT,
    EVENT.NOTES NOTES,
    EVENT.RECURRENCEID RECURRENCEID,
    EVENT.EVENTREFID EVENTREFID,
    EVENT.EVENTTYPE EVENTTYPE,
    TO_DATE('1970-01-01', 'YYYY-MM-DD') + EVENT.EVENTSTARTDATE / 86400000 as EVENTSTARTDATE,
    TO_DATE('1970-01-01', 'YYYY-MM-DD') + EVENT.EVENTENDDATE / 86400000 as EVENTENDDATE,
    EVENT.EVENTINSTRUCTION EVENTINSTRUCTION,
    EVENT.EVENTDURATION EVENTDURATION,
    EVENT.DAILYREGENERATETASKD DAILYREGENERATETASKD,
    EVENT.DAILYRECURWEEKENDDAY DAILYRECURWEEKENDDAY,
    EVENT.DAILYRECURWEEKDAY DAILYRECURWEEKDAY,
    EVENT.DAILYRECURRENCEDAYS DAILYRECURRENCEDAYS,
    EVENT.YEARLYWEEKOFMONTH YEARLYWEEKOFMONTH,
    EVENT.YEARLYREGENERATETASK YEARLYREGENERATETASK,
    EVENT.YEARLYMONTH YEARLYMONTH,
    EVENT.YEARLYDAYOFWEEK YEARLYDAYOFWEEK,
    EVENT.YEARLYDAYOFMONTH YEARLYDAYOFMONTH
FROM
    T_PMEVENT EVENT
LEFT OUTER JOIN IBS_SPEC_ASSIGNMENTS ASSN1
ON
    EVENT.SPEC_ID = ASSN1.SPEC_ID
AND
    ASSN1.ASS_TYPE = 'Event For'
LEFT OUTER JOIN T_TRIPMSCHEDULE SCHED
ON
    SCHED.SPEC_ID = ASSN1.ASS_SPEC_ID
WHERE
    SCHED.TRIIDTX = :pm_id
"""

SQL_GET_EVENTS = """
SELECT
    SCHED.TRIIDTX AS PM_ID,
    SCHED.TRINAMETX AS PM_NAME,
    EVENT.WEEKLYWEDNESDAY WEEKLYWEDNESDAY,
    EVENT.WEEKLYTUESDAY WEEKLYTUESDAY,
    EVENT.WEEKLYTHURSDAY WEEKLYTHURSDAY,
    EVENT.WEEKLYSUNDAY WEEKLYSUNDAY,
    EVENT.WEEKLYSATURDAY WEEKLYSATURDAY,
    EVENT.WEEKLYREGENERATETASK WEEKLYREGENERATETASK,
    EVENT.WEEKLYRECURRENCEWEEKS WEEKLYRECURRENCEWEEKS,
    EVENT.WEEKLYMONDAY WEEKLYMONDAY,
    EVENT.WEEKLYFRIDAY WEEKLYFRIDAY,
    EVENT.STATUS STATUS,
    EVENT.RECURRENCESTARTDATE RECURRENCESTARTDATE,
    EVENT.RECURRENCEPATTERNTYPE RECURRENCEPATTERNTYPE,
    EVENT.RECURRENCEID2 RECURRENCEID2,
    EVENT.NOOFOCCURRENCESBEFOR NOOFOCCURRENCESBEFOR,
    EVENT.NOENDDATE NOENDDATE,
    EVENT.NAME1 NAME1,
    EVENT.MONTHLYWEEKOFMONTH MONTHLYWEEKOFMONTH,
    EVENT.MONTHLYREGENERATETAS MONTHLYREGENERATETAS,
    EVENT.MONTHLYRECURRENCEMON MONTHLYRECURRENCEMON,
    EVENT.MONTHLYDAYOFWEEK MONTHLYDAYOFWEEK,
    EVENT.MONTHLYDAYOFMONTH MONTHLYDAYOFMONTH,
    EVENT.ENDDATE ENDDATE,
    EVENT.TRIUSERMESSAGETX TRIUSERMESSAGETX,
    EVENT.TRIUSERMESSAGEFLAGTX TRIUSERMESSAGEFLAGTX,
    EVENT.TRIADVANCEDBL TRIADVANCEDBL,
    EVENT.TRICAPACITYNU TRICAPACITYNU,
    EVENT.TRIBUILDINGTX TRIBUILDINGTX,
    EVENT.TRIRECURRENCEYEARLYO TRIRECURRENCEYEARLYO,
    EVENT.TRIRECURRENCEWEEKLYO TRIRECURRENCEWEEKLYO,
    EVENT.TRIRECURRENCEMONTHLY TRIRECURRENCEMONTHLY,
    EVENT.TRIRECURRENCEENDOPTI TRIRECURRENCEENDOPTI,
    EVENT.TRIRECURRENCEDAILYOP TRIRECURRENCEDAILYOP,
    EVENT.TRIREQUESTEDFORTX TRIREQUESTEDFORTX,
    EVENT.TRIREQUESTEDFORTXOBJID TRIREQUESTEDFORTXOBJID,
    EVENT.TRILANGUAGELI TRILANGUAGELI,
    EVENT.TRIOFFSETDATEDURATIO TRIOFFSETDATEDURATIO,
    EVENT.TRIMAYBL TRIMAYBL,
    EVENT.TRIFEBRUARYBL TRIFEBRUARYBL,
    EVENT.TRIDECEMBERBL TRIDECEMBERBL,
    EVENT.TRIOCTOBERBL TRIOCTOBERBL,
    EVENT.TRIJULYBL TRIJULYBL,
    EVENT.TRIAUGUSTBL TRIAUGUSTBL,
    EVENT.TRISEPTEMBERBL TRISEPTEMBERBL,
    EVENT.TRIJUNEBL TRIJUNEBL,
    EVENT.TRIAPRILBL TRIAPRILBL,
    EVENT.TRINOVEMBERBL TRINOVEMBERBL,
    EVENT.TRIMARCHBL TRIMARCHBL,
    EVENT.TRIJANUARYBL TRIJANUARYBL,
    EVENT.TRIEXCLUDEMONTHSLA TRIEXCLUDEMONTHSLA,
    EVENT.SUBJECT SUBJECT,
    EVENT.NOTES NOTES,
    EVENT.RECURRENCEID RECURRENCEID,
    EVENT.EVENTREFID EVENTREFID,
    EVENT.EVENTTYPE EVENTTYPE,
    TO_DATE('1970-01-01', 'YYYY-MM-DD') + EVENT.EVENTSTARTDATE / 86400000 as EVENTSTARTDATE,
    TO_DATE('1970-01-01', 'YYYY-MM-DD') + EVENT.EVENTENDDATE / 86400000 as EVENTENDDATE,
    EVENT.EVENTINSTRUCTION EVENTINSTRUCTION,
    EVENT.EVENTDURATION EVENTDURATION,
    EVENT.DAILYREGENERATETASKD DAILYREGENERATETASKD,
    EVENT.DAILYRECURWEEKENDDAY DAILYRECURWEEKENDDAY,
    EVENT.DAILYRECURWEEKDAY DAILYRECURWEEKDAY,
    EVENT.DAILYRECURRENCEDAYS DAILYRECURRENCEDAYS,
    EVENT.YEARLYWEEKOFMONTH YEARLYWEEKOFMONTH,
    EVENT.YEARLYREGENERATETASK YEARLYREGENERATETASK,
    EVENT.YEARLYMONTH YEARLYMONTH,
    EVENT.YEARLYDAYOFWEEK YEARLYDAYOFWEEK,
    EVENT.YEARLYDAYOFMONTH YEARLYDAYOFMONTH
FROM
    T_PMEVENT EVENT
LEFT OUTER JOIN IBS_SPEC_ASSIGNMENTS ASSN1
ON
    EVENT.SPEC_ID = ASSN1.SPEC_ID
AND
    ASSN1.ASS_TYPE = 'Event For'
LEFT OUTER JOIN T_TRIPMSCHEDULE SCHED
ON
    SCHED.SPEC_ID = ASSN1.ASS_SPEC_ID
"""

