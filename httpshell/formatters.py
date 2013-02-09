import json
import xml.dom.minidom
from StringIO import StringIO


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


# under Python <= 2.7.2 the minidom output is gnarly, should be fixed in 2.7.3+
# http://bugs.python.org/issue4147
class XmlFormatter(Formatter):
    def __init__(self, args=None):
        super(XmlFormatter, self).__init__(args)

    # for the time being this big time workaround will do it
    def format_xml(self, node, writer, indent="", addindent="", newl=""):
        # minidom likes to treat whitepace as text nodes
        if node.nodeType == xml.dom.minidom.Node.TEXT_NODE and node.data.strip() == "":
            return

        writer.write(indent + "<" + node.tagName)

        attrs = node.attributes
        keys = sorted(attrs.keys())

        for key in keys:
            writer.write(" %s=\"" % key)
            writer.write(attrs[key].value)
            writer.write("\"")

        if node.childNodes:
            writer.write(">")

            if all(map(lambda n: n.nodeType == xml.dom.minidom.Node.TEXT_NODE,
                       node.childNodes)):
                for child in node.childNodes:
                    child.writexml(writer, "", "", "")
            else:
                writer.write(newl)
                for child in node.childNodes:
                    self.format_xml(child, writer, indent + addindent,
                                    addindent, newl)
                writer.write(indent)
            writer.write("</%s>%s" % (node.tagName, newl))
        else:
            writer.write("/>%s" % (newl))

    def format(self, text):
        formatted = None

        try:
            x = xml.dom.minidom.parseString(text)
            writer = StringIO()
            self.format_xml(x.childNodes[0], writer, addindent="  ", newl="\n")
            formatted = writer.getvalue()
            x.unlink()
        except:
            formatted = text

        return formatted


JSONTYPES = (
    'application/json',
    'application/x-javascript',
    'text/javascript',
    'text/x-javascript',
    'text/x-json')

XMLTYPES = (
    'application/xml',
    'application/atom+xml',
    'application/mathml+xml',
    'application/rss+xml',
    'application/xhtml+xml',
    'text/xml')


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
