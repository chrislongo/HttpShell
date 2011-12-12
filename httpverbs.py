import subprocess


class HttpVerb(object):
    def __init__(self, connection, args, logger, verb):
        self.args = {}
        self.connection = connection
        self.logger = logger
        self.verb = verb

        self.parse_args(args)

    def __del__(self):
        self.connection.close()

    def run(self, headers={}):
        path = self.args["path"] if "path" in self.args else "/"
        self.connection.request(self.verb, path, headers=headers)
        return self.connection.getresponse()

    def parse_args(self, args):
        if not args or len(args) == 0:
            return

        path = args.pop(0)
        command = None

        if "|" in path:
            s = path.split("|")
            path = s.pop(0)
            args.insert(0, "".join(s))

        command = " ".join(args).strip()

        if command[:1] == "|":
            command = command[1:]

        self.args["path"] = path

        if command:
            self.args["command"] = command

    def pipe(self, command, data):
        p = subprocess.Popen(command, shell=True, bufsize=-1,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = p.communicate(data)

        result = None

        if error:
            self.logger.print_error(error.decode("utf-8"))
        else:
            result = output.decode("utf-8")

        return result


class HttpHead(HttpVerb):
    def __init__(self, connection, args, logger):
        super(HttpHead, self).__init__(connection, args, logger, "HEAD")

    def run(self, headers):
        response = super(HttpHead, self).run(headers)
        self.logger.print_response_code(response)
        self.logger.print_headers(headers.items(), sending=True)
        self.logger.print_headers(response.getheaders())


class HttpGet(HttpVerb):
    def __init__(self, connection, args, logger):
        super(HttpGet, self).__init__(connection, args, logger, "GET")

    def run(self, headers):
        response = super(HttpGet, self).run(headers)
        self.logger.print_response_code(response)
        self.logger.print_headers(response.getheaders())

        data = response.read()

        if "command" in self.args:
            data = self.pipe(self.args["command"], data)

        if data:
            self.logger.print_data(data)


class HttpPost(HttpVerb):
    def __init__(self, connection, args, logger):
        super(HttpPost, self).__init__(connection, args, logger, "POST")

    def run(self, headers):
        pass


class HttpPut(HttpVerb):
    def __init__(self, connection, args, logger):
        super(HttpPut, self).__init__(connection, args, logger, "PUT")

    def run(self, args, headers):
        pass


class HttpDelete(HttpVerb):
    def __init__(self, connection, args, logger):
        super(HttpDelete, self).__init__(connection, args, logger, "DELETE")

    def run(self, args, headers):
        pass
