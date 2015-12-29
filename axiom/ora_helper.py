#!/usr/bin/env python3

import cx_Oracle
import re
import logging


def get_connection(tns_name, uname, upass):
    connection = cx_Oracle.connect(uname, upass, tns_name)
    connection.autocommit = True
    return connection

def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]

def execute(sql_statement, connection, parameters=None):
    """
    Executes a SQL statement and returns all results.
    """

    cursor = connection.cursor()
    if parameters:
        cursor = cursor.execute(sql_statement, parameters)
    else:
        cursor = cursor.execute(sql_statement)

    result = rows_to_dict_list(cursor)
    return result

class JdbcConnection:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __str__(self):
        if self.sid:
            return "{}/{}@{}:{}:{}".format(self.username, self.password, self.host, self.port, self.sid)
        else:
            return "{}/{}@{}:{}/{}".format(self.username, self.password, self.host, self.port, self.service_name)

    def get_tns(self):
        if self.sid:
            return "(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST={})(PORT={})))(CONNECT_DATA=(SID={})))".format(self.host, self.port, self.sid)
        else:
            return "(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST={})(PORT={})))(CONNECT_DATA=(SERVICE_NAME={})))".format(self.host, self.port, self.service_name)

    def get_connection(self):
        return get_connection(self.get_tns(), self.username, self.password)

def parse_db_url(url):
    """
    Parses a JDBC Connection URL.

    It can handle URLs like

        USER/PASSWORD@LCONORA-CLUSTER:1533/DELLPROD

    or

        USER/PASSWORD@delldbtest:1521:dellpreprod

    return an object with the following attributes:

        host
        port
        sid
        service_name

    Only one of sid or service_name will be filled. The other will be None.
    """

    logging.debug("Parsing JDBC url: {}".format(url))

    if url is None:
        url = ""

    host = None
    port = None
    sid = None
    service_name = None
    db_type = "Oracle"
    database = None

    sid_pattern = re.compile(r'(?:([^/]*)/([^@]*)@)?([^:]*):(\d*):(.*)')
    sn_pattern = re.compile(r'(?:([^/]*)/([^@]*)@)?([^:]*):(\d*)/(.*)')

    sid_result = sid_pattern.findall(url)
    if sid_result:
        logging.debug("URL matches SID variant.")
        (username, password, host, port, sid) = sid_result[0]

    sn_result = sn_pattern.findall(url)
    if sn_result:
        logging.debug("URL matches Service Name variant.")
        (username, password, host, port, service_name) = sn_result[0]

    if host:
        return JdbcConnection(host=host,
                              port=port,
                              sid=sid,
                              username=username,
                              password=password,
                              service_name=service_name,
                              type=db_type,
                              database=database)
    else:
        return None

