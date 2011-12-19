from ansicolors import colorize
from ansicolors import Color
from ansicolors import Attribute
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import guess_lexer


# ANSI color terminal logger
# use color sparingly or the UI looks like a bowl of fruit loops
class AnsiLogger(object):
    def print_text(self, text=None):
        if text:
            print text
        else:
            print

    def print_response_code(self, response):
        colors = [Color.GREY, Color.GREEN, Color.YELLOW, Color.RED, Color.RED]

        print "HTTP/{0} {1} {2}".format(
            response.version / 10.0,
            response.status,
            colorize(response.reason, colors[response.status / 100 - 1],
                Attribute.BRIGHT))

    def print_headers(self, headers, sending=False):
        for header in headers:
            print "{0}{1}: {2}".format(
                colorize("<" if sending else ">", Color.GREY),
                colorize(header[0], Color.YELLOW, Attribute.BRIGHT),
                header[1])

    def print_tackons(self, params):
        for param in params:
            print "{0}{1}{2}".format(
                param[0],
                "=" if len(param[1]) > 0 else "",
                param[1])

    def print_cookies(self, cookie):
        for morsel in cookie.values():
            print "{0}{1}{2}".format(
               colorize(morsel.key, Color.YELLOW, Attribute.BRIGHT),
               "=" if morsel.value else "",
               morsel.value)

    def print_data(self, data):
        if data:
            print
            print highlight(data,
                guess_lexer(data),
                TerminalFormatter())

    def print_help(self):
        print "Verbs"
        print "  head", colorize("[</path/to/resource>]", Color.GREY)
        print "  get", colorize("[</path/to/resource>] [| <external command>]", Color.GREY)
        print "  post", colorize("[</path/to/resource>] [| <external command>]", Color.GREY)
        print "  put", colorize("[</path/to/resource>] [| <external command>]", Color.GREY)
        print "  delete", "</path/to/resource>", colorize(" [| <external command>]", Color.GREY)
        print "Navigation"
        print "  cd", "</path/to/resource> or .."
        print "  open <url>"
        print "Metacommands"
        print "  headers", colorize("[<name>]:[<value>]", Color.GREY)
        print "  tackons", colorize("[<name>]=[<value>]", Color.GREY)
        print "  cookies"
        print "  debuglevel", colorize("[#]", Color.GREY)
        print "  quit"
        print
        print "Full documentation available at https://github.com/chrislongo/HttpShell#readme"

    def print_error(self, text):
        print text
