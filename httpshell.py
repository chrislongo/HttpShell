import argparse
import httplib
import httpverbs
import loggers
import readline
import sys


class HttpShell(object):
    def __init__(self, args):
        self.map = {
             "head": self.head,
             "get": self.get,
             "post": self.post,
             "put": self.put,
             "delete": self.delete,
             "help": self.help,
             "?": self.help,
             ".header": self.modify_header,
             ".quit": self.exit
        }

        self.commands = self.map.keys()
        self.args = args
        self.logger = loggers.AnsiLogger()
        self.headers = {}

        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")

    def head(self, args):
        httpverbs.HttpHead(self.connect(), self.logger).run(args, self.headers)

    def get(self, args):
        httpverbs.HttpGet(self.connect(), self.logger).run(args, self.headers)

    def post(self, args):
        print "Not implemented."

    def put(self, args):
        print "Not implemented  ."

    def delete(self, args):
        print "Not implemented."

    def help(self, args):
        self.logger.print_help()

    def modify_header(self, args):
        if args and len(args) > 0:
            a = args[0].split("=")
            key = a[0]

            if len(a) > 1:
                value = a[1]

                if len(value) > 0:
                    self.headers[key] = value
                elif key in self.headers:
                    del self.headers[key]
            else:
                self.logger.print_error("Invalid syntax.")

    def complete(self, text, state):
        match = [s for s in self.commands if s and s.startswith(text)] + [None]
        return match[state]

    def connect(self):
        return httplib.HTTPConnection(self.args.host)

    def input(self):
        command = None

        while command != ".quit":
            try:
                command = raw_input(self.args.host + "> ").split()

                if command[0] in self.commands:
                    args = command[1:] if len(command) > 1 else None
                    self.map[command[0]](args)
                else:
                    self.logger.print_error("Invalid command.")
            except (EOFError, KeyboardInterrupt):
                break

        print
        self.exit()

    def exit(self, args=None):
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
