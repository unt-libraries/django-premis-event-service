from datetime import datetime
import uuid

from mock import patch
from lxml import etree, objectify
import pytest

from django.http import HttpResponse

from premis_event_service import presentation, models
from . import EventTestXml, factories


@pytest.fixture
def event_xml():
    with EventTestXml() as f:
        xml = f.read()

    identifier = '7bea513bbe554f21854c5fd251822b3a'
    return identifier, xml.format(identifier=identifier)


def etree_to_objectify(tree):
    """Test helper to convert an etree object to an objectify object."""
    return objectify.fromstring(etree.tostring(tree))


def objectify_to_etree(obj):
    """Test helper to convert an objectify object to an etree object."""
    return etree.fromstring(etree.tostring(obj))


@pytest.mark.django_db
class TestPremisEventXMLToObject:

    def test_returns_event(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
        event = presentation.premisEventXMLToObject(tree)
        assert isinstance(event, models.Event)

    def test_sets_event_type(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.event_type == xml_obj.eventType

    def test_sets_identifier_type(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.event_identifier_type == xml_obj.eventIdentifier.eventIdentifierType

    def test_sets_event_date_time(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert str(event.event_date_time) == xml_obj.eventDateTime
        assert isinstance(event.event_date_time, datetime)

    def test_sets_event_detail(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.event_detail == xml_obj.eventDetail

    def test_sets_event_outcome(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.event_outcome == xml_obj.eventOutcomeInformation.eventOutcome

    def test_sets_event_outcome_detail(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.event_outcome_detail == xml_obj.eventOutcomeInformation.eventOutcomeDetail

    def test_sets_linking_agent_identifier_type(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.linking_agent_identifier_type == (xml_obj
                                                       .linkingAgentIdentifier
                                                       .linkingAgentIdentifierType)

    def test_sets_linking_agent_identifier_value(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        assert event.linking_agent_identifier_value == (xml_obj
                                                        .linkingAgentIdentifier
                                                        .linkingAgentIdentifierValue)

    def test_linking_objects_added(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
        event = presentation.premisEventXMLToObject(tree)

        xml_obj = etree_to_objectify(tree)
        linking_objects = list(xml_obj.linkingObjectIdentifier)

        assert len(linking_objects) == event.linking_objects.count()

    def test_linking_objects_attributes(self, event_xml):
        identifier, xml = event_xml
        tree = etree.fromstring(xml)
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
        identifier, xml = event_xml
        tree = etree.fromstring(xml)

        factories.EventFactory.create(event_identifier=identifier)
        event_or_response = presentation.premisEventXMLToObject(tree)

        assert isinstance(event_or_response, HttpResponse)

    def test_new_identifier_created_if_not_valid_uuid4(self, event_xml):
        _, xml = event_xml

        # Replace the existing hex identifier with a non-hex identifier.
        invalid_identifier = 'invalid-hex'
        xml_obj = objectify.fromstring(xml)
        xml_obj.eventIdentifier.eventIdentifierValue = invalid_identifier

        tree = objectify_to_etree(xml_obj)

        # Create an Event with the same non-hex identifier.
        factories.EventFactory.create(event_identifier=invalid_identifier)
        event = presentation.premisEventXMLToObject(tree)

        # Make sure the returned Event is given a new hex identifier.
        assert event.event_identifier != invalid_identifier
        assert uuid.UUID(event.event_identifier, version=4)

    @pytest.mark.xfail(reason='Validation error is raised on save(). The exception '
                              'this function tests will never be raised.')
    def test_invalid_datetime_string_raises_exception(self, event_xml):
        _, xml = event_xml

        # Replace the datetime string with an invalid datetime string.
        xml_obj = objectify.fromstring(xml)
        xml_obj.eventDateTime = 'invalid-datetime'

        tree = objectify_to_etree(xml_obj)

        with pytest.raises(Exception) as e:
            presentation.premisEventXMLToObject(tree)

        # Since the base Exception is raised from the function, we want to make
        # sure it is the correct Exception, so now check the error message and
        # see if it matches the expected message.
        assert 'Unable to parse' in str(e)
        assert 'into datetime object' in str(e)

    def test_datetime_that_has_decimal_seconds(self, event_xml):
        """Test that a datetime string that contains a decimal second is properly
        converted to a datetime object.
        """
        _, xml = event_xml

        # Replace the datetime string with a valid datetime string that
        # contains a decimal second field.
        date_string = '1997-07-16T19:20:30.45+01:00'
        xml_obj = objectify.fromstring(xml)
        xml_obj.eventDateTime = date_string

        tree = objectify_to_etree(xml_obj)
        event = presentation.premisEventXMLToObject(tree)

        assert isinstance(event.event_date_time, datetime)


@pytest.mark.django_db
class TestPremisAgentXMLToObject:
    identifier = 'EqLVtAeVnHoR'

    def agent_xml(self, identifier):
        """Agent XML outside the context of of a feed entry.

        Takes an Agent identifier as a argument.
        """
        xml = """<?xml version="1.0"?>
            <premis:agent xmlns:premis="info:lc/xmlns/premis-v2">
              <premis:agentIdentifier>
                <premis:agentIdentifierValue>{identifier}</premis:agentIdentifierValue>
                <premis:agentIdentifierType>PES:Agent</premis:agentIdentifierType>
              </premis:agentIdentifier>
              <premis:agentName>asXbNNQgsgbS</premis:agentName>
              <premis:agentType>Software</premis:agentType>
              <premis:agentNote>This is a test Agent</premis:agentNote>
            </premis:agent>
        """
        return xml.format(identifier=identifier)

    def test_returns_agent(self):
        xml = self.agent_xml(self.identifier)
        agent = presentation.premisAgentXMLToObject(xml)
        assert isinstance(agent, models.Agent)

    @patch('premis_event_service.presentation.premisAgentXMLgetObject')
    @patch('premis_event_service.presentation.Agent')
    def test_creates_new_agent(self, agent_mock, get_object_mock):
        """Check that a new Agent object is created if an existing Agent
        cannot be retrieved.
        """
        xml = self.agent_xml(self.identifier)

        # get_object_mock is the mock that is patched over premisAgentXMLgetObject.
        # The name change is for brevity.
        get_object_mock.side_effect = Exception
        presentation.premisAgentXMLToObject(xml)

        # Agent will be called only if the call to premisAgentXMLgetObject
        # raises an exception. We will verify that both mocks have been
        # called to assert that premisAgentXMLgetObject raised and exception
        # and a new Agent was created.
        assert get_object_mock.called
        assert agent_mock.called

    @patch('premis_event_service.presentation.premisAgentXMLgetObject')
    @patch('premis_event_service.presentation.Agent')
    def test_gets_existing_agent(self, agent_mock, get_object_mock):
        xml = self.agent_xml(self.identifier)
        presentation.premisAgentXMLToObject(xml)

        assert get_object_mock.called
        # If agent_mock was not called, we know that an existing Agent was
        # retrieved.
        assert not agent_mock.called

    def test_sets_agent_identifier(self):
        xml = self.agent_xml(self.identifier)
        presentation.premisAgentXMLToObject(xml)
        agent = presentation.premisAgentXMLToObject(xml)
        xml_obj = objectify.fromstring(xml)
        assert agent.agent_identifier == xml_obj.agentIdentifier.agentIdentifierValue

    def test_raises_exception_when_agent_identifier_is_missing(self):
        xml = self.agent_xml(self.identifier)
        xml_obj = objectify.fromstring(xml)
        del xml_obj.agentIdentifier

        with pytest.raises(Exception) as e:
            presentation.premisAgentXMLToObject(etree.tostring(xml_obj))

        expected_message = "Unable to set 'agent_identifier'"
        assert expected_message in str(e), 'The exception messages matches'

    def test_sets_agent_type(self):
        xml = self.agent_xml(self.identifier)
        agent = presentation.premisAgentXMLToObject(xml)
        xml_obj = objectify.fromstring(xml)
        assert agent.agent_type == xml_obj.agentType

    def test_raises_exception_when_agent_type_is_missing(self):
        xml = self.agent_xml(self.identifier)
        xml_obj = objectify.fromstring(xml)
        del xml_obj.agentType

        with pytest.raises(Exception) as e:
            presentation.premisAgentXMLToObject(etree.tostring(xml_obj))

        expected_message = "Unable to set 'agent_type'"
        assert expected_message in str(e), 'The exception messages matches'

    def test_sets_agent_name(self):
        xml = self.agent_xml(self.identifier)
        agent = presentation.premisAgentXMLToObject(xml)
        xml_obj = objectify.fromstring(xml)
        assert agent.agent_name == xml_obj.agentName

    def test_raises_exception_when_agent_name_is_missing(self):
        xml = self.agent_xml(self.identifier)
        xml_obj = objectify.fromstring(xml)
        del xml_obj.agentName

        with pytest.raises(Exception) as e:
            presentation.premisAgentXMLToObject(etree.tostring(xml_obj))

        expected_message = "Unable to set 'agent_name'"
        assert expected_message in str(e), 'The exception messages matches'

    def test_sets_agent_note(self):
        xml = self.agent_xml(self.identifier)
        agent = presentation.premisAgentXMLToObject(xml)
        xml_obj = objectify.fromstring(xml)
        assert agent.agent_note == xml_obj.agentNote

    def test_exception_not_raised_when_agent_note_is_missing(self):
        xml = self.agent_xml(self.identifier)
        xml_obj = objectify.fromstring(xml)
        del xml_obj.agentNote
        presentation.premisAgentXMLToObject(etree.tostring(xml_obj))
        # No assertions here. We only want to make sure that no exceptions
        # were raised.
