import os
import anvl
import urllib
import xml.sax.saxutils as saxutils
from lxml import etree
from datetime import datetime
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from premis_event_service import settings

TIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"
DATE_FORMAT_STRING = "%Y-%m-%d"
BAG_NAMESPACE = settings.BAGATOM_BAG_NAMESPACE
BAG = "{%s}" % BAG_NAMESPACE
BAG_NSMAP = {"bag": BAG_NAMESPACE}
ATOM_NAMESPACE = "http://www.w3.org/2005/Atom"
ATOM = "{%s}" % ATOM_NAMESPACE
ATOM_NSMAP = {None: ATOM_NAMESPACE}
QXML_NAMESPACE = settings.BAGATOM_QXML_NAMESPACE
QXML = "{%s}" % QXML_NAMESPACE
QXML_NSMAP = {None: QXML_NAMESPACE}
NODE_NAMESPACE = settings.BAGATOM_NODE_NAMESPACE
NODE = "{%s}" % NODE_NAMESPACE
NODE_NSMAP = {"node": NODE_NAMESPACE}


def wrapAtom(xml, id, title, author=None, updated=None):
    """
    Create an Atom entry tag and embed the passed XML within it
    """

    entryTag = etree.Element(ATOM + "entry", nsmap=ATOM_NSMAP)
    titleTag = etree.SubElement(entryTag, ATOM + "title")
    titleTag.text = title
    idTag = etree.SubElement(entryTag, ATOM + "id")
    idTag.text = id
    updatedTag = etree.SubElement(entryTag, ATOM + "updated")
    if updated != None:
        updatedTag.text = updated.strftime(TIME_FORMAT_STRING)
    else:
        updatedTag.text = datetime.utcnow().strftime(TIME_FORMAT_STRING)
    if author:
        authorTag = etree.SubElement(entryTag, ATOM + "author")
        nameTag = etree.SubElement(authorTag, ATOM + "name")
        nameTag.text = author
    contentTag = etree.SubElement(entryTag, ATOM + "content")
    contentTag.set("type", "application/xml")
    contentTag.append(xml)
    return entryTag


def getOxum(dataPath):
    """
    Calculate the oxum for a given path
    """

    fileCount = 0L
    fileSizeTotal = 0L
    for root, dirs, files in os.walk(dataPath):
        for fileName in files:
            fullName = os.path.join(root, fileName)
            stats = os.stat(fullName)
            fileSizeTotal += stats.st_size
            fileCount += 1
    return "%s.%s" % (fileSizeTotal, fileCount)


def getBagTags(bagInfoPath):
    """
    get bag tags
    """

    try:
        bagInfoString = open(bagInfoPath, "r").read().decode('utf-8')
    except UnicodeDecodeError:
        bagInfoString = open(bagInfoPath, "r").read().decode('iso-8859-1')
    bagTags = anvl.readANVLString(bagInfoString)
    return bagTags


def bagToXML(bagPath):
    """
    Given a path to a bag, read stuff about it and make an XML file
    """
    bagInfoPath = os.path.join(bagPath, "bag-info.txt")
    bagTags = getBagTags(bagInfoPath)
    if not 'Payload-Oxum' in bagTags:
        bagTags['Payload-Oxum'] = getOxum(os.path.join(bagPath, "data"))
    oxumParts = bagTags['Payload-Oxum'].split(".", 1)
    bagName = "ark:/67531/" + os.path.split(bagPath)[1]
    bagSize = oxumParts[0]
    bagFileCount = oxumParts[1]
    bagitString = open(os.path.join(bagPath, "bagit.txt"), "r").read()
    bagitLines = bagitString.split("\n")
    versionLine = bagitLines[0].strip()
    bagVersion = versionLine.split(None, 1)[1]
    bagXML = etree.Element(BAG + "codaXML", nsmap=BAG_NSMAP)
    name = etree.SubElement(bagXML, BAG + "name")
    name.text = bagName
    fileCount = etree.SubElement(bagXML, BAG + "fileCount")
    fileCount.text = bagFileCount
    payLoadSize = etree.SubElement(bagXML, BAG + "payloadSize")
    payLoadSize.text = bagSize
    bagitVersion = etree.SubElement(bagXML, BAG + "bagitVersion")
    bagitVersion.text = bagVersion
    lastVerified = etree.SubElement(bagXML, BAG + "lastVerified")
    lastStatus = etree.SubElement(bagXML, BAG + "lastStatus")
    if 'Bagging-Date' in bagTags:
        baggingDate = etree.SubElement(bagXML, BAG + "baggingDate")
        baggingDate.text = bagTags['Bagging-Date']
    bagInfo = etree.SubElement(bagXML, BAG + "bagInfo")
    for tag, content in bagTags.items():
        item = etree.SubElement(bagInfo, BAG + "item")
        itemName = etree.SubElement(item, BAG + "name")
        itemName.text = tag
        itemBody = etree.SubElement(item, BAG + "body")
        itemBody.text = content
    return bagXML, bagName


def getValueByName(node, name):
    """
    A helper function to pull the values out of those annoying namespace
    prefixed tags
    """

    try:
        value = node.xpath("*[local-name() = '%s']" % name)[0].text.strip()
    except:
        return None
    return value


def getNodeByName(node, name):
    """
    Get the first child node matching a given local name
    """

    if node == None:
        raise Exception(
            "Cannot search for a child '%s' in a None object" % (name,)
        )
    if not name:
        raise Exception("Unspecified name to find node for.")
    try:
        childNode = node.xpath("*[local-name() = '%s']" % name)[0]
    except:
        return None
    return childNode


def getNodesByName(parent, name):
    """
    Return a list of all of the child nodes matching a given local name
    """

    try:
        childNodes = parent.xpath("*[local-name() = '%s']" % name)
    except:
        return []
    return childNodes


def getNodeByNameChain(node, chain_list):
    """
    Walk down a chain of node names and get the nodes they represent
    e.g. [ "entry", "content", "bag", "fileCount" ]
    """

    working_list = chain_list[:]
    working_list.reverse()
    current_node = node
    while len(working_list):
        current_name = working_list.pop()
        child_node = getNodeByName(current_node, current_name)
        if child_node == None:
            raise Exception("Unable to find child node %s" % current_name)
        current_node = child_node
    return current_node


def nodeToXML(nodeObject):
    """
    Take a Django node object from our CODA store and make an XML
    representation
    """

    xmlRoot = etree.Element(NODE + "node", nsmap=NODE_NSMAP)
    nameNode = etree.SubElement(xmlRoot, NODE + "name")
    nameNode.text = nodeObject.node_name
    urlNode = etree.SubElement(xmlRoot, NODE + "url")
    urlNode.text = nodeObject.node_url
    pathNode = etree.SubElement(xmlRoot, NODE + "path")
    pathNode.text = nodeObject.node_path
    capNode = etree.SubElement(xmlRoot, NODE + "capacity")
    capNode.text = str(nodeObject.node_capacity)
    sizeNode = etree.SubElement(xmlRoot, NODE + "size")
    sizeNode.text = str(nodeObject.node_size)
    if nodeObject.last_checked:
        checkedNode = etree.SubElement(xmlRoot, NODE + "lastChecked")
        checkedNode.text = str(nodeObject.last_checked)
    return xmlRoot


def queueEntryToXML(queueEntry):
    """
    Turn an instance of a QueueEntry model into an xml data format
    """

    xmlRoot = etree.Element(QXML + "queueEntry", nsmap=QXML_NSMAP)
    arkTag = etree.SubElement(xmlRoot, QXML + "ark")
    arkTag.text = queueEntry.ark
    oxumTag = etree.SubElement(xmlRoot, QXML + "oxum")
    oxumTag.text = queueEntry.oxum
    urlListLinkTag = etree.SubElement(xmlRoot, QXML + "urlListLink")
    urlListLinkTag.text = queueEntry.url_list
    statusTag = etree.SubElement(xmlRoot, QXML + "status")
    statusTag.text = queueEntry.status
    startTag = etree.SubElement(xmlRoot, QXML + "start")
    if hasattr(queueEntry, "harvest_start") and queueEntry.harvest_start:
        if type(queueEntry.harvest_start) == type(""):
            startTag.text = queueEntry.harvest_start
        else:
            startTag.text = queueEntry.harvest_start.strftime(
                TIME_FORMAT_STRING
            )
    endTag = etree.SubElement(xmlRoot, QXML + "end")
    if hasattr(queueEntry, "harvest_end") and queueEntry.harvest_end:
        if type(queueEntry.harvest_end) == type(""):
            endTag.text = queueEntry.harvest_end
        else:
            endTag.text = queueEntry.harvest_end.strftime(TIME_FORMAT_STRING)
    positionTag = etree.SubElement(xmlRoot, QXML + "position")
    positionTag.text = str(queueEntry.queue_position)
    return xmlRoot


class AttrDict(dict):
    """
    A class to give us fielded access from a dictionary...how hacky, but lets
    us reuse some code
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self


def makeObjectFeed(
        paginator, objectToXMLFunction, feedId, title, webRoot,
        idAttr="id", nameAttr="name", dateAttr=None, request=None, page=1,
        count=20):
    """
    Take a list of some kind of object, a conversion function, an id and a
    title Return XML representing an ATOM feed
    """

    listSize = paginator.count
    if listSize:
        object_list = paginator.page(page).object_list
    else:
        object_list = []
    count = int(count)
    endStart = ((listSize / count) * count) + 1
    originalId = feedId
    idParts = feedId.split("?", 1)
    GETString = ""
    if len(idParts) == 2:
        feedId = idParts[0]
        GETString = idParts[1]
    GETStruct = request.GET
    feedTag = etree.Element(ATOM + "feed", nsmap=ATOM_NSMAP)
    # the id tag is very similar to the 'self' link
    idTag = etree.SubElement(feedTag, ATOM + "id")
    idTag.text = "%s/%s" % (webRoot, feedId)
    # the title is passed in from the calling function
    titleTag = etree.SubElement(feedTag, ATOM + "title")
    titleTag.text = title
    # the updated tag is a
    updatedTag = etree.SubElement(feedTag, ATOM + "updated")
    updatedTag.text = datetime.utcnow().strftime(TIME_FORMAT_STRING)
    # we will always show the link to the current 'self' page
    linkTag = etree.SubElement(feedTag, ATOM + "link")
    linkTag.set("rel", "self")
    if not request.META['QUERY_STRING']:
        linkTag.set("href", "%s/%s" % (webRoot, feedId))
    else:
        linkTag.set(
            "href", "%s/%s?%s" % (
                webRoot, feedId, urllib.urlencode(request.GET, doseq=True)
            )
        )
    # we always have a last page
    endLink = etree.SubElement(feedTag, ATOM + "link")
    endLink.set("rel", "last")
    endLinkGS = GETStruct.copy()
    endLinkGS.update({"page": paginator.num_pages})
    endLink.set(
        "href", "%s/%s?%s" % (
            webRoot, feedId, urllib.urlencode(endLinkGS, doseq=True)
        )
    )
    # we always have a first page
    startLink = etree.SubElement(feedTag, ATOM + "link")
    startLink.set("rel", "first")
    startLinkGS = GETStruct.copy()
    startLinkGS.update({"page": paginator.page_range[0]})
    startLink.set(
        "href", "%s/%s?%s" % (
            webRoot, feedId, urllib.urlencode(startLinkGS, doseq=True)
        )
    )
    # potentially there is a previous page, list it's details
    if paginator.page(page).has_previous():
        prevLink = etree.SubElement(feedTag, ATOM + "link")
        prevLink.set("rel", "previous")
        prevLinkGS = GETStruct.copy()
        prevLinkGS.update(
            {"page": paginator.page(page).previous_page_number()}
        )
        prevLinkText = "%s/%s?%s" % (
            webRoot, feedId, urllib.urlencode(prevLinkGS, doseq=True)
        )
        prevLink.set("href", prevLinkText)
    # potentially there is a next page, fill in it's details
    if paginator.page(page).has_next():
        nextLink = etree.SubElement(feedTag, ATOM + "link")
        nextLink.set("rel", "next")
        nextLinkGS = GETStruct.copy()
        nextLinkGS.update({"page": paginator.page(page).next_page_number()})
        nextLinkText = "%s/%s?%s" % (
            webRoot, feedId, urllib.urlencode(nextLinkGS, doseq=True)
        )
        nextLink.set("href", nextLinkText)
    for o in object_list:
        objectXML = objectToXMLFunction(o)
        if dateAttr:
            dateStamp = getattr(o, dateAttr)
        else:
            dateStamp = None
        objectEntry = wrapAtom(
            xml=objectXML,
            id='%s/%s%s/' % (webRoot, originalId, getattr(o, idAttr)),
            title=getattr(o, nameAttr),
            updated=dateStamp,
        )
        feedTag.append(objectEntry)
    return feedTag


def makeServiceDocXML(title, collections):
    """
    Make an ATOM service doc here. The 'collections' parameter is a list of
    dictionaries, with the keys of 'title', 'accept' and 'categories'
    being valid
    """

    serviceTag = etree.Element("service")
    workspaceTag = etree.SubElement(serviceTag, "workspace")
    titleTag = etree.SubElement(workspaceTag, ATOM + "title", nsmap=ATOM_NSMAP)
    titleTag.text = title
    for collection in collections:
        collectionTag = etree.SubElement(workspaceTag, "collection")
        if 'href' in collection:
            collectionTag.set("href", collection['href'])
        if 'title' in collection:
            colTitleTag = etree.SubElement(
                collectionTag, ATOM + "title", nsmap=ATOM_NSMAP
            )
            colTitleTag.text = collection['title']
        if 'accept' in collection:
            acceptTag = etree.SubElement(collectionTag, "accept")
            acceptTag.text = collection['accept']
    return serviceTag


def addObjectFromXML(
    xmlObject, XMLToObjectFunc, topLevelName, idKey, updateList):
    """
    Handle adding or updating the Queue.  Based on XML input.
    """

    # get the current object to update
    contentElement = getNodeByName(xmlObject, "content")
    objectNode = getNodeByName(contentElement, topLevelName)
    dupObjects = None
    newObject = XMLToObjectFunc(objectNode)
    try:
        kwargs = {idKey: getattr(newObject, idKey)}
        dupObjects = type(newObject).objects.filter(**kwargs)
    except type(newObject).DoesNotExist:
        pass
    if dupObjects and dupObjects.count() > 1:
        raise Exception(
            "Duplicate object with identifier %s" % getattr(newObject, idKey)
        )
    newObject.save()
    return newObject


def updateObjectFromXML(
    xmlObject, XMLToObjectFunc, topLevelName, idKey, updateList):
    """
    Handle updating an object.  Based on XML input.
    """

    # get the current object to update
    existing_object = XMLToObjectFunc(xmlObject)
    # iterate over the keys of the translation dictionary from event objects
    # to xml objects, so we can update the fields with the new information
    for k, v in updateList.items():
        # then hit each node, and see if the tag matches the translation dict
        for node in xmlObject.getiterator():
            node_tag = node.tag.split('}')[1]
            if node_tag in v[0]:
                # if we find a match, iterate the children
                for n in node.getiterator():
                    if n.tag.split('}')[1] in v[-1]:
                        # if we match the final translation, set the new value
                        setattr(existing_object, k, n.text)
    return existing_object
