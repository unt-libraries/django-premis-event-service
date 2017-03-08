import re
import math
from datetime import datetime
import json
import urllib

from lxml import etree
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import FieldError
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound)
from django.db.utils import IntegrityError
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template.context import RequestContext

from codalib import APP_AUTHOR as CODALIB_APP_AUTHOR
from codalib.bagatom import (makeObjectFeed, addObjectFromXML,
                             updateObjectFromXML, wrapAtom, makeServiceDocXML,)
from codalib.xsdatetime import xsDateTime_parse
from .forms import EventSearchForm
from .models import Event, Agent, AGENT_TYPE_CHOICES
from .presentation import (premisEventXMLToObject, premisEventXMLgetObject,
                           premisAgentXMLToObject, premisAgentXMLgetObject,
                           objectToPremisEventXML, objectToPremisAgentXML,
                           objectToAgentXML, translateDict, DuplicateEventError,
                           PREMIS_NSMAP)
from settings import ARK_NAAN

ARK_ID_REGEX = re.compile(r'ark:/'+str(ARK_NAAN)+r'/\w.*')
MAINTENANCE_MSG = settings.MAINTENANCE_MSG
EVENT_UPDATE_TRANSLATION_DICT = translateDict
XML_HEADER = "<?xml version=\"1.0\"?>\n%s"


def get_request_body(request):
    """Get a request's body (POST data). Works with all Django versions."""
    return getattr(request, 'body', getattr(request, 'raw_post_data', ''))


def app(request):
    """
    Return the AtomPub service document
    """

    collections = [
        {
            "title": "node",
            "href": "http://%s/APP/node/" % request.META.get('HTTP_HOST'),
            "accept": "application/atom+xml;type=entry"
        },
        {
            "title": "bag",
            "href": "http://%s/APP/bag/" % request.META.get('HTTP_HOST'),
            "accept": "application/atom+xml;type=entry"
        },
        {
            "title": "event",
            "href": "http://%s/APP/event/" % request.META.get('HTTP_HOST'),
            "accept": "application/atom+xml;type=entry"
        },
        {
            "title": "agent",
            "href": "http://%s/APP/agent/" % request.META.get('HTTP_HOST'),
            "accept": "application/atom+xml;type=entry"
        },
        {
            "title": "queue",
            "href": "http://%s/APP/queue/" % request.META.get('HTTP_HOST'),
            "accept": "application/atom+xml;type=entry"
        },
    ]
    serviceXML = makeServiceDocXML(
        "Atom Publishing Protocol (APP) Interface",
        collections
    )
    serviceXMLText = XML_HEADER % etree.tostring(serviceXML, pretty_print=True)
    resp = HttpResponse(serviceXMLText, content_type="application/atom+xml")
    return resp


def humanEvent(request, identifier=None):
    """
    Return a human readable event, or list of events
    """

    event_object = get_object_or_404(Event, event_identifier=identifier)
    return render_to_response(
        'premis_event_service/event.html',
        {
            'record': event_object,
            'maintenance_message': MAINTENANCE_MSG,
        },
        context_instance=RequestContext(request)
    )


def last_page_ordinal(query_set, per_page=20):
    qa = query_set.order_by('ordinal')[0:20]
    return qa.last().ordinal


def paginate_events(valid, request, per_page=20):
    total_events = None
    events = None
    page = int(request.GET.get('page', 1))
    offset = None
    unfiltered = True
    # This is an assumption that will not hold if events
    # are delete from the db. But this doesn't seem to
    # happen in practice.
    last_page_ord = per_page+1
    if any([v for k, v in valid.items() if k != 'min_ordinal']):
        events = (Event.objects.search(**valid)
                  .prefetch_related('linking_objects'))
        total_events = events.count()
        offset = (page-1) * per_page
        last_page_ord = last_page_ordinal(events)
        # The min_ordinal is actually the "bottom" (end) of the current
        # page and the top (start) of the next. This is because the
        # ordinal is autoincrementing and acts as a proxy for
        # date added, so we're paging from greatest to least.
        if 'min_ordinal' in valid and valid['min_ordinal']:
            events = events.filter(ordinal__lte=valid['min_ordinal'])[:20]
        else:
            events = events[offset:offset+per_page]
        unfiltered = False
    else:
        events = Event.objects.searchunfilt(request.GET.get('min_ordinal'))
        total_events = Event.objects.all().count()
        events = events.prefetch_related('linking_objects')[0:per_page]
    page_max_ord = 0
    page_min_ord = 0
    if events:
        page_max_ord = max([e.ordinal for e in events])
        page_min_ord = min([e.ordinal for e in events])
    max_page = int(math.ceil(total_events/float(per_page)))
    if page > max_page and page > 1:
        raise EmptyPage()
    page_range = range(
        max(1, page-6),
        min(max_page, page+7)
    )
    if unfiltered:
        page_offsets = [(p, page_min_ord-(per_page*(p-page-1))) for p in page_range]
    else:
        # We don't know (or at least can't really guess) the ordinals for unfiltered
        # searches. Set these to empty strings.
        page_offsets = [(p, '') for p in page_range]
    context = {
        'events': events, 'page_range': page_range, 'page_offsets': page_offsets,
        'page_max_ordinal': page_max_ord, 'page_min_ordinal': page_min_ord,
        'last_page_ordinal': last_page_ord, 'page': page, 'max_page': max_page,
        'per_page': per_page, 'next_page': page+1, 'previous_page': page-1
    }
    return context


def event_search(request):
    """Return a human readable list of search results."""
    form = EventSearchForm(request.GET)
    valid = form.cleaned_data if form.is_valid() else {}
    pagination_context = paginate_events(valid, request, 20)
    context = {'search_form': form}
    context.update(pagination_context)
    return render(request, 'premis_event_service/search.html', context)


def json_event_search(request):
    """
    returns json search results for premis events
    """
    args = {}
    form = EventSearchForm(request.GET)
    if form.is_valid():
        valid = form.cleaned_data
    else:
        errors = []
        for field, field_errors in form.errors.as_data().items():
            errors.append('%s:' % field)
            for field_error in field_errors:
                message = field_error.message % field_error.params
                errors.append('\t%s: %s' % (field_error.code, message))
        errors = '\n'.join(errors)
        return HttpResponse(
            'Invalid parameters.\n'+errors,
            status=400,
            content_type="text/plain"
        )
    # make a results list to pass to the view
    event_json = []
    # paginate 20 per page
    paginated_entries = paginate_events(valid, request, per_page=20)
    events = paginated_entries['events']
    total_events = Event.objects.all().count()
    if events.count() is not 0:
        # prepare a results set and then append each event to it as a dict
        rel_links = []
        entries = []
        # we will ALWAYS have a self, first and last relative link
        args['page'] = paginated_entries['page']
        current_page_args = args.copy()
        args['page'] = 1
        first_page_args = args.copy()
        args['page'] = paginated_entries['max_page']
        last_page_args = args.copy()
        # store links for adjacent events relative to the current event
        rel_links.extend(
            [
                {
                    'rel': 'self',
                    'href': "http://%s%s?%s" % (
                        request.META.get('HTTP_HOST'),
                        request.path,
                        urllib.urlencode(current_page_args)
                    )
                },
                {
                    'rel': 'first',
                    'href': "http://%s%s?%s" % (
                        request.META.get('HTTP_HOST'),
                        request.path,
                        urllib.urlencode(first_page_args)
                    )
                },
                {
                    'rel': 'last',
                    'href': "http://%s%s?%s" % (
                        request.META.get('HTTP_HOST'),
                        request.path,
                        urllib.urlencode(last_page_args)
                    )
                },
            ]
        )
        # if we are past the first event, we can always add a previous event
        if paginated_entries['page'] > 1:
            args['page'] = current_page_args['page'] - 1
            rel_links.append(
                {
                    'rel': 'previous',
                    'href': "http://%s%s?%s" % (
                        request.META.get('HTTP_HOST'),
                        request.path,
                        urllib.urlencode(args)
                    )
                },
            )
        # if our event is not the last in the list, we can add a next event
        if paginated_entries['page'] < paginated_entries['max_page']:
            args['page'] = current_page_args['page'] + 1
            rel_links.append(
                {
                    'rel': 'next',
                    'href': "http://%s%s?%s" % (
                        request.META.get('HTTP_HOST'),
                        request.path,
                        urllib.urlencode(args)
                    )
                },
            )
        for entry in events:
            linked_objects = ", ".join(
                entry.linking_objects.values_list(
                    'object_identifier',
                    flat=True
                )
            )
            entries.extend(
                [
                    {
                        'linked_objects': linked_objects,
                        'identifier': entry.event_identifier,
                        'event_type': entry.event_type,
                        'outcome': entry.event_outcome,
                        'date': str(entry.event_date_time),
                    },
                ],
            )
        event_json = {
            'feed': {
                'entry': entries,
                'link': rel_links,
                'opensearch:Query': request.GET,
                "opensearch:itemsPerPage":
                    paginated_entries['per_page'],
                "opensearch:startIndex": "1",
                "opensearch:totalResults": total_events,
                "title": "Premis Event Search"
            }
        }
    response = HttpResponse(content_type='application/json')
    json.dump(
        event_json,
        fp=response,
        indent=4,
        sort_keys=True,
    )
    return response


def recent_event_list(request):
    """
    Return a tabled list of 10 most recent events
    """

    events = (Event.objects
                   .all()
                   .prefetch_related('linking_objects')
                   .order_by('-event_date_time')[:10])

    # render to the template
    return render_to_response(
        'premis_event_service/recent_event_list.html',
        {
            'entries': events,
            'num_events': Event.objects.count(),
            'maintenance_message': MAINTENANCE_MSG,
        },
        context_instance=RequestContext(request),
    )


def json_agent(request, identifier=None):
    """
    returns a consumable json for robots with some basic info
    """

    # get data for json dictionary
    a = get_object_or_404(Agent, agent_identifier=identifier)
    # dump the dict to as an HttpResponse
    response = HttpResponse(content_type='application/json')
    # construct the dictionary with values from aggregates
    jsonDict = {
        'id': "http://%s%s" % (request.get_host(), a.get_absolute_url()),
        'type': [c for c in AGENT_TYPE_CHOICES if c[0] == a.agent_type][0][1],
        'name': a.agent_name,
        'note': a.agent_note,
    }
    # dump to response
    json.dump(
        jsonDict,
        fp=response,
        indent=4,
        sort_keys=True,
    )
    return response


def humanAgent(request, identifier=None):
    """
    Return a human readable list of agests
    """

    if identifier:
        agents = Agent.objects.filter(agent_identifier=identifier).values()
        if not agents:
            return HttpResponseNotFound("Agent not found.", content_type='text/plain')
    else:
        agents = Agent.objects.all().values()
    for a in agents:
        a['agent_type'] = [
            tup for tup in AGENT_TYPE_CHOICES if tup[0] == a['agent_type']
        ][0][0]
    return render_to_response(
        'premis_event_service/agent.html',
        {
            'agents': agents,
            'num_agents': Agent.objects.count(),
            'maintenance_message': MAINTENANCE_MSG,
        },
        context_instance=RequestContext(request),
    )


def eventXML(request, identifier=None):
    return HttpResponse(
        "So you would like XML for the event with identifier %s?" % identifier
    )


def findEvent(request, linked_identifier, event_type=None):
    resultSet = Event.objects.filter(
        linking_objects__object_identifier__contains=linked_identifier
    )
    if event_type:
        resultSet = resultSet.filter(event_type__contains=event_type)
    if not resultSet.count():
        return HttpResponseNotFound(
            "There is no event for matching those parameters"
        )
    lateDate = resultSet[0].event_date_time
    lateEvent = resultSet[0]
    for singleEvent in resultSet:
        if singleEvent.event_date_time > lateDate:
            lateDate = singleEvent.event_date_time
            lateEvent = singleEvent
    eventXML = objectToPremisEventXML(lateEvent)
    althref = request.build_absolute_uri(
        reverse('event-detail', args=[lateEvent.event_identifier, ])
    )
    atomXML = wrapAtom(
        eventXML, lateEvent.event_identifier, lateEvent.event_identifier,
        alt=althref
    )
    atomText = XML_HEADER % etree.tostring(atomXML, pretty_print=True)
    resp = HttpResponse(atomText, content_type="application/atom+xml")
    return resp


def agentXML(request, identifier):
    """
    Return a representation of a given agent
    """

    if 'premis' in request.path:
        identifier = identifier.replace('.premis', '')
        try:
            agentObject = Agent.objects.get(agent_identifier=identifier)
        except Agent.DoesNotExist:
            return HttpResponseNotFound(
                "There is no agent with the identifier %s" % identifier
            )
        returnXML = objectToPremisAgentXML(
            agentObject,
            webRoot=request.get_host() + '/',
        )
        returnText = XML_HEADER % etree.tostring(returnXML, pretty_print=True)
        content_type = "application/xml"
    else:
        try:
            agentObject = Agent.objects.get(agent_identifier=identifier)
        except Agent.DoesNotExist:
            return HttpResponseNotFound(
                "There is no agent with the identifier %s" % identifier
            )
        agent_obj_xml = objectToAgentXML(agentObject)
        althref = request.build_absolute_uri(
            reverse('agent-detail', args=[identifier, ])
        )
        return_atom = wrapAtom(
            agent_obj_xml, identifier, identifier,
            alt=althref
        )
        returnText = XML_HEADER % etree.tostring(return_atom, pretty_print=True)
        content_type = "application/atom+xml"
    return HttpResponse(returnText, content_type=content_type)


def app_event(request, identifier=None):
    """
    This method handles the ATOMpub protocol for events
    """
    DATE_FORMAT = "%m/%d/%Y"
    returnEvent = None
    request_body = get_request_body(request)
    # are we POSTing a new identifier here?
    if request.method == 'POST' and not identifier:
        xmlDoc = etree.fromstring(request_body)
        try:
            newEvent = addObjectFromXML(
                xmlDoc, premisEventXMLToObject, "event", "event_identifier",
                EVENT_UPDATE_TRANSLATION_DICT
            )
        except DuplicateEventError as e:
            return HttpResponse(
                "An event with id='{}' exists.".format(e.message),
                status=409, content_type="text/plain"
            )
        if type(newEvent) == HttpResponse:
            return newEvent
        eventObjectXML = objectToPremisEventXML(newEvent)
        atomXML = wrapAtom(
            xml=eventObjectXML,
            id='http://%s/APP/event/%s/' % (
                request.META['HTTP_HOST'],
                newEvent.event_identifier
            ),
            title=newEvent.event_identifier,
        )
        atomText = XML_HEADER % etree.tostring(atomXML, pretty_print=True)
        resp = HttpResponse(atomText, content_type="application/atom+xml")
        resp.status_code = 201
        resp['Location'] = 'http://%s/APP/event/%s/' % (
            request.META['HTTP_HOST'],
            newEvent.event_identifier
        )
        return resp
    # if not, return a feed
    elif request.method == 'GET' and not identifier:
        # negotiate the details of our feed here
        events = Event.objects.all()
        startTime = datetime.now()
        # parse the request get variables and filter the search
        if request.GET.get('start_date'):
            start_date = datetime.strptime(
                request.GET.get('start_date'),
                DATE_FORMAT
            )
            events = events.filter(event_date_time__gte=start_date)
        if request.GET.get('end_date'):
            end_date = datetime.strptime(
                request.GET.get('end_date'),
                DATE_FORMAT
            )
            events = events.filter(event_date_time__lte=end_date)
        if request.GET.get('link_object_id'):
            linking_object_id = request.GET.get('link_object_id')
            events = events.filter(
                linking_objects__object_identifier=linking_object_id
            )
        if request.GET.get('outcome'):
            outcome = request.GET.get('outcome')
            events = events.filter(event_outcome=outcome)
        if request.GET.get('type'):
            event_type = request.GET.get('type')
            events = events.filter(event_type=event_type)
        if request.GET.get('orderby'):
            order_field = request.GET.get('orderby')
            unordered_events = events
            if request.GET.get('orderdir'):
                if request.GET.get('orderdir') == 'descending':
                    events = events.order_by(order_field).reverse()
                else:
                    events = events.order_by(order_field)
            else:
                events = events.order_by(order_field)
            try:
                # Trigger QuerySet eval.
                if events:
                    pass
            except FieldError:
                # If order_by fails, revert to natural order.
                events = unordered_events
        debug_list = []
        endTime = datetime.now()
        if request.GET:
            page = int(request.GET['page']) if request.GET.get('page') else 1
        else:
            page = 1
        try:
            atomFeed = makeObjectFeed(
                paginator=Paginator(events, 20),
                objectToXMLFunction=objectToPremisEventXML,
                feedId=request.path[1:],
                webRoot='http://%s' % request.META.get('HTTP_HOST'),
                title="Event Entry Feed",
                idAttr="event_identifier",
                nameAttr="event_identifier",
                dateAttr="event_date_time",
                request=request,
                page=page,
            )
        except EmptyPage:
            return HttpResponse(
                "That page does not exist.\n",
                status=400,
                content_type='text/plain'
            )
        comment = etree.Comment(
            "\n".join(debug_list) +
            "\nTime prior to filtering is %s, time after filtering is %s" %
            (startTime, endTime)
        )
        atomFeed.append(comment)
        atomFeedText = XML_HEADER % etree.tostring(atomFeed, pretty_print=True)
        resp = HttpResponse(atomFeedText, content_type="application/atom+xml")
        resp.status_code = 200
        return resp
    # updating an existing record
    elif request.method == 'PUT' and identifier:
        try:
            xmlDoc = etree.fromstring(request_body)
            xmlDoc = xmlDoc.xpath('//premis:event', namespaces=PREMIS_NSMAP)[0]
        except etree.LxmlError:
            return HttpResponse(
                'Invalid request XML.',
                content_type='text/plain',
                status=400
            )
        except IndexError:
            return HttpResponse(
                'Event element missing in request body.',
                content_type='text/plain',
                status=400
            )
        updatedEvent = updateObjectFromXML(
            xmlObject=xmlDoc,
            XMLToObjectFunc=premisEventXMLgetObject,
            topLevelName="event",
            idKey="event_identifier",
            updateList=EVENT_UPDATE_TRANSLATION_DICT,
        )
        # If XML identifier and resource ID don't match, bail.
        if updatedEvent.event_identifier != identifier:
            return HttpResponse(
                'URI-identifier mismatch ("{}" != "{}")'.format(
                    updatedEvent.event_identifier, identifier
                ),
                content_type='text/plain',
                status=400
            )
        updatedEvent.event_date_time = xsDateTime_parse(
            updatedEvent.event_date_time
        )
        returnEvent = updatedEvent
        updatedEvent.save()
        eventObjectXML = objectToPremisEventXML(returnEvent)
        atomXML = wrapAtom(eventObjectXML, identifier, identifier)
        atomText = XML_HEADER % etree.tostring(atomXML, pretty_print=True)
        resp = HttpResponse(atomText, content_type="application/atom+xml")
        resp.status_code = 200
        return resp
    if request.method == 'GET' and identifier:
        # attempt to retrieve record -- error if unable
        try:
            event_object = Event.objects.get(event_identifier=identifier)
        except Event.DoesNotExist:
            return HttpResponseNotFound(
                "There is no event for identifier %s.\n" % identifier
            )
        returnEvent = event_object
        eventObjectXML = objectToPremisEventXML(returnEvent)
        althref = request.build_absolute_uri(
            reverse('event-detail', args=[identifier, ])
        )
        atomXML = wrapAtom(
            xml=eventObjectXML,
            id='http://%s/APP/event/%s/' % (
                request.META['HTTP_HOST'], identifier
            ),
            title=identifier,
            alt=althref,
            updated=event_object.event_added,
            author=CODALIB_APP_AUTHOR["name"],
            author_uri=CODALIB_APP_AUTHOR["uri"]
        )
        atomText = XML_HEADER % etree.tostring(atomXML, pretty_print=True)
        resp = HttpResponse(atomText, content_type="application/atom+xml")
        resp.status_code = 200
        return resp
    # This is here so clients can ping this endpoint to
    # test for availability. See codalib's waitForURL func
    # in util.py.
    elif request.method == 'HEAD':
        return HttpResponse(content_type="application/atom+xml")

    elif request.method == 'DELETE' and identifier:
        # attempt to retrieve record -- error if unable
        try:
            event_object = Event.objects.get(event_identifier=identifier)
        except:
            return HttpResponseNotFound(
                "Unable to Delete. There is no event for identifier %s.\n"
                % identifier
            )
        # grab the event, delete it, and inform the user.
        returnEvent = event_object
        eventObjectXML = objectToPremisEventXML(returnEvent)
        event_object.delete()
        atomXML = wrapAtom(
            xml=eventObjectXML,
            id='http://%s/APP/event/%s/' % (
                request.META['HTTP_HOST'], identifier
            ),
            title=identifier,
        )
        atomText = XML_HEADER % etree.tostring(atomXML, pretty_print=True)
        resp = HttpResponse(atomText, content_type="application/atom+xml")
        resp.status_code = 200
        return resp


def app_agent(request, identifier=None):
    """
    Return a representation of a given agent
    """

    request_body = get_request_body(request)
    # full paginated ATOM PUB FEED
    if not identifier:
        # we just want to look at it.
        if request.method == 'GET':
            requestString = request.path
            if len(request.GET):
                requestString = "%s?%s" % (
                    request.path, request.GET.urlencode()
                )
                page = request.GET.get('page')
            else:
                page = 1
            try:
                atomFeed = makeObjectFeed(
                    paginator=Paginator(Agent.objects.all(), 20),
                    objectToXMLFunction=objectToAgentXML,
                    feedId=requestString[1:],
                    webRoot="http://%s" % request.META.get('HTTP_HOST'),
                    title="Agent Entry Feed",
                    idAttr="agent_identifier",
                    nameAttr="agent_name",
                    request=request,
                    page=page,
                )
            except EmptyPage:
                return HttpResponse(
                    "That page doesn't exist.\n", status=400,
                    content_type='text/plain'
                )
            atomFeedText = XML_HEADER % etree.tostring(
                atomFeed, pretty_print=True
            )
            resp = HttpResponse(atomFeedText, content_type="application/atom+xml")
            resp.status_code = 200
            return resp
        elif request.method == 'POST':
            entry_etree = etree.XML(request_body)
            try:
                agent_object = premisAgentXMLgetObject(entry_etree)
            except:
                pass
            else:
                return HttpResponse(
                    "Conflict with already-existing resource.\n",
                    status=409, content_type="text/plain"
                )
            try:
                agent_object = premisAgentXMLToObject(request_body)
            except etree.XMLSyntaxError:
                return HttpResponse(
                    "Invalid XML in request body.\n",
                    status=400, content_type="text/plain"
                )
            try:
                agent_object.save()
            except IntegrityError:
                return HttpResponse(
                    "Conflict with already-existing resource.\n",
                    status=409, content_type="text/plain"
                )
            returnXML = objectToAgentXML(agent_object)
            returnEntry = wrapAtom(
                returnXML,
                agent_object.agent_name,
                agent_object.agent_name
            )
            entryText = XML_HEADER % etree.tostring(
                returnEntry,
                pretty_print=True
            )
            resp = HttpResponse(entryText, content_type="application/atom+xml")
            resp.status_code = 201
            resp['Location'] = agent_object.agent_identifier + '/'
            return resp
        # This is here so clients can ping this endpoint to
        # test for availability. See codalib's waitForURL func
        # in util.py.
        elif request.method == 'HEAD':
            return HttpResponse(content_type="application/atom+xml")
        else:
            return HttpResponseBadRequest("Invalid method for this URL.")
    # identifier supplied, will be a GET or DELETE
    else:
        try:
            agent_object = get_object_or_404(
                Agent,
                agent_identifier=identifier
            )
        except Exception:
            return HttpResponseNotFound(
                "There is no agent for identifier \'%s\'.\n" % identifier
            )
        if request.method == 'DELETE':
            agent_object.delete()
            resp = HttpResponse("Deleted %s.\n" % identifier)
            resp.status_code = 200
            return resp
        elif request.method == 'PUT':
            agent_object = premisAgentXMLToObject(request_body)
            agent_object.save()
            returnXML = objectToAgentXML(agent_object)
            returnEntry = wrapAtom(
                returnXML, agent_object.agent_name, agent_object.agent_name
            )
            entryText = XML_HEADER % etree.tostring(
                returnEntry,
                pretty_print=True
            )
            resp = HttpResponse(entryText, content_type="application/atom+xml")
            resp.status_code = 200
            return resp
        elif request.method == 'GET':
            returnXML = objectToAgentXML(agent_object)
            althref = request.build_absolute_uri(
                reverse('agent-detail', args=(identifier, ))
            )
            returnEntry = wrapAtom(
                returnXML,
                agent_object.agent_name,
                agent_object.agent_name,
                alt=althref,
                author=CODALIB_APP_AUTHOR["name"],
                author_uri=CODALIB_APP_AUTHOR["uri"]
            )
            entryText = XML_HEADER % etree.tostring(
                returnEntry,
                pretty_print=True
            )
            resp = HttpResponse(entryText, content_type="application/atom+xml")
            resp.status_code = 200
            return resp
        # This is here so clients can ping this endpoint to
        # test for availability. See codalib's waitForURL func
        # in util.py.
        elif request.method == 'HEAD':
            return HttpResponse(content_type="application/atom+xml")
