import argparse
import httplib
import httpverbs
import loggers
import readline
import sys


class HttpShell(object):
    def __init__(self, args):
        self.dispatch = {
             "head": self.head,
             "get": self.get,
             "post": self.post,
             "put": self.put,
             "delete": self.delete,
             "help": self.help,
             "?": self.help,
             ".headers": self.modify_header,
             ".path": self.set_path,
             ".quit": self.exit
        }

        self.commands = self.dispatch.keys()
        self.args = args
        self.logger = loggers.AnsiLogger()
        self.headers = {}
        self.path = "/"

        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")

    def head(self, args):
        httpverbs.HttpHead(self.connect(), args, self.logger).run(self.headers)

    def get(self, args):
        httpverbs.HttpGet(self.connect(), args, self.logger).run(self.headers)

    def post(self, args):
        print "Not implemented."

    def put(self, args):
        print "Not implemented  ."

    def delete(self, args):
        print "Not implemented."

    def help(self, args):
        self.logger.print_help()

    def set_path(self, args):
        path = args["path"]

        if path == "..":
            path = "".join(self.path.rsplit("/", 1)[:1])

        self.path = path if path else "/"

    def modify_header(self, args):
        print args
        if args and len(args) > 0:
            a = args[0].split(":", 1)
            key = a[0]

            if len(a) > 1:
                value = a[1]

                if len(value) > 0:
                    self.headers[key] = value
                elif key in self.headers:
                    del self.headers[key]
            else:
                self.logger.print_error("Invalid syntax.")
        else:
            self.logger.print_headers(self.headers.items(), sending=True)

    def complete(self, text, state):
        match = [s for s in self.commands if s and s.startswith(text)] + [None]
        return match[state]

    def connect(self):
        return httplib.HTTPConnection(self.args.host)

    def input(self):
        command = None

        while command != ".quit":
            try:
                prompt = "{0}:{1}> ".format(self.args.host, self.path)
                command = raw_input(prompt).split()

                if not command:
                    continue
                elif command[0] in self.commands:
                    args = self.parse_args(command[1:])
                    self.dispatch[command[0]](args)
                else:
                    self.logger.print_error("Invalid command.")
            except (EOFError, KeyboardInterrupt):
                break

        print
        self.exit()

    def parse_args(self, args):
        parsed = {}
        path = None
        command = None

        if args and len(args) > 0:
            path = args.pop(0)

            if path[:1] != "/" and path[:1] != ".":
                path = "/" + path

            command = None

            if "|" in path:
                s = path.split("|", 1)
                path = s.pop(0)
                args.insert(0, "".join(s))

            command = " ".join(args).strip()

            if command[:1] == "|":
                command = command[1:]

        parsed["path"] = path if path else self.path

        if command:
            parsed["command"] = command

        return parsed

    def exit(self, args=None):
        sys.exit(0)


def parse_command_line():
    parser = argparse.ArgumentParser(
        description="HTTP Shell.")

    parser.add_argument(
        "host",
        metavar="host",
        help="host to connect to")

    return parser.parse_args()

args = parse_command_line()
shell = HttpShell(args)
shell.input()
# /apps/mediacatalog/rest/timeService/HBO/servertime
