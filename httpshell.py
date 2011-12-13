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
             "cd": self.set_path,
             "help": self.help,
             "?": self.help,
             ".headers": self.modify_headers,
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
        list = []

        while True:
            line = raw_input("... ")
            if len(line) == 0:
                break
            list.append(line)

        params = "".join(list)
        args.append(params)
        httpverbs.HttpPost(self.connect(), args, self.logger).run(self.headers)

    def put(self, args):
        httpverbs.HttpPut(self.connect(), args, self.logger).run(self.headers)

    def delete(self, args):
        httpverbs.HttpDelete(
            self.connect(), args, self.logger).run(self.headers)

    def help(self, args):
        self.logger.print_help()

    def set_path(self, args):
        path = args.pop()

        if path == "..":
            path = "".join(self.path.rsplit("/", 1)[:1])

        self.path = path if path else "/"

    def modify_headers(self, args):

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
        host = self.args.host
        port = 80

        if ":" in host:
            split = self.args.host.split(":")
            host = split[0]
            port = split[1]

        connection = None

        if(self.args.ssl):
            connection = httplib.HTTPSConnection(host, port)
        else:
            connection = httplib.HTTPConnection(host, port)

        return connection

    def input(self):
        command = None

        while command != ".quit":
            try:
                prompt = "{0}:{1}> ".format(self.args.host, self.path)
                input = raw_input(prompt).split()

                if not input or len(input) == 0:
                    continue

                command = input.pop(0)

                if command in self.commands:
                    args = self.parse_args(input, command)
                    self.dispatch[command](args)
                else:
                    self.logger.print_error("Invalid command.")
            except (EOFError, KeyboardInterrupt):
                break

        print
        self.exit()

    def parse_args(self, args, command):
        stack = []

        if command[0] != ".":
            path = None

            if len(args) > 0:
                path = args.pop(0)

                if "|" in path:
                    s = path.split("|", 1)
                    path = s.pop(0)
                    args.insert(0, "".join(s))

                if len(args) > 0:
                    pipe = " ".join(args).strip()

                    if pipe[0] == "|":
                        pipe = pipe[1:]

                    stack.append(pipe)

                if path and not path[0] in "/.":
                    path = "{0}{1}{2}".format(
                        self.path,
                        "/" if self.path[-1] != "/" else "",
                        path)

            stack.append(path if path else self.path)
        else:
            if len(args) > 0:
                stack.append(" ".join(args))

        return stack

    def exit(self, args=None):
        sys.exit(0)


def parse_command_line():
    parser = argparse.ArgumentParser(
        description="HTTP Shell.")

    parser.add_argument(
        "host",
        metavar="host[:port]",
        help="host to connect to")

    parser.add_argument(
        "--ssl",
        action="store_true",
        default=False,
        dest="ssl",
        help="enable SSL")

    return parser.parse_args()


def main():
    args = parse_command_line()
    shell = HttpShell(args)
    shell.input()

if __name__ == "__main__":
    main()
