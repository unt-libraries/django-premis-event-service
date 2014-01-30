from datetime import datetime
from coda.bagatom import getValueByName, getNodeByName, getNodesByName
from .models import Event, Agent, LinkObject, AGENT_TYPE_CHOICES
from django.shortcuts import get_object_or_404
from lxml import etree
from django.contrib.sites.models import Site
import uuid

from . import settings

PREMIS_NAMESPACE = "info:lc/xmlns/premis-v2"
PREMIS = "{%s}" % PREMIS_NAMESPACE
PREMIS_NSMAP = {"premis": PREMIS_NAMESPACE}
dateFormat = "%Y-%m-%d %H:%M:%S"
altDateFormat = "%Y-%m-%dT%H:%M:%S"

translateDict = {
    "event_identifier": ["eventIdentifier", "eventIdentifierValue"],
    "event_identifier_type": ["eventIdentifier", "eventIdentifierType"],
    "event_type": ["eventType"],
    "event_date_time": ["eventDateTime"],
    "event_detail": ["eventDetail"],
    "event_outcome": ["eventOutcomeInformation", "eventOutcome"],
    "event_outcome_detail": ["eventOutcomeInformation", "eventOutcomeDetail"],
    "linking_agent_identifier_type": ["linkingAgentIdentifier", \
        "linkingAgentIdentifierType"],
    "linking_agent_identifier_value": ["linkingAgentIdentifier", \
        "linkingAgentIdentifierValue"],
}


def premisEventXMLToObject(eventXML):
    """
    Event XML -> create Event object
    """

    newEventObject = Event()
    for fieldName, chain in translateDict.iteritems():
        doSimpleXMLAssignment(newEventObject, fieldName, eventXML, chain)
    linkingObjectIDNodes = getNodesByName(eventXML, "linkingObjectIdentifier")
    try:
        Event.objects.get(event_identifier=identifier)
        resp = HttpResponse('The uuid already exists')
        resp.status_code = 409
        return resp
    except Exception, e:
        pass
    # if we dont have a uuid looking event_identifier
    # create our own before we save.
    try:
        uuid.UUID(newEventObject.event_identifier)
    except Exception, e:
        newEventObject.event_identifier = uuid.uuid4().hex
    newEventObject.save()
    for linkingObjectIDNode in linkingObjectIDNodes:
        identifierValue = getValueByName(linkingObjectIDNode, \
            "linkingObjectIdentifierValue")
        try:
            linkObject = LinkObject.objects.get(
                object_identifier=identifierValue
            )
        except LinkObject.DoesNotExist, dne:
            linkObject = LinkObject()
            linkObject.object_identifier = identifierValue
            linkObject.object_type = getValueByName(linkingObjectIDNode, \
                "linkingObjectIdentifierType")
            linkObject.object_role = getValueByName(linkingObjectIDNode, \
                "linkingObjectRole")
            linkObject.save()
        except LinkObject.MultipleObjectsReturned, mob:
            linkObject = LinkObject.objects.filter(
                object_identifier=identifierValue
            )[0]
        newEventObject.linking_objects.add(linkObject)
    datetimeObject = None
    dateString = newEventObject.event_date_time.split(".", 1)[0]
    try:
        datetimeObject = datetime.strptime(dateString, dateFormat)
    except ValueError:
        try:
            datetimeObject = datetime.strptime(dateString, altDateFormat)
        except ValueError:
            raise Exception("Unable to parse %s (%s) into datetime object" % \
                (dateString, newEventObject.event_date_time))
    newEventObject.event_date_time = datetimeObject
    return newEventObject


def premisAgentXMLToObject(agentXML):
    """
    Agent XML -> create Event object
    """

    # we need to make this xpath parseable, and not just raw text.
    entryRoot = etree.XML(agentXML)
    # first, let's get the agent identifier and see if it exists already
    try:
        agent_object = premisAgentXMLgetObject(entryRoot)
    # if we can't get the object, then we're making a new one.
    except Exception:
        agent_object = Agent()
    try:
        # move to identifier node
        agent_xml = entryRoot.xpath("*[local-name() = 'agentIdentifier']")[0]
        agent_identifier = agent_xml.xpath(
            "*[local-name() = 'agentIdentifierValue']"
        )[0].text.strip()
        agent_object.agent_identifier = agent_identifier
        # and now move back to the parent node for the other xpath gets
        agent_xml = agent_xml.getparent()
    except Exception, e:
        raise Exception("Unable to set 'agent_identifier' attribute: %s" % e)
    try:
        agent_object.agent_name = agent_xml.xpath(
            "*[local-name() = 'agentName']"
        )[0].text.strip()
    except Exception, e:
        raise Exception("Unable to set 'agent_name' attribute: %s" % e)
    try:
        agent_object.agent_type = agent_xml.xpath(
            "*[local-name() = 'agentType']"
        )[0].text.strip()
    except Exception, e:
        raise Exception("Unable to set 'agent_type' attribute: %s" % e)
    try:
        agent_object.agent_note = agent_xml.xpath(
            "*[local-name() = 'agentNote']"
        )[0].text.strip()
    except Exception, e:
        pass
    return agent_object


def premisEventXMLgetObject(eventXML):
    """
    Given an XML object of a Premis event element, get the existing object of
    the same identifier
    """

    identifierValue = ''
    tag = []
    for element in eventXML:
        if element.tag == '{http://www.w3.org/2005/Atom}id':
            identifierValue = element.text
    ExistingObject = get_object_or_404(Event, event_identifier=identifierValue)
    return ExistingObject


def premisAgentXMLgetObject(agentXML):
    """
    Agent XML -> existing object
    """

    agent_xml = agentXML.xpath("*[local-name() = 'agentIdentifier']")[0]
    agent_identifier = agent_xml.xpath(
        "*[local-name() = 'agentIdentifierValue']"
    )[0].text.strip()
    ExistingObject = get_object_or_404(
        Agent, agent_identifier=agent_identifier
    )
    return ExistingObject


def objectToPremisEventXML(eventObject):
    """
    Event Django Object -> XML
    """

    eventXML = etree.Element("%sevent" % PREMIS, nsmap=PREMIS_NSMAP)
    for fieldName, chain in translateDict.iteritems():
        if not hasattr(eventObject, fieldName):
            continue
        baseName = chain[0]
        baseNode = getNodeByName(eventXML, baseName)
        chain = chain[1:]
        if baseNode == None:
            baseNode = etree.SubElement(eventXML, PREMIS + baseName)
        for i in range(len(chain)):
            chainItem = chain[i]
            parentNode = baseNode
            baseNode = getNodeByName(eventXML, chainItem)
            if baseNode == None:
                baseNode = etree.SubElement(parentNode, PREMIS + chainItem)
        try:
            baseNode.text = getattr(eventObject, fieldName)
        except TypeError, t:
            value = getattr(eventObject, fieldName)
            if type(value) == datetime:
                baseNode.text = value.strftime(dateFormat)
    linking_objects = eventObject.linking_objects.all()
    for linking_object in linking_objects:
        linkObjectIDXML = etree.SubElement(
            eventXML, PREMIS + "linkingObjectIdentifier"
        )
        linkObjectIDTypeXML = etree.SubElement(
            linkObjectIDXML, PREMIS + "linkingObjectIdentifierType"
        )
        linkObjectIDTypeXML.text = linking_object.object_type
        linkObjectIDValueXML = etree.SubElement(
            linkObjectIDXML, PREMIS + "linkingObjectIdentifierValue"
        )
        linkObjectIDValueXML.text = linking_object.object_identifier
        linkObjectIDRoleXML = etree.SubElement(
            linkObjectIDXML, PREMIS + "linkingObjectRole"
        )
        linkObjectIDRoleXML.text = linking_object.object_role
    return eventXML


def objectToAgentXML(agentObject):
    """
    Agent Django object -> XML
    """

    # get current site for domain prefix
    domain_prefix = Site.objects.get_current().domain
    agentXML = etree.Element(PREMIS + "agent", nsmap=PREMIS_NSMAP)
    agentIdentifier = etree.SubElement(agentXML, PREMIS + "agentIdentifier")
    agentIdentifierValue = etree.SubElement(
        agentIdentifier, PREMIS + "agentIdentifierValue"
    )
    agentIdentifierValue.text = agentObject.agent_identifier
    agentIdentifierType = etree.SubElement(
        agentIdentifier, PREMIS + "agentIdentifierType"
    )
    # is this just a constant? yes.
    agentIdentifierType.text = "PES:Agent"
    agentName = etree.SubElement(agentXML, PREMIS + "agentName")
    agentName.text = agentObject.agent_name
    agentType = etree.SubElement(agentXML, PREMIS + "agentType")
    agentType.text = [tup for tup in AGENT_TYPE_CHOICES if \
        tup[0] == agentObject.agent_type][0][1]
    return agentXML


def objectToPremisAgentXML(agentObject, webRoot):
    """
    Agent Django object -> XML
    """

    # get current site for domain prefix
    domain_prefix = Site.objects.get_current().domain
    agentXML = etree.Element(PREMIS + "agent", nsmap=PREMIS_NSMAP)
    agentIdentifier = etree.SubElement(agentXML, PREMIS + "agentIdentifier")
    agentIdentifierValue = etree.SubElement(
        agentIdentifier, PREMIS + "agentIdentifierValue"
    )
    agentIdentifierValue.text = 'http://%s/%s/' % (
        webRoot, agentObject.agent_identifier
    )
    agentIdentifierType = etree.SubElement(
        agentIdentifier, PREMIS + "agentIdentifierType"
    )
    # is this just a constant? yes.
    agentIdentifierType.text = settings.LINK_AGENT_ID_TYPE_XML
    agentName = etree.SubElement(agentXML, PREMIS + "agentName")
    agentName.text = agentObject.agent_name
    agentType = etree.SubElement(agentXML, PREMIS + "agentType")
    agentType.text = [tup for tup in AGENT_TYPE_CHOICES if \
        tup[0] == agentObject.agent_type][0][1]
    return agentXML


def doSimpleXMLAssignment(recordObject, fieldName, node, chain):
    """
    """

    if type(chain) != type([]) and type(chain) != type(()):
        chain = [chain]
    currentNode = getNodeByName(node, chain[0])
    chain = chain[1:]
    for i in range(len(chain)):
        chainItem = chain[i]
        currentNode = getNodeByName(currentNode, chainItem)
    if currentNode != None and currentNode.text:
        value = currentNode.text.strip()
    else:
        value = None
    if value:
        setattr(recordObject, fieldName, value)
