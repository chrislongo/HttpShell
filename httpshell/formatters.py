import json
import xml.dom.minidom


class Formatter(object):
    def __init__(self, args=None):
        self.args = args

    def format(text):
        pass


class JsonFormatter(Formatter):
    def __init__(self, args=None):
        super(JsonFormatter, self).__init__(args)

    def format(self, text):
        formatted = None

        try:
            o = json.loads(text)
            formatted = json.dumps(o, indent=2)
        except (TypeError, ValueError):
            formatted = text

        return formatted


class XmlFormatter(Formatter):
    def __init__(self, args=None):
        super(XmlFormatter, self).__init__(args)

    def format(self, text):
        formatted = None

        try:
            x = xml.dom.minidom.parseString(text)
            formatted = x.toprettyxml("  ")
        except:
            formatted = text

        return formatted


JSONTYPES = ("application/json", "application/x-javascript", "text/javascript",
"text/x-javascript", "text/x-json")

XMLTYPES = ("application/xml", "text/xml", "application/xhtml+xml",
"application/atom+xml", "application/mathml+xml", "application/rss+xml")


def format_by_mimetype(text, mimetype):
    formatter = None

    if mimetype in JSONTYPES:
        formatter = JsonFormatter()
    elif mimetype in XMLTYPES:
        formatter = XmlFormatter()

    if formatter:
        return formatter.format(text)
    else:
        return text
