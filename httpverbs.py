import subprocess


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

    def pipe(self, command, data):

        p = subprocess.Popen(command, shell=True, bufsize=-1,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = p.communicate(data)

        return output.decode('utf-8')


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

        data = response.read()

        if args and len(args) > 1 and args[1] == "|":
            command = " ".join(args[2:])
            data = self.pipe(command, data)

        self.logger.print_data(data)
