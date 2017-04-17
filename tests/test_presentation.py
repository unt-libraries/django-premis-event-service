from datetime import datetime

from mock import patch
from lxml import etree, objectify
import pytest

from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist

from premis_event_service import presentation, models
from premis_event_service import settings
from . import factories

from codalib.xsdatetime import xsDateTime_format, localize_datetime


def etree_to_objectify(tree):
    """Test helper to convert an etree object to an objectify object."""
    return objectify.fromstring(etree.tostring(tree))


def objectify_to_etree(obj):
    """Test helper to convert an objectify object to an etree object."""
    return etree.fromstring(etree.tostring(obj))


def has_premis_namespace(tree):
    """True if the element has the Premis namespace.

    Arguments:
        tree: An etree._Element instance.
    """
    return tree.nsmap['premis'] == 'info:lc/xmlns/premis-v2'


@pytest.mark.django_db
class TestPremisEventXMLToObject:

    def test_validate_event_fixture(self, event_xml, premis_schema):
        exml = etree.fromstring(event_xml.obj_xml)
        assert isinstance(exml, etree._Element)
        assert isinstance(premis_schema, etree.XMLSchema)
        # validate event fixture doc against premis v2.3 XSD
        premis_schema.assert_(exml)

    def test_returns_event(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)
        assert isinstance(event, models.Event)

    def test_returns_event_without_some_elements(self):
        # The event XML is valid but lacks some elements.
        obj_xml = """<?xml version="1.0"?>
            <premis:event xmlns:premis="info:lc/xmlns/premis-v2">
                <premis:eventIdentifier>
                    <premis:eventIdentifierType>http://purl.org/net/untl/vocabularies/identifier-qualifiers/#UUID</premis:eventIdentifierType>
                    <premis:eventIdentifierValue>1a81d172ce8f465fbcb52d146485f882</premis:eventIdentifierValue>
                </premis:eventIdentifier>
                <premis:eventType>http://purl.org/net/untl/vocabularies/preservationEvents/#fixityCheck</premis:eventType>
                <premis:eventDateTime>2017-05-13T09:14:55-05:00</premis:eventDateTime>
            </premis:event>
        """
        tree = etree.fromstring(obj_xml)
        event = presentation.premisEventXMLToObject(tree)
        assert isinstance(event, models.Event)

    def test_sets_event_type(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.event_type == xml_obj.eventType

    def test_sets_identifier_type(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.event_identifier_type == xml_obj.eventIdentifier.eventIdentifierType

    def test_sets_event_date_time(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)
        xml_obj = etree_to_objectify(tree)

        assert isinstance(event.event_date_time, datetime)
        xsdt = xsDateTime_format(event.event_date_time)
        assert xsdt in xml_obj.eventDateTime.text

    def test_sets_event_detail(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.event_detail == xml_obj.eventDetail

    def test_sets_event_outcome(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.event_outcome == xml_obj.eventOutcomeInformation.eventOutcome

    def test_sets_event_outcome_detail(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        eodn = xml_obj.eventOutcomeInformation.eventOutcomeDetail
        eodn = eodn.eventOutcomeDetailNote
        assert event.event_outcome_detail == eodn

    def test_sets_linking_agent_identifier_type(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.linking_agent_identifier_type == (xml_obj
                                                       .linkingAgentIdentifier
                                                       .linkingAgentIdentifierType)

    def test_sets_linking_agent_identifier_value(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.linking_agent_identifier_value == (xml_obj
                                                        .linkingAgentIdentifier
                                                        .linkingAgentIdentifierValue)

    def test_linking_objects_added(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        linking_objects = list(xml_obj.linkingObjectIdentifier)

        assert len(linking_objects) == event.linking_objects.count()

    def test_linking_objects_attributes(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        xml_linking_object_id = xml_obj.linkingObjectIdentifier.linkingObjectIdentifierValue.text
        xml_linking_object_type = xml_obj.linkingObjectIdentifier.linkingObjectIdentifierType.text

        # Get the newly created LinkObject from the database.
        linking_object = event.linking_objects.get(object_identifier=xml_linking_object_id)

        # Assert that the database version matches the values defined in the XML.
        assert xml_linking_object_id == linking_object.object_identifier
        assert xml_linking_object_type == linking_object.object_type

    @pytest.mark.xfail(reason='Try block always catches a NameError before able to return.')
    def test_existing_event_identifier_results_in_HttpResponse(self, event_xml):
        tree = etree.fromstring(event_xml.obj_xml)

        factories.EventFactory.create(event_identifier=event_xml.identifier)
        event_or_response = presentation.premisEventXMLToObject(tree)

        assert isinstance(event_or_response, HttpResponse)

    def test_duplicate_event_id_raises_duplicate_error(self, event_xml):
        # Replace the existing hex identifier with a non-hex identifier.
        invalid_identifier = 'invalid-hex'
        xml_obj = objectify.fromstring(event_xml.obj_xml)
        xml_obj.eventIdentifier.eventIdentifierValue = invalid_identifier

        tree = objectify_to_etree(xml_obj)

        # Create an Event with the identifier.
        factories.EventFactory.create(event_identifier=invalid_identifier)
        # Try to create an Event with the same identifier (from xml).
        with pytest.raises(presentation.DuplicateEventError):
            presentation.premisEventXMLToObject(tree)

    @pytest.mark.xfail(reason='Validation error is raised on save(). The exception '
                              'this function tests will never be raised.')
    def test_invalid_datetime_string_raises_exception(self, event_xml):
        # Replace the datetime string with an invalid datetime string.
        xml_obj = objectify.fromstring(event_xml.obj_xml)
        xml_obj.eventDateTime = 'invalid-datetime'

        tree = objectify_to_etree(xml_obj)

        with pytest.raises(Exception) as e:
            presentation.premisEventXMLToObject(tree)

        # Since the base Exception is raised from the function, we want to make
        # sure it is the correct Exception, so now check the error message and
        # see if it matches the expected message.
        assert 'Unable to parse' in str(e)
        assert 'into datetime object' in str(e)

    def test_datetime_that_has_milliseconds(self, event_xml):
        """Test that a datetime string that contains milliseconds is properly
        converted to a datetime object.
        """
        # Replace the datetime string with a valid datetime string that
        # contains milliseconds.
        date_string = '1997-07-16T19:20:30.45+01:00'
        xml_obj = objectify.fromstring(event_xml.obj_xml)
        xml_obj.eventDateTime = date_string

        tree = objectify_to_etree(xml_obj)
        event = presentation.premisEventXMLToObject(tree)

        assert isinstance(event.event_date_time, datetime)

    def test_datetime_without_milliseconds(self, event_xml):
        """Test that a datetime string that does not contains milliseconds
        is properly converted to a datetime object.
        """
        # Replace the datetime string with a valid datetime string that
        # does not contain milliseconds.
        date_string = '1997-07-16T19:20:30'
        xml_obj = objectify.fromstring(event_xml.obj_xml)
        xml_obj.eventDateTime = date_string

        tree = objectify_to_etree(xml_obj)
        event = presentation.premisEventXMLToObject(tree)

        assert isinstance(event.event_date_time, datetime)


@pytest.mark.django_db
class TestPremisAgentXMLToObject:

    def test_validate_agent_fixture(self, agent_xml, premis_schema):
        axml = etree.fromstring(agent_xml.obj_xml)
        assert isinstance(axml, etree._Element)
        assert isinstance(premis_schema, etree.XMLSchema)
        # validate agent fixture doc against premis v2.3 XSD
        premis_schema.assert_(axml)

    def test_returns_agent(self, agent_xml):
        agent = presentation.premisAgentXMLToObject(agent_xml.obj_xml)
        assert isinstance(agent, models.Agent)

    @patch('premis_event_service.presentation.premisAgentXMLgetObject')
    @patch('premis_event_service.presentation.Agent')
    def test_creates_new_agent(self, agent_mock, get_object_mock, agent_xml):
        """Check that a new Agent object is created if an existing Agent
        cannot be retrieved.
        """
        # get_object_mock is the mock that is patched over premisAgentXMLgetObject.
        # The name change is for brevity.
        get_object_mock.side_effect = Exception
        presentation.premisAgentXMLToObject(agent_xml.obj_xml)

        # Agent will be called only if the call to premisAgentXMLgetObject
        # raises an exception. We will verify that both mocks have been
        # called to assert that premisAgentXMLgetObject raised and exception
        # and a new Agent was created.
        assert get_object_mock.called
        assert agent_mock.called

    @patch('premis_event_service.presentation.premisAgentXMLgetObject')
    @patch('premis_event_service.presentation.Agent')
    def test_gets_existing_agent(self, agent_mock, get_object_mock, agent_xml):
        presentation.premisAgentXMLToObject(agent_xml.obj_xml)

        assert get_object_mock.called
        # If agent_mock was not called, we know that an existing Agent was
        # retrieved.
        assert not agent_mock.called

    def test_sets_agent_identifier(self, agent_xml):
        agent = presentation.premisAgentXMLToObject(agent_xml.obj_xml)
        xml_obj = objectify.fromstring(agent_xml.obj_xml)
        assert agent.agent_identifier == xml_obj.agentIdentifier.agentIdentifierValue

    def test_raises_exception_when_agent_identifier_is_missing(self, agent_xml):
        xml_obj = objectify.fromstring(agent_xml.obj_xml)
        del xml_obj.agentIdentifier

        with pytest.raises(Exception) as e:
            presentation.premisAgentXMLToObject(etree.tostring(xml_obj))

        expected_message = "Unable to set 'agent_identifier'"
        assert expected_message in str(e), 'The exception message matches'

    def test_sets_agent_type(self, agent_xml):
        agent = presentation.premisAgentXMLToObject(agent_xml.obj_xml)
        xml_obj = objectify.fromstring(agent_xml.obj_xml)
        assert agent.agent_type == xml_obj.agentType

    def test_raises_exception_when_agent_type_is_missing(self, agent_xml):
        xml_obj = objectify.fromstring(agent_xml.obj_xml)
        del xml_obj.agentType

        with pytest.raises(Exception) as e:
            presentation.premisAgentXMLToObject(etree.tostring(xml_obj))

        expected_message = "Unable to set 'agent_type'"
        assert expected_message in str(e), 'The exception message matches'

    def test_sets_agent_name(self, agent_xml):
        agent = presentation.premisAgentXMLToObject(agent_xml.obj_xml)
        xml_obj = objectify.fromstring(agent_xml.obj_xml)
        assert agent.agent_name == xml_obj.agentName

    def test_raises_exception_when_agent_name_is_missing(self, agent_xml):
        xml_obj = objectify.fromstring(agent_xml.obj_xml)
        del xml_obj.agentName

        with pytest.raises(Exception) as e:
            presentation.premisAgentXMLToObject(etree.tostring(xml_obj))

        expected_message = "Unable to set 'agent_name'"
        assert expected_message in str(e), 'The exception message matches'

    def test_sets_agent_note(self, agent_xml):
        agent = presentation.premisAgentXMLToObject(agent_xml.obj_xml)
        xml_obj = objectify.fromstring(agent_xml.obj_xml)
        assert agent.agent_note == xml_obj.agentNote

    def test_exception_not_raised_when_agent_note_is_missing(self, agent_xml):
        xml_obj = objectify.fromstring(agent_xml.obj_xml)
        del xml_obj.agentNote
        presentation.premisAgentXMLToObject(etree.tostring(xml_obj))
        # No assertions here. We only want to make sure that no exceptions
        # were raised.


@pytest.mark.django_db
class TestPremisEventXMLGetObjects:

    def test_validate_event_fixture(self, event_xml, premis_schema):
        exml = etree.fromstring(event_xml.obj_xml)
        assert isinstance(exml, etree._Element)
        assert isinstance(premis_schema, etree.XMLSchema)
        # validate event fixture doc against premis v2.3 XSD
        premis_schema.assert_(exml)

    def test_returns_correct_event_object(self, event_xml):
        tree = etree.fromstring(event_xml.entry_xml)
        factories.EventFactory(event_identifier=event_xml.identifier)
        event_obj = presentation.premisEventXMLgetObject(tree)
        assert event_obj.event_identifier == event_xml.identifier
        assert isinstance(event_obj, models.Event)

    def test_raises_doesnotexist_if_object_not_found(self, event_xml):
        tree = etree.fromstring(event_xml.entry_xml)
        with pytest.raises(ObjectDoesNotExist):
            presentation.premisEventXMLgetObject(tree)

    def test_raises_noeventidentifier_when_xml_has_no_id(self, event_xml):
        xml_obj = objectify.fromstring(event_xml.entry_xml)
        del xml_obj.id
        xml_obj.find(
            './/premis:eventIdentifierValue', namespaces=presentation.PREMIS_NSMAP
        ).clear()
        tree = objectify_to_etree(xml_obj)

        factories.EventFactory(event_identifier=event_xml.identifier)

        with pytest.raises(presentation.NoEventIdentifier):
            presentation.premisEventXMLgetObject(tree)

    def test_returns_correct_event_on_uri_id(self, event_xml):
        factories.EventFactory(event_identifier=event_xml.identifier)
        base_id = event_xml.identifier
        event_xml.identifier = 'http://example.com/a/b/c/{}'.format(base_id)
        xml_obj = objectify.fromstring(event_xml.entry_xml)
        tree = objectify_to_etree(xml_obj)
        event_obj = presentation.premisEventXMLgetObject(tree)
        assert event_obj.event_identifier == base_id


@pytest.mark.django_db
class TestPremisAgentXMLGetObjects:

    def test_returns_correct_agent_object(self, agent_xml):
        tree = etree.fromstring(agent_xml.obj_xml)
        factories.AgentFactory(agent_identifier=agent_xml.identifier)
        agent_obj = presentation.premisAgentXMLgetObject(tree)
        assert agent_obj.agent_identifier == agent_xml.identifier
        assert isinstance(agent_obj, models.Agent)

    def test_raises_Http404_if_object_not_found(self, agent_xml):
        tree = etree.fromstring(agent_xml.obj_xml)
        with pytest.raises(Http404):
            presentation.premisAgentXMLgetObject(tree)


@pytest.mark.django_db
class TestObjectToPremisEventXML:

    def test_returns_Element(self):
        event = factories.EventFactory()
        event_xml = presentation.objectToPremisEventXML(event)
        assert isinstance(event_xml, etree._Element)

    def test_root_namespace(self):
        event = factories.EventFactory()
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)
        assert has_premis_namespace(event_xml)

    def test_event_identifier(self):
        event = factories.EventFactory()
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        element = event_xml.eventIdentifier.eventIdentifierValue
        assert element == event.event_identifier
        assert has_premis_namespace(element)

    def test_event_identifier_type(self):
        event = factories.EventFactory()
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        element = event_xml.eventIdentifier.eventIdentifierType
        assert element == event.event_identifier_type
        assert has_premis_namespace(element)

    def test_event_type(self):
        event = factories.EventFactory()
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        element = event_xml.eventType
        assert element == event.event_type
        assert has_premis_namespace(element)

    def test_event_date_time(self):
        event = factories.EventFactory()
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        element = event_xml.eventDateTime
        dt = event.event_date_time
        dt = localize_datetime(dt)
        assert element.text == xsDateTime_format(dt)
        assert has_premis_namespace(element)

    def test_event_outcome(self):
        event = factories.EventFactory()
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        element = event_xml.eventOutcomeInformation.eventOutcome
        assert element == event.event_outcome
        assert has_premis_namespace(element)

    def test_event_outcome_detail(self):
        event = factories.EventFactory()
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        element = event_xml.eventOutcomeInformation.eventOutcomeDetail
        element = element.eventOutcomeDetailNote
        assert element == event.event_outcome_detail
        assert has_premis_namespace(element)

    def test_event_detail(self):
        event = factories.EventFactory()
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        element = event_xml.eventDetail
        assert element == event.event_detail
        assert has_premis_namespace(element)

    def test_linking_agent_identifier_value(self):
        event = factories.EventFactory()
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        element = event_xml.linkingAgentIdentifier.linkingAgentIdentifierValue
        assert element == event.linking_agent_identifier_value
        assert has_premis_namespace(element)

    def test_linking_agent_identifier_type(self):
        event = factories.EventFactory()
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        element = event_xml.linkingAgentIdentifier.linkingAgentIdentifierType
        assert element == event.linking_agent_identifier_type
        assert has_premis_namespace(element)

    def test_link_object_identifier(self):
        event = factories.EventFactory(linking_objects=True, linking_objects__count=2)
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        element = event_xml.linkingObjectIdentifier
        assert len(element) == 2
        assert has_premis_namespace(element)

    def test_link_object_identifier_value(self):
        event = factories.EventFactory(linking_objects=True)
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        linking_object = event.linking_objects.first()

        element = event_xml.linkingObjectIdentifier.linkingObjectIdentifierValue
        assert element == linking_object.object_identifier
        assert has_premis_namespace(element)

    def test_link_object_identifier_type(self):
        event = factories.EventFactory(linking_objects=True)
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        linking_object = event.linking_objects.first()

        element = event_xml.linkingObjectIdentifier.linkingObjectIdentifierType
        assert element == linking_object.object_type
        assert has_premis_namespace(element)

    def test_link_object_role(self):
        event = factories.EventFactory(linking_objects=True)
        tree = presentation.objectToPremisEventXML(event)
        event_xml = etree_to_objectify(tree)

        linking_object = event.linking_objects.first()

        element = event_xml.linkingObjectIdentifier.linkingObjectRole
        assert element.text == linking_object.object_role
        assert has_premis_namespace(element)

    def test_validate_eventxml(self, premis_schema):
        event = factories.EventFactory()
        event_xml = presentation.objectToPremisEventXML(event)
        premis_schema.assert_(event_xml)


@pytest.mark.django_db
class TestObjectToAgentXML:

    def test_returns_Element(self):
        agent = factories.AgentFactory()
        agent_xml = presentation.objectToAgentXML(agent)
        assert isinstance(agent_xml, etree._Element)

    def test_root_namespace(self):
        agent = factories.AgentFactory()
        agent_xml = presentation.objectToAgentXML(agent)
        assert has_premis_namespace(agent_xml)

    def test_agent_identifier_value(self):
        agent = factories.AgentFactory()
        tree = presentation.objectToAgentXML(agent)
        agent_xml = etree_to_objectify(tree)

        element = agent_xml.agentIdentifier.agentIdentifierValue
        assert element == agent.agent_identifier
        assert has_premis_namespace(element)

    def test_agent_identifier_type(self):
        agent = factories.AgentFactory()
        tree = presentation.objectToAgentXML(agent)
        agent_xml = etree_to_objectify(tree)

        element = agent_xml.agentIdentifier.agentIdentifierType
        assert element == presentation.PES_AGENT_ID_TYPE
        assert has_premis_namespace(element)

    def test_agent_name(self):
        agent = factories.AgentFactory()
        tree = presentation.objectToAgentXML(agent)
        agent_xml = etree_to_objectify(tree)

        element = agent_xml.agentName
        assert element == agent.agent_name
        assert has_premis_namespace(element)

    def test_agent_type(self):
        agent = factories.AgentFactory()
        tree = presentation.objectToAgentXML(agent)
        agent_xml = etree_to_objectify(tree)

        element = agent_xml.agentType
        assert element == agent.agent_type
        assert has_premis_namespace(element)

    def test_validate_agentxml(self, premis_schema):
        agent = factories.AgentFactory()
        agent_xml = presentation.objectToAgentXML(agent)
        premis_schema.assert_(agent_xml)


@pytest.mark.django_db
class TestObjectToPremisAgentXML:

    def test_returns_Element(self):
        agent = factories.AgentFactory()
        agent_xml = presentation.objectToPremisAgentXML(agent, 'example.com')
        assert isinstance(agent_xml, etree._Element)

    def test_root_namespace(self):
        agent = factories.AgentFactory()
        agent_xml = presentation.objectToPremisAgentXML(agent, 'example.com')
        assert has_premis_namespace(agent_xml)

    def test_agent_identifier_value(self):
        agent = factories.AgentFactory()
        tree = presentation.objectToPremisAgentXML(agent, 'example.com')
        agent_xml = etree_to_objectify(tree)

        element = agent_xml.agentIdentifier.agentIdentifierValue
        identifier = 'http://example.com/agent/{0}/'.format(agent.agent_identifier)
        assert element == identifier
        assert has_premis_namespace(element)

    def test_agent_identifier_type(self):
        agent = factories.AgentFactory()
        tree = presentation.objectToPremisAgentXML(agent, 'example.com')
        agent_xml = etree_to_objectify(tree)

        element = agent_xml.agentIdentifier.agentIdentifierType
        assert element == settings.LINK_AGENT_ID_TYPE_XML
        assert has_premis_namespace(element)

    def test_agent_name(self):
        agent = factories.AgentFactory()
        tree = presentation.objectToPremisAgentXML(agent, 'example.com')
        agent_xml = etree_to_objectify(tree)

        element = agent_xml.agentName
        assert element == agent.agent_name
        assert has_premis_namespace(element)

    def test_agent_type(self):
        agent = factories.AgentFactory()
        tree = presentation.objectToPremisAgentXML(agent, 'example.com')
        agent_xml = etree_to_objectify(tree)

        element = agent_xml.agentType
        assert element == agent.agent_type
        assert has_premis_namespace(element)

    def test_validate_agentxml(self, premis_schema):
        agent = factories.AgentFactory()
        agent_xml = presentation.objectToPremisAgentXML(agent, 'example.com')
        premis_schema.assert_(agent_xml)
