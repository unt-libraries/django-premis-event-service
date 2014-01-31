import json
from lxml import etree
import uuid
import datetime
import bagatom
import httplib2
import urllib2
import urlparse
import sys
import tempfile
import os
import time
import subprocess

from premis_event_service import settings

#not really thrilled about duplicating these globals here -- maybe define them in coda.bagatom?
PREMIS_NAMESPACE = "http://www.loc.gov/standards/premis/v1"
PREMIS = "{%s}" % PREMIS_NAMESPACE
PREMIS_NSMAP = {"premis": PREMIS_NAMESPACE}
dateFormat = "%Y-%m-%d %H:%M:%S"
svn_version_path = "/usr/bin/svnversion"


def parseVocabularySources(jsonFilePath):
    choiceList = []
    jsonString = open(jsonFilePath, "r").read()
    jsonDict = json.loads(jsonString)
    terms = jsonDict["terms"]
    for term in terms:
        choiceList.append((term['name'], term['label']))
    return choiceList


class HEADREQUEST(urllib2.Request):
    def get_method(self):
        return "HEAD"


class PUTREQUEST(urllib2.Request):
    def get_method(self):
        return "PUT"


class DELETEREQUEST(urllib2.Request):
    def get_method(self):
        return "DELETE"


def waitForURL(url, max_seconds=None):
    """
    Give it a URL.  Keep trying to get a HEAD request from it until it works.
    If it doesn't work, wait a while and try again
    """

    startTime = datetime.datetime.now()
    while True:
        #loop for-evah!
        #httpCon = httplib2.Http()
        response = None
        info = None
        try:
            #response,content = httpCon.request(url, "HEAD")
            response = urllib2.urlopen(HEADREQUEST(url))
        except urllib2.URLError, u:
            pass
        #if response != None and response["status"] == "200":
        if response != None and isinstance(response, urllib2.addinfourl):
            info = response.info()
            if response.getcode() == 200:
                #we're done, yay!
                return
        timeNow = datetime.datetime.now()
        timePassed = timeNow - startTime
        if max_seconds and max_seconds < timePassed.seconds:
            return
        print("Waiting on URL %s for %s so far" % (url, timePassed))
        time.sleep(30)


def doWaitWebRequest(url, method="GET", data=None, headers={}):
    """
    Same as doWebRequest, but with built in wait-looping
    """

    completed = False
    while completed == False:
        completed = True
        try:
            response, content = doWebRequest(url, method, data, headers)
        except urllib2.URLError, u:
            completed = False
            waitForURL(url)
    return response, content


def doWebRequest(url, method="GET", data=None, headers={}):
    """
    A urllib2 wrapper to mimic the functionality of http2lib, but with timeout support
    """

    # initialize variables
    response = None
    info = None
    content = None
    # find condition that matches request
    if method == "HEAD":
        request = HEADREQUEST(url, data=data, headers=headers)
    elif method == "PUT":
        request = PUTREQUEST(url, data=data, headers=headers)
    elif method == "DELETE":
        request = DELETEREQUEST(url, headers=headers)
    elif method == "GET":
        request = urllib2.Request(url, headers=headers)
    # POST?
    else:
        request = urllib2.Request(url, data=data, headers=headers)
    response = urllib2.urlopen(request)
    if response:
        content = response.read()
        info = response.info()
    return response, content


def sendPREMISEvent(webRoot, eventType, agentIdentifier, eventDetail,
                    eventOutcome, eventOutcomeDetail=None, linkObjectList=[],
                    eventDate=None, debug=False, eventIdentifier=None):
    """
    A function to format an event to be uploaded and send it to a particular CODA server
    in order to register it
    """

    atomID = uuid.uuid1().hex
    eventXML = createPREMISEventXML(
        eventType=eventType,
        agentIdentifier=agentIdentifier,
        eventDetail=eventDetail,
        eventOutcome=eventOutcome,
        outcomeDetail=eventOutcomeDetail,
        eventIdentifier=eventIdentifier,
        eventDate=eventDate,
        linkObjectList=linkObjectList
    )
    atomXML = bagatom.wrapAtom(eventXML, id=atomID, title=atomID)
    atomXMLText = '<?xml version="1.0"?>\n%s' % etree.tostring(
        atomXML, pretty_print=True
    )
    if debug:
        print "Uploading XML to %s\n---\n%s\n---\n" % (webRoot, atomXMLText)
    response = None
    try:
        response, content = doWebRequest(webRoot, "POST", data=atomXMLText)
    except urllib2.URLError, u:
        pass
    if not response:
        waitForURL(webRoot, 60)
        response, content = doWebRequest(webRoot, "POST", data=atomXMLText)
    if response.code != 201:
        if debug:
            tempdir = tempfile.gettempdir()
            tfPath = os.path.join(
                tempdir, "premis_upload_%s.html" % uuid.uuid1().hex
            )
            tf = open(tfPath, "w")
            tf.write(content)
            tf.close()
            sys.stderr.write(
                "Output from webserver available at %s. Response code %s" % (
                    tf.name, response.code
                )
            )
        raise Exception(
            "Error uploading PREMIS Event to %s. Response code is %s" % (
                webRoot, response.code
            )
        )
    return (response, content)


def createPREMISEventXML(eventType, agentIdentifier, eventDetail, eventOutcome,
                         outcomeDetail=None, eventIdentifier=None,
                         linkObjectList=[], eventDate=None):
    """
    Actually create our PREMIS Event XML
    """

    eventXML = etree.Element(PREMIS + "event", nsmap=PREMIS_NSMAP)
    eventTypeXML = etree.SubElement(eventXML, PREMIS + "eventType")
    eventTypeXML.text = eventType
    eventIDXML = etree.SubElement(eventXML, PREMIS + "eventIdentifier")
    eventIDTypeXML = etree.SubElement(
        eventIDXML, PREMIS + "eventIdentifierType"
    )
    eventIDTypeXML.text = settings.EVENT_ID_TYPE_XML
    eventIDValueXML = etree.SubElement(
        eventIDXML, PREMIS + "eventIdentifierValue"
    )
    if eventIdentifier:
        eventIDValueXML.text = eventIdentifier
    else:
        eventIDValueXML.text = uuid.uuid4().hex
    eventDateTimeXML = etree.SubElement(eventXML, PREMIS + "eventDateTime")
    if eventDate == None:
        eventDateTimeXML.text = datetime.datetime.now().strftime(dateFormat)
    else:
        eventDateTimeXML.text = eventDate.strftime(dateFormat)
    eventDetailXML = etree.SubElement(eventXML, PREMIS + "eventDetail")
    eventDetailXML.text = eventDetail
    eventOutcomeInfoXML = etree.SubElement(
        eventXML, PREMIS + "eventOutcomeInformation"
    )
    eventOutcomeXML = etree.SubElement(
        eventOutcomeInfoXML, PREMIS + "eventOutcome"
    )
    eventOutcomeXML.text = eventOutcome
    if outcomeDetail:
        eventOutcomeDetailXML = etree.SubElement(
            eventOutcomeInfoXML, PREMIS + "eventOutcomeDetail"
        )
        eventOutcomeDetailXML.text = outcomeDetail
        #assuming it's a list of 3-item tuples here [ ( identifier, type, role) ]
    for linkObject in linkObjectList:
        linkObjectIDXML = etree.SubElement(
            eventXML, PREMIS + "linkingObjectIdentifier"
        )
        linkObjectIDTypeXML = etree.SubElement(
            linkObjectIDXML, PREMIS + "linkingObjectIdentifierType"
        )
        linkObjectIDTypeXML.text = linkObject[1]
        linkObjectIDValueXML = etree.SubElement(
            linkObjectIDXML, PREMIS + "linkingObjectIdentifierValue"
        )
        linkObjectIDValueXML.text = linkObject[0]
        if linkObject[2]:
            linkObjectRoleXML = etree.SubElement(
                linkObjectIDXML, PREMIS + "linkingObjectRole"
            )
            linkObjectRoleXML.text = linkObject[2]
    linkAgentIDXML = etree.SubElement(
        eventXML, PREMIS + "linkingAgentIdentifier"
    )
    linkAgentIDTypeXML = etree.SubElement(
        linkAgentIDXML, PREMIS + "linkingAgentIdentifierType"
        )
    linkAgentIDTypeXML.text = settings.LINK_AGENT_ID_TYPE_XML
    linkAgentIDValueXML = etree.SubElement(
        linkAgentIDXML, PREMIS + "linkingAgentIdentifierValue"
    )
    linkAgentIDValueXML.text = agentIdentifier
    linkAgentIDRoleXML = etree.SubElement(
        linkAgentIDXML, PREMIS + "linkingAgentIdentifierRole"
    )
    linkAgentIDRoleXML.text = settings.LINK_AGENT_ID_ROLE_XML
    return eventXML


def get_svn_revision(path=None):

    if not path:
        path = os.path.dirname(sys.argv[0])
    path = os.path.abspath(path)
    exec_list = [svn_version_path, path]
    proc = subprocess.Popen(exec_list, stdout=subprocess.PIPE)
    out, errs = proc.communicate()
    return out.strip()


def deleteQueue(destinationRoot, queueArk, debug=False):
    """
    Delete an entry from the queue
    """

    url = urlparse.urljoin(destinationRoot, "APP/queue/" + queueArk + "/")
    response, content = doWaitWebRequest(url, "DELETE")
    if response.getcode() != 200:
        raise Exception(
            "Error updating queue %s to url %s.  Response code is %s\n%s" % \
            (queueArk, url, response.getcode(), content)
        )


def updateQueue(destinationRoot, queueDict, debug=False):
    """
    With a dictionary that represents a queue entry, update the queue entry with
    the values
    """

    attrDict = bagatom.AttrDict(queueDict)
    url = urlparse.urljoin(destinationRoot, "APP/queue/" + attrDict.ark + "/")
    queueXML = bagatom.queueEntryToXML(attrDict)
    urlID = os.path.join(destinationRoot, attrDict.ark)
    uploadXML = bagatom.wrapAtom(queueXML, id=urlID, title=attrDict.ark)
    uploadXMLText = '<?xml version="1.0"?>\n' + etree.tostring(
        uploadXML, pretty_print=True
    )
    if debug:
        print "Sending XML to %s" % url
        print uploadXMLText
    try:
        response, content = doWebRequest(url, "PUT", data=uploadXMLText)
    except:
        # sleep a few minutes then give it a second shot before dying
        time.sleep(300)
        response, content = doWebRequest(url, "PUT", data=uploadXMLText) 
    if response.getcode() != 200:
        raise Exception(
            "Error updating queue %s to url %s.  Response code is %s\n%s" % \
            (attrDict.ark, url, response.getcode(), content)
        )
