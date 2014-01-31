import uuid
import math
import random
import datetime

from coda import util

"""
This is a utility script to populate a premis_event database with a bunch of
events for demonstration purposes
"""


def d100():
    """
    I wrote this function before realizing that the random.randint() function
    could do the same thing.
    Oh well.
    """
    return int(math.ceil(random.random() * 100))


def populate(
        webRoot, agentId, successRate, startDate, endDate, maxTimeGap,
        maxObjects=None, debug=False
):
    """
    Given a PREMIS Event service at webRoot, start to generate events with a
    success rate of successRate %.  Start dating events at startDate and set
    the next event's date at a random interval between 1 and maxTimeGap
    minutes.  Don't generate more than maxObjects 'objects'

    webRoot : This is the URL to the AtomPub endpoint for our event server
    agentId : This the identifier for the PREMIS agent that will be
    'generating' these events
    successRate : This is an integer from 0-100 that determines the success
    percentage for each step
    startDate : This is a Python datetime object to determine the starting
    date for the fake events
    endDate : This is a Python datetime object to describe the point at which
    we stop generating fake events
    maxTimeGap : This is an integer describing the maximum amount of minutes
    to place between generated dates for subsequent events
    maxObjects : If specified, this is the total maximum number of fake
    objects to run events on
    """

    objectCount = 0
    currentDate = startDate
    random.seed()
    while objectCount < maxObjects and currentDate < endDate:
        virusScan = False
        fixityCheck = False
        objectCopy = False
        objectIngest = False
        objectName = "object_" + uuid.uuid1().hex
        objectList = [(objectName, "local-id", None)]
        failOn = None
        if d100() <= successRate:
            virusScan = True
            outcome = "pass"
        else:
            outcome = "fail"
        util.sendPREMISEvent(
            webRoot=webRoot,
            eventType="virus_scan",
            agentIdentifier=agentId,
            eventDetail="Scanning %s for viruses" % objectName,
            eventOutcome=outcome,
            linkObjectList=objectList,
            eventDate=currentDate,
            debug=debug,
        )
        if virusScan:
            if d100() <= successRate:
                fixityCheck = True
                outcome = "pass"
            else:
                outcome = "fail"
                failOn = "Failed during fixity verification phase"
            util.sendPREMISEvent(
                webRoot=webRoot,
                eventType="fixity_check",
                agentIdentifier=agentId,
                eventDetail="Checking Fixity of %s" % objectName,
                eventOutcome=outcome,
                linkObjectList=objectList,
                eventDate=currentDate,
                debug=debug,
            )
        if fixityCheck:
            if d100() <= successRate:
                objectCopy = True
                outcome = "pass"
            else:
                outcome = "fail"
                failOn = "Failed during file replication phase"

            util.sendPREMISEvent(
                webRoot=webRoot,
                eventType="object_copy",
                agentIdentifier=agentId,
                eventDetail="Copying %s to remote location" % objectName,
                eventOutcome=outcome,
                linkObjectList=objectList,
                eventDate=currentDate,
                debug=debug,
            )
        if objectCopy:
            objectIngest = True
            outcome = "pass"
        else:
            outcome = "fail"
        util.sendPREMISEvent(
            webRoot=webRoot,
            eventType="object_ingest",
            agentIdentifier=agentId,
            eventDetail="Ingesting object %s into our system" % objectName,
            eventOutcome=outcome,
            linkObjectList=objectList,
            eventOutcomeDetail=failOn,
            eventDate=currentDate,
            debug=debug,
        )
        delta = datetime.timedelta(minutes=random.randint(1, maxTimeGap))
        currentDate = currentDate + delta
        objectCount = objectCount + 1
