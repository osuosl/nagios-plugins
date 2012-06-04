#! /usr/bin/env python

# Bacula Check for Nagios
#
# Author: Trevor Bramwell
# Date: Fri May  4 11:34:32 PDT 2012
#
import sys

from datetime import datetime, timedelta

from optparse import make_option
from pynagios import Plugin

# Some day I will punch someone in the face for using this
#  CamelCase in python
import MySQLdb as mysqldb

# Set the DB for the checks to run on
DB = 'bacula'


class BaculaCheck(Plugin):
    """
    Nagios plugin to check if bacula is running on host.
    """
    hours = make_option("--hours", type="int",
        dest="hours",
        help="limit check to within last HOURS")
    job = make_option("-j", "--job", dest="job",
        help="bacula job to check")
    user = make_option("-u", "--username",
        dest="username",
        help="database user")
    passwd = make_option("-p", "--password",
        dest="password",
        help="database password")
    port = make_option("-P", "--port",
        dest="port",
        type="int",
        help="database port")

    def check(self):
        """
        Nagios check main function
        """
        self.options.host = self.options.hostname
        opts = self.options

        if opts.verbosity > 2:
            print opts

        # Grab only hostname, username, password and port.
        conn_fields = dict((k, v) for (k, v) in vars(opts).items()
            if v is not None and k in ('host', 'user', 'passwd', 'port'))

        # Calculate how far back (in hours) to check, if passed
        #  default to begining of epoch
        starttime = datetime.now()
        endtime = datetime.fromtimestamp(0)

        if opts.hours:
            endtime = starttime - timedelta(hours=opts.hours)

        # Format string: MySQL only takes YYYY-MM-DD HH:MM:SS strings,
        #  but datetime includes microseconds. This removes microseconds.
        fstr = "%Y-%m-%d %X"
        starttime = starttime.strftime(fstr)
        endtime = endtime.strftime(fstr)

        if opts.verbosity > 2:
            print conn_fields

        # Create db connection
        try:
            conn = mysqldb.connect(db=DB, **conn_fields)
        except mysqldb.Error, e:
            print (e.args[0], e.args[1])
            sys.exit(1)

        cursor = conn.cursor()

        if hasattr(opts, 'job'):
            cursor.execute(
                """
                SELECT count(*) as 'count'
                from Job
                where (Name='%s') and
                (JobStatus='T') and (
                    (EndTime <= '%s') and (EndTime >= '%s')
                )
                """ % (opts.job, starttime, endtime)
            )

            # Get job count
            jobs = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        #return Response(pynagios.OK, "Everything is ok!")
        return self.response_for_value(jobs,
            "Found %s successful Bacula jobs for %s" % (jobs, opts.job))

if __name__ == "__main__":
    # Build and Run the Nagios Plugin
    BaculaCheck().check().exit()
