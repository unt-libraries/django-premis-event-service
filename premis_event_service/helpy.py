# this script will read through a file specified as the first sys.argv
# and then create an Event object
# then, call sendPREMISEvent from util.py which creates an xml object
# that then, POSTs the string representation of the xml to collection
# if we get back anything except 201 status code, it will say failure

import csv
import os
import re
import sys
import uuid
from datetime import datetime
from coda.util import sendPREMISEvent

class Event(object):
    __slots__ = ("event_identifier event_identifier_type event_type "
                 "event_date_time event_added event_detail event_outcome "
                 "event_outcome_detail linking_agent_identifier_type "
                 "linking_agent_identifier_value linking_agent_role "
                 "event_id object_identifier object_type").split()

    def __init__(self, dbid, event_identifier, event_identifier_type,
                 event_type, event_date_time, event_added, event_detail,
                 event_outcome, event_outcome_detail,
                 linking_agent_identifier_type, linking_agent_identifier_value,
                 linking_agent_role, event_db_id, event_id, linkobject_id,
                 link_object_db_id, object_identifier, object_type,
                 object_role):
        self.event_identifier = event_identifier
        self.event_identifier_type = event_identifier_type
        self.event_type = event_type
        self.event_date_time = event_date_time
        self.event_added = event_added
        self.event_detail = event_detail
        self.event_outcome = event_outcome
        self.event_outcome_detail = event_outcome_detail
        self.linking_agent_identifier_type = linking_agent_identifier_type
        self.linking_agent_identifier_value = linking_agent_identifier_value
        self.linking_agent_role = linking_agent_role
        self.event_id = event_id
        self.object_identifier = object_identifier
        self.object_type = object_type


def read_events(infile, outfile):
    print 'using ' + infile
    badrow = []
    for row in csv.reader(open(infile, "r"), delimiter=';'):
        if len(row) == 19:
            # this is a good row, yield it
            row[4] = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
            row[5] = datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S')
            yield Event(*row)
        else:
            # this is a bad row, extend on to badrow list
            badrow.extend(row)
            # if we have built a full row
            if badrow[-1] == "NULL":
                # check that the second row is a valid UUID
                try:
                    uuid.UUID(badrow[1])
                except ValueError as e:
                    print 'trying to use badrow w/o event_identifier:', e
                    outfile.write(';'.join(badrow))
                    badrow = []
                else:
                    if len(badrow) > 19:
                        # merge the badly split event_outcome_detail
                        badrow[8:-10] = ['\n'.join(badrow[8:-10])]
                    # row looks valid now, submit event
                    row = badrow
                    badrow = []
                    row[4] = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
                    row[5] = datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S')
                    yield Event(*row)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print 'usage: python helpy.py <infile> <event collection>'
    else:
        infile = sys.argv[1]
        # let's write failed rows to user's home directory
        failname = os.path.join(os.path.expanduser("~"), 'fail.txt')
        outfile = open(failname, 'w')
        premisRoot = sys.argv[2]
        for event in read_events(infile, outfile):
            sendPREMISEvent(
                webRoot=premisRoot,
                eventType=event.event_type,
                agentIdentifier=event.linking_agent_identifier_value,
                eventDetail=event.event_detail,
                eventOutcome=event.event_outcome,
                eventOutcomeDetail=event.event_outcome_detail,
                linkObjectList=[
                    (
                        event.object_identifier,
                        event.object_type,
                        '',
                    ),
                ],
                eventDate=event.event_date_time,
                debug=False,
                eventIdentifier=event.event_identifier,
            )
            print 'added event %s' % event.event_identifier
        outfile.close()
        print "any failed rows were written to %s" % (failname)
