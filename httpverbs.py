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
