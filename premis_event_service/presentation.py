from datetime import datetime
import uuid
from urlparse import urlparse

from lxml import etree
from django.shortcuts import get_object_or_404

from codalib.bagatom import getValueByName, getNodeByName, getNodesByName
from codalib.xsdatetime import xsDateTime_parse, xsDateTime_format, localize_datetime
from .models import Event, Agent, LinkObject, AGENT_TYPE_CHOICES
from premis_event_service import settings
import collections

PREMIS_NAMESPACE = 'info:lc/xmlns/premis-v2'
PREMIS = '{%s}' % PREMIS_NAMESPACE
PREMIS_NSMAP = {'premis': PREMIS_NAMESPACE}
PES_AGENT_ID_TYPE = 'PES:Agent'

translateDict = collections.OrderedDict()
translateDict['event_identifier_type'] = ['eventIdentifier', 'eventIdentifierType']
translateDict['event_identifier'] = ['eventIdentifier', 'eventIdentifierValue']
translateDict['event_type'] = ['eventType']
translateDict['event_date_time'] = ['eventDateTime']
translateDict['event_detail'] = ['eventDetail']
translateDict['event_outcome'] = ['eventOutcomeInformation', 'eventOutcome']
translateDict['event_outcome_detail'] = [
    'eventOutcomeInformation', 'eventOutcomeDetail', 'eventOutcomeDetailNote'
]
translateDict['linking_agent_identifier_type'] = [
    'linkingAgentIdentifier', 'linkingAgentIdentifierType'
]
translateDict['linking_agent_identifier_value'] = [
    'linkingAgentIdentifier', 'linkingAgentIdentifierValue'
]

xpath_map = collections.OrderedDict()
xpath_map['@namespaces'] = PREMIS_NSMAP
xpath_map['event_identifier_type'] = 'premis:eventIdentifier/eventIdentifierType'
xpath_map['event_identifier'] = 'premis:eventIdentifier/premis:eventIdentifierValue'
xpath_map['event_type'] = 'premis:eventType'
xpath_map['event_date_time'] = 'premis:eventDateTime'
xpath_map['event_detail'] = 'premis:eventDetail'
xpath_map['event_outcome'] = 'premis:eventOutcomeInformation/premis:eventOutcome'
xpath_map['event_outcome_detail'] = 'premis:eventOutcomeInformation' + \
        '/premis:eventOutcomeDetail/premis:eventOutcomeDetailNote'
xpath_map['linking_agent_identifier_type'] = 'premis:linkingAgentIdentifier' + \
        '/premis:linkingAgentIdentifierType'
xpath_map['linking_agent_identifier_value'] = 'premis:linkingAgentIdentifier' + \
        '/premis:linkingAgentIdentifierValue'


class DuplicateEventError(Exception):
    pass


class NoEventIdentifier(Exception):
    pass


def premisEventXMLToObject(eventXML):
    """
    Event XML -> create Event object
    """

    newEventObject = Event()
    for fieldName, chain in translateDict.iteritems():
        doSimpleXMLAssignment(newEventObject, fieldName, eventXML, chain)
    linkingObjectIDNodes = getNodesByName(eventXML, "linkingObjectIdentifier")
    try:
        Event.objects.get(event_identifier=newEventObject.event_identifier)
        raise DuplicateEventError(newEventObject.event_identifier)
    except Event.DoesNotExist as e:
        pass
    except DuplicateEventError as e:
        raise e
    # if we dont have a uuid looking event_identifier
    # create our own before we save.
    try:
        uuid.UUID(newEventObject.event_identifier)
    except Exception, e:
        newEventObject.event_identifier = uuid.uuid4().hex
    if not isinstance(newEventObject.event_date_time, datetime):
        newEventObject.event_date_time = xsDateTime_parse(
            newEventObject.event_date_time
        )
    newEventObject.save()
    for linkingObjectIDNode in linkingObjectIDNodes:
        identifierValue = getValueByName(
            linkingObjectIDNode, "linkingObjectIdentifierValue")
        try:
            linkObject = LinkObject.objects.get(
                object_identifier=identifierValue
            )
        except LinkObject.DoesNotExist:
            linkObject = LinkObject()
            linkObject.object_identifier = identifierValue
            linkObject.object_type = getValueByName(
                linkingObjectIDNode, "linkingObjectIdentifierType")
            linkObject.object_role = getValueByName(
                linkingObjectIDNode, "linkingObjectRole")
            linkObject.save()
        except LinkObject.MultipleObjectsReturned:
            linkObject = LinkObject.objects.filter(
                object_identifier=identifierValue
            )[0]
        newEventObject.linking_objects.add(linkObject)
    return newEventObject


def premisAgentXMLToObject(agentXML):
    """
    Agent XML -> create Event object
    """

    # we need to make this xpath parseable, and not just raw text.
    entryRoot = etree.XML(agentXML)
    agent_root = entryRoot.xpath('//premis:agent', namespaces=PREMIS_NSMAP)[0]
    # first, let's get the agent identifier and see if it exists already
    try:
        agent_object = premisAgentXMLgetObject(agent_root)
    # if we can't get the object, then we're making a new one.
    except Exception:
        agent_object = Agent()
    try:
        # move to identifier node
        agent_identifier = agent_root.xpath(
            "//premis:agentIdentifierValue",
            namespaces=PREMIS_NSMAP
        )[0].text.strip()
        agent_object.agent_identifier = agent_identifier
    except Exception, e:
        raise Exception("Unable to set 'agent_identifier' attribute: %s" % e)
    try:
        agent_object.agent_name = agent_root.xpath(
            "//premis:agentName", namespaces=PREMIS_NSMAP
        )[0].text.strip()
    except Exception, e:
        raise Exception("Unable to set 'agent_name' attribute: %s" % e)
    try:
        agent_object.agent_type = agent_root.xpath(
            "//premis:agentType", namespaces=PREMIS_NSMAP
        )[0].text.strip()
    except Exception, e:
        raise Exception("Unable to set 'agent_type' attribute: %s" % e)
    try:
        agent_object.agent_note = agent_root.xpath(
                "//premis:agentNote", namespaces=PREMIS_NSMAP
        )[0].text.strip()
    except Exception, e:
        pass
    return agent_object


def premisEventXMLgetObject(eventXML):
    """
    Given an XML object of a Premis event element, get the existing object of
    the same identifier
    """

    identifierValue = None
    # Look for Event ID in entry metadata.
    try:
        identifierValue = eventXML.xpath('//id')[0].text
    except (etree.LxmlError, IndexError):
        pass
    # If no Event ID in entry metadata, look in
    # premis:event eventIdentifierValue element.
    if not identifierValue:
        try:
            identifierValue = eventXML.xpath(
                '//premis:eventIdentifierValue', namespaces=PREMIS_NSMAP
            )[0].text
        except (etree.LxmlError, IndexError):
            raise NoEventIdentifier('No event identifier in request XML.')
    # It's possible that the XML tree is malformed, e.g. an empty
    # eventIdentifierValue element. Check for '' or None again here.
    if not identifierValue:
        raise NoEventIdentifier('Missing event identifier.')
    # If we have some kind of identifier, we check to see if it's url-ish
    # and strip the ID out of the path if it is.
    parsed_url = urlparse(identifierValue)
    if parsed_url.scheme:
        try:
            identifierValue = parsed_url.path.strip('/').split('/')[-1]
        except IndexError:
            raise NoEventIdentifier('Malformed event identifier in request XML.')
    existing_obj = Event.objects.get(event_identifier=identifierValue)
    return existing_obj


def premisAgentXMLgetObject(agentXML):
    """
    Agent XML -> existing object
    """
    agent_xml = agentXML.xpath("//premis:agent", namespaces=PREMIS_NSMAP)[0]
    agent_identifier = agent_xml.xpath(
        "//premis:agentIdentifierValue", namespaces=PREMIS_NSMAP
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
        if baseNode is None:
            baseNode = etree.SubElement(eventXML, PREMIS + baseName)
        for i in range(len(chain)):
            chainItem = chain[i]
            parentNode = baseNode
            baseNode = getNodeByName(eventXML, chainItem)
            if baseNode is None:
                baseNode = etree.SubElement(parentNode, PREMIS + chainItem)
        try:
            baseNode.text = getattr(eventObject, fieldName)
        except TypeError:
            value = getattr(eventObject, fieldName)
            if isinstance(value, datetime):
                if value.tzinfo is None:
                    value = localize_datetime(value)
                baseNode.text = xsDateTime_format(value)
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

    agentXML = etree.Element(PREMIS + "agent", nsmap=PREMIS_NSMAP)
    agentIdentifier = etree.SubElement(agentXML, PREMIS + "agentIdentifier")
    # order matters here. these items are defined as part of the
    # agentIdentifier *sequence* in the XSD -- type must come first
    # to validate
    agentIdentifierType = etree.SubElement(
        agentIdentifier, PREMIS + "agentIdentifierType"
    )
    # is this just a constant? yes.
    agentIdentifierType.text = PES_AGENT_ID_TYPE
    agentIdentifierValue = etree.SubElement(
        agentIdentifier, PREMIS + "agentIdentifierValue"
    )
    agentIdentifierValue.text = agentObject.agent_identifier
    agentName = etree.SubElement(agentXML, PREMIS + "agentName")
    agentName.text = agentObject.agent_name
    agentType = etree.SubElement(agentXML, PREMIS + "agentType")
    agentType.text = [tup for tup in AGENT_TYPE_CHOICES if
                      tup[0] == agentObject.agent_type][0][1]
    return agentXML


def objectToPremisAgentXML(agentObject, webRoot):
    """
    Agent Django object -> XML
    """

    agentXML = etree.Element(PREMIS + "agent", nsmap=PREMIS_NSMAP)
    agentIdentifier = etree.SubElement(agentXML, PREMIS + "agentIdentifier")
    agentIdentifierType = etree.SubElement(
        agentIdentifier, PREMIS + "agentIdentifierType"
    )
    # is this just a constant? yes.
    agentIdentifierType.text = settings.LINK_AGENT_ID_TYPE_XML
    agentIdentifierValue = etree.SubElement(
        agentIdentifier, PREMIS + "agentIdentifierValue"
    )
    agentIdentifierValue.text = 'http://%s%s' % (
        webRoot, agentObject.get_absolute_url()
    )
    agentName = etree.SubElement(agentXML, PREMIS + "agentName")
    agentName.text = agentObject.agent_name
    agentType = etree.SubElement(agentXML, PREMIS + "agentType")
    agentType.text = [tup for tup in AGENT_TYPE_CHOICES if
                      tup[0] == agentObject.agent_type][0][1]
    return agentXML


def doSimpleXMLAssignment(recordObject, fieldName, node, chain):
    """
    """

    if not isinstance(chain, list) and not isinstance(chain, tuple):
        chain = [chain]
    currentNode = getNodeByName(node, chain[0])
    chain = chain[1:]
    for i in range(len(chain)):
        chainItem = chain[i]
        currentNode = getNodeByName(currentNode, chainItem)
    if currentNode is not None and currentNode.text:
        value = currentNode.text.strip()
    else:
        value = None
    if value:
        setattr(recordObject, fieldName, value)
