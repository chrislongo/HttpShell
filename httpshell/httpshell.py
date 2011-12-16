import httplib
import httpverbs
import json
import loggers
import readline
import sys
from urlparse import urlparse
from urllib import urlencode


class HttpShell(object):
    def __init__(self, args):
        self.http_commands = {
             "head": self.head,
             "get": self.get,
             "post": self.post,
             "put": self.put,
             "delete": self.delete,
             "cd": self.set_path,
        }

        self.meta_commands = {
             "help": self.help,
             "?": self.help,
             "headers": self.modify_headers,
             "tackons": self.modify_tackons,
             "open": self.open_host,
             "quit": self.exit
        }

        # dispatch map is http + meta maps
        self.dispatch = dict(
            self.http_commands.items() + self.meta_commands.items())

        self.url = None
        self.path = None
        self.query = None

        self.args = args
        self.headers = {}
        self.tackons = {}

        # all printing is done via the logger, that way a non-ANSI printer
        # will be a lot easier to add retroactively
        self.logger = loggers.AnsiLogger()

        # sets up tab command completion
        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")

        # setup host and initinal path
        self.init_host(self.args.url)

    # dispatch methods

    def head(self, path, pipe=None):
        httpverbs.HttpHead(
            self.connect(path), path, pipe, self.logger).run(self.headers)

    def get(self, path, pipe=None):
        httpverbs.HttpGet(
            self.connect(path), path, pipe, self.logger).run(self.headers)

    def post(self, path, pipe=None):
        params = self.input_params()

        if params:
            httpverbs.HttpPost(self.connect(path),
                path, pipe, params, self.logger).run(self.headers)

    def put(self, path, pipe=None):
        params = self.input_params()

        if params:
            httpverbs.HttpPut(self.connect(path),
                path, pipe, params, self.logger).run(self.headers)

    def delete(self, path, pipe=None):
        httpverbs.HttpDelete(
            self.connect(path), path, pipe, self.logger).run(self.headers)

    def help(self):
        self.logger.print_help()

    # handles .headers meta-command
    def modify_headers(self, header=None):
        if header and len(header) > 0:
            # header will be header:[value]
            a = header.split(":", 1)
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

    # handles params meta-command
    def modify_tackons(self, args=None):
        if args and len(args) > 0:
            # args will be param:[value]

            if not "=" in args[0]:
                key = "".join(args)
                value = ""
                self.tackons[key] = value
            else:
                a = args[0].split("=", 1)
                key = a[0]

                if len(a) > 1:
                    value = a[1]

                if len(value) > 0:
                    self.tackons[key] = value
                elif key in self.tackons:
                    del self.tackons[key]  # if no value provided, delete
        else:
            # print send tackons
            self.logger.print_tackons(self.tackons.items())

    # changes the current host
    def open_host(self, url=None):
        if url:
            self.init_host(url)

    # handles cd <path> command
    def set_path(self, path):
        if path == "..":
            path = "".join(self.path.rsplit("/", 1)[:1])

        self.path = path if path else "/"

    def init_host(self, url):
        # url parse needs a proceeding "//" for default scheme param to work
        if not "//" in url[:8]:
            url = "//" + url

        self.url = urlparse(url, "http")
        self.path = self.url.path if self.url.path else "/"
        self.query = self.url.query

    # converts tackon dict to query params
    def dict_to_query(self, map):
        l = []
        for k, v in sorted(map.items()):
            s = k
            if(v):
                s += "=" + str(v)
            l.append(s)

        return "&".join(l)

    # combine two query strings into one
    def combine_queries(self, a, b):
        s = ""
        if a and len(a) > 0:
            s = a
            if b and len(b) > 0:
                s += "&"
        if b and len(b) > 0:
            s += b

        return s

    # modifies the path for tackon query params
    def mod_path(self, path, query=None):
        q = self.combine_queries(
                query, self.dict_to_query(self.tackons))

        if len(q) > 0:
            return path + "?" + q
        else:
            return path

    # readline complete handler
    def complete(self, text, state):
        match = [s for s in self.dispatch.keys() if s
            and s.startswith(text)] + [None]

        return match[state]

    # connecting is done on-demand from the dispatch methods
    def connect(self, path):
        self.logger.print_text("Connecting to {0}://{1}{2}\n".format(
             self.url.scheme, self.url.netloc, path))

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

    # read lines of input for POST/PUT
    def input_params(self):
        list = []

        while True:
            line = raw_input("... ")
            if len(line) == 0:
                break
            list.append(line)

        # join list to form string
        params = "".join(list)

        if params[:2] == "@{":  # magic JSON -> urlencode invoke char
            params = self.json_to_urlencode(params[1:])

        return params

    # converts JSON to url encoded for easier posting forms
    def json_to_urlencode(self, json_string):
        params = None

        try:
            o = json.loads(json_string)
            params = urlencode(o)
        except ValueError:
            self.logger.print_error("Malformed JSON.")

        return params

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
                        self.dispatch[command](*args)
                    except Exception as e:
                        self.logger.print_error(
                           "Error: {0}".format(e))
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
            pipe = None

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

                # account for requests from relative dirs
                if path and not path[0] in "/.":
                    path = "{0}{1}{2}".format(
                        self.path,
                        "/" if self.path[-1] != "/" else "",
                        path)

            # push the path on the stack for command method
            # if it's empty the user did not supply one so use self.path
            if path:
                query = None
                a = path.split("?")  # chop query params

                if len(a) > 1:
                    path = a[0]
                    query = a[1]
                stack.append(self.mod_path(path, query))
            else:
                stack.append(self.mod_path(self.path, self.query))

            if pipe:
                stack.append(pipe)
        else:
            if len(args) > 0:
                # meta-commands to their own arg parsing
                stack.append(" ".join(args))

        return stack

    def exit(self, args=None):
        sys.exit(0)
