import json
import subprocess
from urllib import urlencode


class HttpVerb(object):
    def __init__(self, connection, args, logger, verb):
        self.connection = connection
        self.logger = logger
        self.verb = verb
        self.path = args.pop()
        self.pipe_command = args.pop() if args else None

    def __del__(self):
        self.connection.close()

    def run(self, params=None, headers=None):
        self.connection.request(self.verb, self.path, params, headers)
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
            self.logger.print_error(error.decode("utf-8"))
        else:
            result = output.decode("utf-8")

        return result

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


class HttpHead(HttpVerb):
    def __init__(self, connection, args, logger):
        super(HttpHead, self).__init__(connection, args, logger, "HEAD")

    def run(self, headers):
        response = super(HttpHead, self).run(headers=headers)
        self.handle_response(response, headers)


class HttpGet(HttpVerb):
    def __init__(self, connection, args, logger):
        super(HttpGet, self).__init__(connection, args, logger, "GET")

    def run(self, headers):
        response = super(HttpGet, self).run(headers=headers)
        self.handle_response(response, headers, with_data=True)


class HttpPost(HttpVerb):
    def __init__(self, connection, args, logger):
        super(HttpPost, self).__init__(connection, args, logger, "POST")
        self.params = self.input_params()

    def run(self, headers):
        if self.params:
            response = super(HttpPost, self).run(
                params=self.params, headers=headers)

            self.handle_response(response, headers, with_data=True)


class HttpPut(HttpVerb):
    def __init__(self, connection, args, logger):
        super(HttpPut, self).__init__(connection, args, logger, "PUT")
        self.params = self.input_params()

    def run(self, headers):
        if self.params:
            response = super(HttpPut, self).run(
                params=self.params, headers=headers)

            self.handle_response(response, headers, with_data=True)


class HttpDelete(HttpVerb):
    def __init__(self, connection, args, logger):
        super(HttpDelete, self).__init__(connection, args, logger, "DELETE")

    def run(self, headers):
        response = super(HttpDelete, self).run(headers=headers)
        self.handle_response(response, headers, with_data=True)
