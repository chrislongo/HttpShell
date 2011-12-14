import httplib
import httpverbs
import loggers
import readline
import sys
from urlparse import urlparse


class HttpShell(object):
    def __init__(self, args):
        self.http_commands = {
             "head": self.head,
             "get": self.get,
             "post": self.post,
             "put": self.put,
             "delete": self.delete,
             "cd": self.set_path,  # should be .cd but that didn't feel natural
        }

        self.meta_commands = {
             "help": self.help,
             "?": self.help,
             "headers": self.modify_headers,
             "open": self.open_host,
             "quit": self.exit
        }

        self.dispatch = dict(self.http_commands, **self.meta_commands)

        self.args = args

        # all printing is done via the logger, that way a non-ANSI printer
        # will be a lot easier to add retroactively
        self.logger = loggers.AnsiLogger()
        self.headers = {}

        # sets up tab command completion
        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")

        # setup host and initinal path
        self.init_host(self.args.url)

    # dispatch methods

    def head(self, args):
        httpverbs.HttpHead(
            self.connect(), args, self.logger).run(self.headers)

    def get(self, args):
        httpverbs.HttpGet(
            self.connect(), args, self.logger).run(self.headers)

    def post(self, args):
        httpverbs.HttpPost(
            self.connect(), args, self.logger).run(self.headers)

    def put(self, args):
        httpverbs.HttpPut(
            self.connect(), args, self.logger).run(self.headers)

    def delete(self, args):
        httpverbs.HttpDelete(
            self.connect(), args, self.logger).run(self.headers)

    def help(self, args):
        self.logger.print_help()

    # handles .headers meta-command
    def modify_headers(self, args):
        if args and len(args) > 0:
            # args will be header:[value]
            a = args[0].split(":", 1)
            key = a[0]

            if len(a) > 1:
                value = a[1]

                if len(value) > 0:
                    self.headers[key] = value
                elif key in self.headers:
                    del self.headers[key]  # if no value provided, delete
            else:
                self.logger.print_error("Invalid syntax.")
        else:
            # print send headers
            self.logger.print_headers(self.headers.items(), sending=True)

    # changes the current host
    def open_host(self, args):
        if len(args) > 0:
            url = args.pop(0)
            self.init_host(url)

    # handles cd <path> command
    def set_path(self, args):
        path = args.pop()

        if path == "..":
            path = "".join(self.path.rsplit("/", 1)[:1])

        self.path = path if path else "/"

    def init_host(self, url):
        # url parse needs a proceeding "//" for default scheme param to work
        if not "//" in url[:8]:
            url = "//" + url

        self.url = urlparse(url, "http")
        self.path = self.url.path if self.url.path else "/"

    # readline complete handler
    def complete(self, text, state):
        match = [s for s in self.dispatch.keys() if s
            and s.startswith(text)] + [None]

        return match[state]

    # connecting is done on-demand from the dispatch methods
    def connect(self):
        host = self.url.netloc
        port = None
        connection = None

        # handle user-supplied ports from command line
        if ":" in host:
            split = host.split(":")
            host = split[0]
            port = split[1]

        if(self.url.scheme == "https"):
            connection = httplib.HTTPSConnection(host, port if port else 443)
        else:
            connection = httplib.HTTPConnection(host, port if port else 80)

        return connection

    def input_loop(self):
        command = None

        while command != ".quit":
            try:
                prompt = "{0}:{1}> ".format(self.url.netloc, self.path)

                # a valid command line will be <command> [path] [| filter]
                input = raw_input(prompt).split()

                # ignore blank input
                if not input or len(input) == 0:
                    continue

                # command will be element 0 in the array from split
                command = input.pop(0)

                if command in self.dispatch:
                    # push arguments to the stack for command
                    args = self.parse_args(input, command)

                    # invoke command via dispatch table
                    try:
                        self.dispatch[command](args)
                    except Exception as (number, desc):
                        self.logger.print_error(
                            "Error: {0} ({1})".format(desc, number))
                else:
                    self.logger.print_error("Invalid command.")
            except (EOFError, KeyboardInterrupt):
                break

        print
        self.exit()

    # parses input to set up the call stack for dispatch commands
    def parse_args(self, args, command):
        stack = []

        # ignore meta-commands
        if command not in self.meta_commands:
            path = None

            if len(args) > 0:
                # element 0 of args array will be the path element
                path = args.pop(0)

                # there's a pipe in my path!
                # user didn't use whitespace between path and pipe character
                # also accounts for if the user did not supply a path
                if "|" in path:
                    s = path.split("|", 1)
                    path = s.pop(0)
                    args.insert(0, "".join(s))

                # pipe, if exists, will be first element in array now
                if len(args) > 0:
                    pipe = " ".join(args).strip()

                    if pipe[0] == "|":
                        pipe = pipe[1:]
                    # push it on the call stack for the command method
                    stack.append(pipe)

                # if path has changed update self.path so the UI reflects it
                if path and not path[0] in "/.":
                    path = "{0}{1}{2}".format(
                        self.path,
                        "/" if self.path[-1] != "/" else "",
                        path)

            # push the path on the stack for command method
            # if it's empty the user did not supply one so use self.path
            stack.append(path if path else self.path)
        else:
            if len(args) > 0:
                # meta-commands to their own arg parsing
                stack.append(" ".join(args))

        return stack

    def exit(self, args=None):
        sys.exit(0)
