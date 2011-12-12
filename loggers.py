from ansicolors import colorize
from ansicolors import Color
from ansicolors import Attribute
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import guess_lexer


class AnsiLogger(object):
    def print_response_code(self, response):
        colors = [Color.GREY, Color.GREEN, Color.YELLOW, Color.RED, Color.RED]

        print "HTTP/{0} {1} {2}".format(
            response.version / 10.0,
            response.status,
            colorize(response.reason, colors[response.status / 100 - 1]))

    def print_headers(self, headers, sending=False):
        for header in headers:
            print "{0}{1}: {2}".format(
                colorize("<" if sending else ">", Color.GREY),
                colorize(header[0], Color.YELLOW, Attribute.BRIGHT),
                colorize(header[1], Color.WHITE))

    def print_data(self, data):
        print highlight(data,
            guess_lexer(data),
            TerminalFormatter())

    def print_help(self):
        print "Verbs"
        print "  head", colorize("[path] [| <external command>]", Color.GREY)
        print "  get", colorize("[path]", Color.GREY)
        print "  post", colorize("[path] [data]", Color.GREY)
        print "  put", colorize("[path] [data]", Color.GREY)
        print "  delete path"
        print "Metacommands"
        print "  .header name={0}".format(colorize("[value]", Color.GREY))
        print "  .quit"

    def print_error(self, text):
        print text
