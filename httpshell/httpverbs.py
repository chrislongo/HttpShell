import subprocess


class HttpVerb(object):
    def __init__(self, connection, path, pipe, logger, verb):
        self.connection = connection
        self.logger = logger
        self.verb = verb
        self.path = path
        self.pipe_command = pipe

    def __del__(self):
        self.connection.close()

    def run(self, body=None, headers=None):
        self.connection.request(self.verb, self.path, body, headers)
        return self.connection.getresponse()

    def handle_response(self, response, headers, with_data=False):
        self.logger.print_response_code(response)
        self.logger.print_headers(headers.items(), sending=True)
        self.logger.print_headers(response.getheaders())

        if with_data:
            data = response.read()

            if self.pipe_command:
                data = self.pipe(self.pipe_command, data)

            self.logger.print_data(data)

    # pipes output to external commands like xmllint, tidy for filtering
    def pipe(self, command, data):
        result = None

        p = subprocess.Popen(command, shell=True, bufsize=-1,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = p.communicate(data)

        if error:
            self.logger.print_text()
            self.logger.print_error(error.decode("utf-8"))
        else:
            result = output.decode("utf-8")

        return result


class HttpHead(HttpVerb):
    def __init__(self, connection, path, pipe, logger):
        super(HttpHead, self).__init__(connection, path, pipe, logger, "HEAD")

    def run(self, headers):
        response = super(HttpHead, self).run(headers=headers)
        self.handle_response(response, headers)


class HttpGet(HttpVerb):
    def __init__(self, connection, path, pipe, logger):
        super(HttpGet, self).__init__(connection, path, pipe, logger, "GET")

    def run(self, headers):
        response = super(HttpGet, self).run(headers=headers)
        self.handle_response(response, headers, with_data=True)


class HttpPost(HttpVerb):
    def __init__(self, connection, path, pipe, body, logger):
        super(HttpPost, self).__init__(connection, path, pipe, logger, "POST")
        self.body = body

    def run(self, headers):
        response = super(HttpPost, self).run(
            body=self.body, headers=headers)

        self.handle_response(response, headers, with_data=True)


class HttpPut(HttpVerb):
    def __init__(self, connection, path, pipe, body, logger):
        super(HttpPut, self).__init__(connection, path, pipe, logger, "PUT")
        self.body = body

    def run(self, headers):
        response = super(HttpPut, self).run(
            body=self.body, headers=headers)

        self.handle_response(response, headers, with_data=True)


class HttpDelete(HttpVerb):
    def __init__(self, connection, path, pipe, logger):
        super(HttpDelete, self).__init__(
            connection, path, pipe, logger, "DELETE")

    def run(self, headers):
        response = super(HttpDelete, self).run(headers=headers)
        self.handle_response(response, headers, with_data=True)
