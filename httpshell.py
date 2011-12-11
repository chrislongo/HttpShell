import argparse
import httplib
import readline
import sys
from ansicolors import colorize
from ansicolors import Color
from ansicolors import Attribute
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import guess_lexer


class TerminalLogger(object):
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

    def print_data(self, response):
        data = response.read()

        print highlight(data,
            guess_lexer(data),
            TerminalFormatter())


class HttpVerb(object):
    def __init__(self, connection, logger, verb):
        self.connection = connection
        self.logger = logger
        self.verb = verb

    def __del__(self):
        self.connection.close()

    def run(self, args, headers={}):
        path = args[0] if args else "/"
        self.connection.request(self.verb, path, headers=headers)
        return self.connection.getresponse()


class HttpHead(HttpVerb):
    def __init__(self, connection, logger):
        super(HttpHead, self).__init__(connection, logger, "HEAD")

    def run(self, args, headers):
        response = super(HttpHead, self).run(args, headers)
        self.logger.print_response_code(response)
        self.logger.print_headers(headers.items(), sending=True)
        self.logger.print_headers(response.getheaders())


class HttpGet(HttpVerb):
    def __init__(self, connection, logger):
        super(HttpGet, self).__init__(connection, logger, "GET")

    def run(self, args, headers):
        response = super(HttpGet, self).run(args, headers)
        self.logger.print_response_code(response)
        self.logger.print_headers(response.getheaders())
        self.logger.print_data(response)


class HttpShell(object):
    def __init__(self, args):
        self.map = {
             "head": self.head,
             "get": self.get,
             "post": self.post,
             "put": self.put,
             "delete": self.delete,
             ".header": self.add_header
        }

        self.commands = self.map.keys()
        self.args = args
        self.logger = TerminalLogger()
        self.headers = {}

        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")

    def head(self, args):
        HttpHead(self.connect(), self.logger).run(args, self.headers)

    def get(self, args):
        HttpGet(self.connect(), self.logger).run(args, self.headers)

    def post(self, args):
        print "Not implemented."

    def put(self, args):
        print "Not implemented  ."

    def delete(self, args):
        print "Not implemented."

    def add_header(self, args):
        if args and len(args) > 0:
            a = args[0].split("=")
            name = a[0]
            value = a[1] if len(a) > 1 else ""
            self.headers[name] = value

    def complete(self, text, state):
        match = [s for s in self.commands if s and s.startswith(text)] + [None]
        return match[state]

    def connect(self):
        return httplib.HTTPConnection(self.args.host)

    def input(self):
        command = None

        while command != "quit":
            try:
                command = raw_input(self.args.host + "> ").split()

                if command[0] in self.commands:
                    args = command[1:] if len(command) > 1 else None
                    self.map[command[0]](args)
                else:
                    print "Invalid command."
            except (EOFError, KeyboardInterrupt):
                break

        print
        sys.exit(0)


def parse_args():
    parser = argparse.ArgumentParser(
        description="HTTP Shell.")

    parser.add_argument(
        "host",
        metavar="host",
        help="host to connect to")

    return parser.parse_args()

args = parse_args()
shell = HttpShell(args)
shell.input()
# /apps/mediacatalog/rest/timeService/HBO/servertime
