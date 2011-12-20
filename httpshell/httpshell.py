import httpverbs
import json
import loggers
import os
import re
import readline
import sys
import Cookie
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
             "cookies": self.modify_cookies,
             "open": self.open_host,
             "debuglevel": self.set_debuglevel,
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
        self.cookies = {}

        self.args.debuglevel = 0

        # all printing is done via the logger, that way a non-ANSI printer
        # will be a lot easier to add retroactively
        self.logger = loggers.AnsiLogger()

        self.init_readline()

        # setup host and initial path
        self.init_host(self.args.url)

    def init_readline(self):
        self.history_file = os.path.join(os.path.expanduser("~"), ".httpsh")

        try:
            readline.read_history_file(self.history_file)
        except IOError:
            pass

        # sets up tab command completion
        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")

    def init_host(self, url):
        # url parse needs a proceeding "//" for default scheme param to work
        if not "//" in url[:8]:
            url = "//" + url

        self.url = urlparse(url, "http")
        self.path = self.url.path if self.url.path else "/"
        self.query = self.url.query

    # dispatch methods

    def head(self, path, pipe=None):
        httpverbs.HttpHead(self.args, self.logger).run(
            self.url, path, pipe, self.headers, self.cookies)

    def get(self, path, pipe=None):
        httpverbs.HttpGet(self.args, self.logger).run(
            self.url, path, pipe, self.headers, self.cookies)

    def post(self, path, pipe=None):
        body = self.input_body()

        if body:
            httpverbs.HttpPost(self.args, self.logger).run(
                self.url, path, pipe, body, self.headers, self.cookies)

    def put(self, path, pipe=None):
        body = self.input_body()

        if body:
            httpverbs.HttpPut(self.args, self.logger).run(
                self.url, path, pipe, body, self.headers, self.cookies)

    def delete(self, path, pipe=None):
        httpverbs.HttpDelete(self.args, self.logger).run(
            self.url, path, pipe, self.headers, self.cookies)

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
            # args will be param=[value]

            if not "=" in args:  # it's not foo=bar it's just foo
                self.tackons[args] = ""
            else:
                a = args.split("=", 1)
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

    def modify_cookies(self, args=None):
        if args and len(args) > 0:
            # args will be cookie=[value]

            cookie = None

            if not self.url.netloc in self.cookies:
                cookie = Cookie.SimpleCookie()
                self.cookies[self.url.netloc] = cookie
            else:
                cookie = self.cookies[self.url.netloc]

            if args and len(args) > 0:
                # cookie will be cookie=[value]
                a = args.split("=", 1)
                key = a[0]
                if len(a) > 1:
                    value = a[1]

                    if len(value) > 0:
                        cookie[key] = value
                    else:
                        for morsel in cookie.values():
                            if morsel.key == key:
                                del cookie[morsel.key]
                else:
                    self.logger.print_error("Invalid syntax.")
        elif self.url.netloc in self.cookies:
            self.logger.print_cookies(self.cookies[self.url.netloc])

    # changes the current host
    def open_host(self, url=None):
        if url:
            self.init_host(url)

    # handles cd <path> command
    def set_path(self, path):
        path = path.split("?")[0]  # chop off any query params

        if path == "..":
            path = "".join(self.path.rsplit("/", 1)[:1])

        self.path = path if path else "/"

    def set_debuglevel(self, level=None):
        if not level:
            self.logger.print_text(str(self.args.debuglevel))
        else:
            try:
                self.args.debuglevel = int(level)
            except:
                pass

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

    # read lines of input for POST/PUT
    def input_body(self):
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

    @property
    def prompt(self):
        host = None

        if "@" in self.url.netloc:  # hide password in prompt
            split = re.split("@|:", self.url.netloc)
            host = split[0] + "@" + split[-1]
        else:
            host = self.url.netloc

        return "{0}:{1}> ".format(host, self.path)

    def input_loop(self):
        command = None

        while True:
            try:
                # a valid command line will be <command> [path] [| filter]
                input = raw_input(self.prompt).split()

                # ignore blank input
                if not input or len(input) == 0:
                    continue

                # command will be element 0 in the array from split
                command = input.pop(0).lower()

                if command in self.dispatch:
                    # push arguments to the stack for command
                    args = self.parse_args(input, command)

                    # invoke command via dispatch table
                    #try:
                    self.dispatch[command](*args)
                    #except Exception as e:
                    #    self.logger.print_error(
                    #       "Error: {0}".format(e))
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
        readline.write_history_file(self.history_file)
        sys.exit(0)
