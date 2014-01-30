"""
Simple bit of code to implement reading and writing ANVL files
"""


def readANVLString(string):
    """
    Take a string in ANVL format and break it into a dictionary of key/values
    """

    ANVLDict = {}
    ANVLLines = string.split("\n")
    lineCount = len(ANVLLines)
    index = 0
    while index < lineCount:
        line = ANVLLines[index]
        #print "line is %s" % line
        if not len(line) or not len(line.strip()):
            index = index + 1
            continue
        if "#" == line[0]:
            index = index + 1
            continue
        parts = line.split(":", 1)
        key = parts[0].strip()
        #print "key is %s" % key
        contentBuffer = parts[1].lstrip()
        nextIndex = index + 1
        while nextIndex < lineCount:
            nextLine = ANVLLines[nextIndex]
            if len(nextLine) and "#" == nextLine[0]:
                nextIndex = nextIndex + 1
                continue
            if nextLine == nextLine.lstrip():
                break
            if contentBuffer:
                contentBuffer = contentBuffer + " " + nextLine.lstrip()
            else:
                contentBuffer = nextLine.lstrip()
            nextIndex = nextIndex + 1
        index = nextIndex
        ANVLDict[key] = contentBuffer
        #index = index + 1
    return ANVLDict


def breakString(string, width=79, firstLineOffset=0):
    originalWidth = width
    width = width - firstLineOffset
    if len(string) < width + 1:
        return string
    index = width
    while index > 0:
        if ' ' == string[index]:
            if not string[index + 1].isspace() and not \
                string[index - 1].isspace():
                stringPart1 = string[0:index]
                stringPart2 = string[index:]
                return "%s\n%s" % (
                    stringPart1,
                    breakString(stringPart2, originalWidth)
                )
        index = index - 1
    return string


def writeANVLString(ANVLDict):
    """
    Take a dictionary and write out they key/value pairs in ANVL format
    """
    lines = []
    keys = ANVLDict.keys()
    keys.sort()
    for key in keys:
        value = ANVLDict[key]
        offset = len(key) + 1
        line = "%s: %s" % (key, breakString(value, 79, offset))
        lines.append(line)
    return "\n".join(lines)
