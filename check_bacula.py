#! /usr/bin/env python

# Copyright 2012 Oregon State University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Bacula Checks for Nagios
#
from optparse import make_option
from pynagios import Plugin, Response, CRITICAL

# Some day I will punch someone in the face for using this
#  CamelCase in python
import MySQLdb as mysqldb


class BaculaCheck(Plugin):
    """
    Nagios plugin to check if bacula is running on host.
    """
    database = make_option("-d", "--database",
        dest="database",
        type="string",
        default="bacula",
        help="bacula database title (default: 'bacula')",)
    hours = make_option("--hours", type="int",
        dest="hours",
        default="72",
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

        if opts.verbosity > 2:
            print conn_fields

        # Create db connection
        try:
            conn = mysqldb.connect(db=opts.database, **conn_fields)
        except mysqldb.Error, err:
            return Response(CRITICAL, err.args[1])

        # Create a cursor, given the db connection succeeded
        cursor = conn.cursor()

        if hasattr(opts, 'job') and opts.job is not None:
            status = self.check_single_job(cursor, opts)

            return self.response_for_value(status,
                "Found %s successful Bacula jobs for %s" % (status, opts.job))
        else:
            return Response(CRITICAL, "No job provided to script")

        cursor.close()
        conn.close()


    def check_single_job(self, cursor, opts):
        """
        Given a single job, get a count of it's status in the last given hours
        """
        cursor.execute(
            """
            SELECT COUNT(*) as 'count'
            FROM Job
            WHERE (Name='%(job)s') AND (JobStatus='T')
              AND (EndTime <= NOW() AND
                 EndTime >= SUBDATE(NOW(), INTERVAL %(hours)s HOUR))
            """ % (vars(opts))
        )

        # Get and return job count
        status = cursor.fetchone()[0]
        return status

if __name__ == "__main__":
    # Build and Run the Nagios Plugin
    BaculaCheck().check().exit()
