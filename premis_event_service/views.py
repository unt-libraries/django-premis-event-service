from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator
from django.template.context import RequestContext
from django.utils import simplejson
from django.contrib.sites.models import Site
from coda import bagindexer
from coda.bagatom import makeObjectFeed, addObjectFromXML, \
    updateObjectFromXML, wrapAtom, makeServiceDocXML
from presentation import premisEventXMLToObject, premisEventXMLgetObject, \
    premisAgentXMLToObject, objectToPremisEventXML, objectToPremisAgentXML, \
    objectToAgentXML, translateDict
from lxml import etree
from datetime import datetime
from .models import Event, Agent, AGENT_TYPE_CHOICES
import uuid
import re
import urllib
import datetime
from premis_event.forms import EventSearchForm

MAINTENANCE_MSG = settings.MAINTENANCE_MSG
EVENT_UPDATE_TRANSLATION_DICT = translateDict
ISO8601Pattern = r"(?P<year>\d\d\d\d)(-(?P<month>\d\d)(-(?P<day>\d\d))?)?(T\
(?P<hour>\d\d):(?P<minute>\d\d)(:(?P<second>\d\d)(\.(?P<microsecond>\d+))?)?)?\
(?P<timezone>Z|((\+|-)\d\d:\d\d))?"
dateReg = re.compile(ISO8601Pattern)
ARK_ID_REGEX = re.compile(r'ark:/67531/\w.*')
TYPE_LIST = Event.objects.order_by().values_list(
    'event_type', flat=True
).distinct()
OUTCOME_LIST = Event.objects.order_by().values_list(
    'event_outcome', flat=True
).distinct()
AGENT_LIST = Event.objects.order_by().values_list(
    'linking_agent_identifier_value', flat=True
).distinct()
XML_HEADER = "<?xml version=\"1.0\"?>\n%s"


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
    resp = HttpResponse(serviceXMLText, mimetype="application/atom+xml")
    return resp


def humanEvent(request, identifier=None):
    """
    Return a human readable event, or list of events
    """

    event_object = get_object_or_404(Event, event_identifier=identifier)
    return render_to_response(
        'premis_event/event.html',
        {
            'site_title': Site.objects.get_current().name,
            'record': event_object,
            'maintenance_message': MAINTENANCE_MSG,
        },
        context_instance=RequestContext(request)
    )


def paginate_entries(request, entries, num_per_page=20):
    """
    paginates a set of entries (set of model objects)
    """

    # create paginator from result set
    paginator = Paginator(entries, num_per_page)
    paginated_entries = None
    # try to resolve the current page
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        paginated_entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        paginated_entries = paginator.page(paginator.num_pages)
    # send back the paginated entries
    return paginated_entries


def event_search(request):
    """
    Return a human readable list of search results
    """

    events = Event.objects.all()
    DATE_FORMAT = "%m/%d/%Y"
    start_date = '01/01/1999'
    end_date = '12/31/2999'
    linking_object_id = ''
    outcome = ''
    event_type = ''
    # make initial dict for persistent form fields
    initial = {}
    # parse the request get variables and filter the search
    if request.GET.get('start_date'):
        start_date = datetime.datetime.strptime(
            request.GET.get('start_date').strip(), DATE_FORMAT
        )
        events = events.filter(event_date_time__gte=start_date)
        initial.setdefault('start_date', start_date.strftime(DATE_FORMAT))
    if request.GET.get('end_date'):
        end_date = datetime.datetime.strptime(
            request.GET.get('end_date').strip(), DATE_FORMAT
        )
        events = events.filter(event_date_time__lte=end_date)
        initial.setdefault('end_date', end_date.strftime(DATE_FORMAT))
    if request.GET.get('linked_object_id'):
        linking_object_id = request.GET.get('linked_object_id').strip()
        if ARK_ID_REGEX.match(linking_object_id):
            events = events.filter(
                linking_objects__object_identifier=linking_object_id
            )
        elif ARK_ID_REGEX.match("ark:/67531/%s" % linking_object_id):
            linking_object_id = "ark:/67531/%s" % linking_object_id
            events = events.filter(
                linking_objects__object_identifier=linking_object_id
            )
        else:
            pass
        initial.setdefault('linked_object_id', linking_object_id)
    if request.GET.get('outcome'):
        outcome = request.GET.get('outcome').strip()
        events = events.filter(event_outcome=outcome)
        initial.setdefault('outcome', outcome)
    if request.GET.get('event_type'):
        event_type = request.GET.get('event_type').strip()
        events = events.filter(event_type=str(event_type))
        initial.setdefault('event_type', event_type)
    # sort events by date
    events = events.order_by('-event_date_time')
    # paginate 20 per page
    paginated_entries = paginate_entries(request, events, num_per_page=20)
    # render to the template
    return render_to_response(
        'premis_event/search.html',
        {
            'search_form': EventSearchForm(initial=initial),
            'site_title': Site.objects.get_current().name,
            'linking_object_id': linking_object_id,
            'start_date': start_date,
            'end_date': end_date,
            'event_type': event_type,
            'outcome': outcome,
            'type_list': TYPE_LIST,
            'outcome_list': OUTCOME_LIST,
            'agent_list': AGENT_LIST,
            'entries': paginated_entries,
            'maintenance_message': MAINTENANCE_MSG,
        },
        context_instance=RequestContext(request),
    )


def json_event_search(request):
    """
    returns json search results for premis events
    """

    events = Event.objects.all()
    DATE_FORMAT = "%m/%d/%Y"
    args = {}
    # get data for json dictionary
    if request.GET.get('start_date'):
        args['start_date'] = datetime.datetime.strptime(
            request.GET.get('start_date').strip(), DATE_FORMAT
        )
        events = events.filter(event_date_time__gte=args['start_date'])
    if request.GET.get('end_date'):
        args['end_date'] = datetime.datetime.strptime(
            request.GET.get('end_date').strip(), DATE_FORMAT
        )
        events = events.filter(event_date_time__lte=args['end_date'])
    if request.GET.get('link_object_id'):
        args['linking_object_id'] = request.GET.get('link_object_id').strip()
        if ARK_ID_REGEX.match(args['linking_object_id']):
            events = events.filter(
                linking_objects__object_identifier=args['linking_object_id']
            )
        elif ARK_ID_REGEX.match("ark:/67531/%s" % linking_object_id):
            args['linking_object_id'] = "ark:/67531/%s" % linking_object_id
            events = events.filter(
                linking_objects__object_identifier=args['linking_object_id']
            )
    if request.GET.get('outcome'):
        args['outcome'] = request.GET.get('outcome').strip()
        events = events.filter(event_outcome=args['outcome'])
    if request.GET.get('type'):
        args['event_type'] = request.GET.get('type').strip()
        events = events.filter(event_type=args['event_type'])
    # make a results list to pass to the view
    event_json = []
    if events.count() is not 0:
        # paginate 20 per page
        paginated_entries = paginate_entries(request, events, num_per_page=20)
        # prepare a results set and then append each event to it as a dict
        event_url_prefix = "%s/event/search.json" % \
            request.META.get('HTTP_HOST')
        rel_links = []
        entries = []
        cur_page = paginated_entries.number
        # we will ALWAYS have a self, first and last relative link
        args['page'] = paginated_entries.number
        current_page_args = args.copy()
        args['page'] = 1
        first_page_args = args.copy()
        args['page'] = paginated_entries.paginator.num_pages
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
        if paginated_entries.number > 1:
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
        if paginated_entries.number < paginated_entries.paginator.num_pages:
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
        for entry in paginated_entries.object_list:
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
                "opensearch:itemsPerPage": paginated_entries.\
                    paginator.per_page,
                "opensearch:startIndex": "1",
                "opensearch:totalResults": events.count(),
                "title": "Premis Event Search"
            }
        }
    response = HttpResponse(mimetype='application/json')
    simplejson.dump(
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

    events = Event.objects.all().order_by('-event_date_time')[:10]
    # render to the template
    return render_to_response(
        'premis_event/recent_event_list.html',
        {
            'site_title': Site.objects.get_current().name,
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
    response = HttpResponse(mimetype='application/json')
    # construct the dictionary with values from aggregates
    jsonDict = {
        'id': request.META.get('HTTP_REFERER'),
        'type': [c for c in AGENT_TYPE_CHOICES if c[0] == a.agent_type][0][1],
        'name': a.agent_name,
        'note': a.agent_note,
    }
    # dump to response
    simplejson.dump(
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
    else:
        agents = Agent.objects.all().values()
    for a in agents:
        a['agent_type'] = [
            tup for tup in AGENT_TYPE_CHOICES if tup[0] == a['agent_type']
        ][0][0]
    return render_to_response(
        'premis_event/agent.html',
        {
            'site_title': Site.objects.get_current().name,
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
    atomXML = wrapAtom(
        eventXML, lateEvent.event_identifier, lateEvent.event_identifier
    )
    atomText = XML_HEADER % etree.tostring(atomXML, pretty_print=True)
    resp = HttpResponse(atomText, mimetype="application/atom+xml")
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
            webRoot=request.META['HTTP_HOST'] + '/',
        )
        returnText = XML_HEADER % etree.tostring(returnXML, pretty_print=True)
    else:
        try:
            agentObject = Agent.objects.get(agent_identifier=identifier)
        except Agent.DoesNotExist:
            return HttpResponseNotFound(
                "There is no agent with the identifier %s" % identifier
            )
        returnXML = objectToAgentXML(agentObject)
        returnText = XML_HEADER % etree.tostring(returnXML, pretty_print=True)
    return HttpResponse(returnText, mimetype="application/atom+xml")


def app_event(request, identifier=None):
    """
    This method handles the ATOMpub protocol for events
    """

    returnEvent = None
    # are we POSTing a new identifier here?
    if request.method == 'POST' and not identifier:
        xmlDoc = etree.fromstring(request.raw_post_data)
        newEvent = addObjectFromXML(
            xmlDoc, premisEventXMLToObject, "event", "event_identifier",
            EVENT_UPDATE_TRANSLATION_DICT
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
        resp = HttpResponse(atomText, mimetype="application/atom+xml")
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
        startTime = datetime.datetime.now()
        # parse the request get variables and filter the search
        if request.GET.get('start_date'):
            start_date = datetime.datetime.strptime(
                request.GET.get('start_date'),
                DATE_FORMAT
            )
            events = events.filter(event_date_time__gte=start_date)
        if request.GET.get('end_date'):
            end_date = datetime.datetime.strptime(
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
            if request.GET.get('orderdir'):
                if request.GET.get('orderdir') == 'descending':
                    events = events.order_by(order_field).reverse()
                else:
                    events = events.order_by(order_field)
            else:
                events = events.order_by(order_field)
        debug_list = []
        endTime = datetime.datetime.now()
        requestString = request.path
        if request.GET:
            requestString = "%s?%s" % (request.path, request.GET.urlencode())
            page = int(request.GET['page']) if request.GET.get('page') else 1
        else:
            page = 1
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
        comment = etree.Comment(\
            "\n".join(debug_list) + \
            "\nTime prior to filtering is %s, time after filtering is %s" % \
            (startTime, endTime)
        )
        atomFeed.append(comment)
        atomFeedText = XML_HEADER % etree.tostring(atomFeed, pretty_print=True)
        resp = HttpResponse(atomFeedText, mimetype="application/atom+xml")
        resp.status_code = 200
        return resp
    # updating an existing record
    elif request.method == 'PUT' and identifier:
        xmlDoc = etree.fromstring(request.raw_post_data)
        updatedEvent = updateObjectFromXML(
            xmlObject=xmlDoc,
            XMLToObjectFunc=premisEventXMLgetObject,
            topLevelName="event",
            idKey="event_identifier",
            updateList=EVENT_UPDATE_TRANSLATION_DICT,
        )
        returnEvent = updatedEvent
        updatedEvent.save()
        eventObjectXML = objectToPremisEventXML(returnEvent)
        atomXML = wrapAtom(eventObjectXML, identifier, identifier)
        atomText = XML_HEADER % etree.tostring(atomXML, pretty_print=True)
        resp = HttpResponse(atomText, mimetype="application/atom+xml")
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
        atomXML = wrapAtom(
            xml=eventObjectXML,
            id='http://%s/APP/event/%s/' % (
                request.META['HTTP_HOST'], identifier
            ),
            title=identifier,
        )
        atomText = XML_HEADER % etree.tostring(atomXML, pretty_print=True)
        resp = HttpResponse(atomText, mimetype="application/atom+xml")
        resp.status_code = 200
        return resp
    elif request.method == 'DELETE' and identifier:
    # attempt to retrieve record -- error if unable
        try:
            event_object = Event.objects.get(event_identifier=identifier)
        except:
            return HttpResponseNotFound(
                "Unable to Delete. There is no event for identifier %s.\n" \
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
        resp = HttpResponse(atomText, mimetype="application/atom+xml")
        resp.status_code = 200
        return resp


def app_agent(request, identifier=None):
    """
    Return a representation of a given agent
    """

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
            atomFeedText = XML_HEADER % etree.tostring(
                atomFeed, pretty_print=True
            )
            resp = HttpResponse(atomFeedText, mimetype="application/atom+xml")
            resp.status_code = 200
            return resp
        elif request.method == 'POST':
            agent_object = premisAgentXMLToObject(request.raw_post_data)
            agent_object.save()
            returnXML = objectToAgentXML(agent_object)
            returnEntry = bagindexer.wrapAtom(
                returnXML,
                agent_object.agent_name,
                agent_object.agent_name
            )
            entryText = XML_HEADER % etree.tostring(
                returnEntry,
                pretty_print=True
            )
            resp = HttpResponse(entryText, mimetype="application/atom+xml")
            resp.status_code = 201
            resp['Location'] = agent_object.agent_identifier + '/'
            return resp
        else:
            return HttpResponseBadRequest("Invalid method for this URL.")
    # identifier supplied, will be a GET or DELETE
    else:
        try:
            agent_object = get_object_or_404(
                Agent,
                agent_identifier=identifier
            )
        except Exception, e:
            return HttpResponseNotFound(
                "There is no agent for identifier \'%s\'.\n" % identifier
            )
        if request.method == 'DELETE':
            agent_object.delete()
            resp = HttpResponse("Deleted %s.\n" % identifier)
            resp.status_code = 200
            return resp
        elif request.method == 'PUT':
            agent_object = premisAgentXMLToObject(request.raw_post_data)
            agent_object.save()
            returnXML = objectToAgentXML(agent_object)
            returnEntry = bagindexer.wrapAtom(
                returnXML, agent_object.agent_name, agent_object.agent_name
            )
            entryText = XML_HEADER % etree.tostring(
                returnEntry,
                pretty_print=True
            )
            resp = HttpResponse(entryText, mimetype="application/atom+xml")
            resp.status_code = 200
            return resp
        elif request.method == 'GET':
            returnXML = objectToAgentXML(agent_object)
            returnText = XML_HEADER % etree.tostring(
                returnXML,
                pretty_print=True
            )
            resp = HttpResponse(returnText, mimetype="application/atom+xml")
            resp.status_code = 200
            return resp
