import base64
import formatters
import httplib
import subprocess
import Cookie


class HttpVerb(object):
    def __init__(self, args, logger, verb):
        self.connection = None

        self.args = args
        self.logger = logger
        self.verb = verb

    def __del__(self):
        if self.connection:
            self.connection.close()

    def run(self, url, path, pipe=None, body=None, headers=None, cookies=None):
        self.url = url
        self.path = path
        self.pipe = pipe
        self.headers = headers
        self.cookies = cookies

        if not self.args.disable_cookies:
            self.set_request_cookies()

        self.connect()
        self.connection.request(self.verb, self.path, body, headers)
        return self.connection.getresponse()

    # connecting is done on-demand from the dispatch methods
    def connect(self):
        self.logger.print_text("Connecting to {0}://{1}{2}\n".format(
             self.url.scheme, self.url.netloc, self.path))

        host = self.url.netloc
        port = None

        if "@" in host:
            split = host.split("@")
            if len(split) > 1:
                auth = base64.b64encode(split[0])
                host = split[1]
                self.headers["Authorization"] = "Basic " + auth
            else:
                host = split[0]

        # handle user-supplied ports from command line
        if ":" in host:
            split = host.split(":")
            host = split[0]
            port = split[1]

        if(self.url.scheme == "https"):
            self.connection = httplib.HTTPSConnection(
                host, port if port else 443)
        else:
            self.connection = httplib.HTTPConnection(
                host, port if port else 80)

        self.connection.set_debuglevel(self.args.debuglevel)

    def handle_response(self, response, with_data=False):
        self.logger.print_response_code(response)
        self.logger.print_headers(self.headers.items(), sending=True)
        self.logger.print_headers(response.getheaders())

        if not self.args.disable_cookies:
            self.store_response_cookies(response)

        if with_data:
            data = response.read()

            if self.args.auto_format:
                mimetype = response.getheader("content-type")

                if mimetype:
                    data = formatters.format_by_mimetype(
                        data, mimetype.split(";")[0])

            if self.pipe:
                data = self.pipe_data(self.pipe, data)

            self.logger.print_data(data)

    def set_request_cookies(self):
        if self.url.netloc in self.cookies:
            l = []
            cookie = self.cookies[self.url.netloc]
            #  very basic cookie support atm.  no expiry, etc.
            for morsel in cookie.values():
                l.append(morsel.key + "=" + morsel.coded_value)
            self.headers["cookie"] = "; ".join(l)

    def store_response_cookies(self, response):
        header = response.getheader("set-cookie")
        if header:
            cookie = Cookie.SimpleCookie(header)
            self.cookies[self.url.netloc] = cookie

    # pipes output to external commands like xmllint, tidy for filtering
    def pipe_data(self, command, data):
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
    def __init__(self, args, logger):
        super(HttpHead, self).__init__(args, logger, "HEAD")

    def run(self, url, path, pipe=None, headers=None, cookies=None):
        response = super(HttpHead, self).run(
            url, path, pipe, headers=headers, cookies=cookies)

        self.handle_response(response)


class HttpGet(HttpVerb):
    def __init__(self, args, logger):
        super(HttpGet, self).__init__(args, logger, "GET")

    def run(self, url, path, pipe=None, headers=None, cookies=None):
        response = super(HttpGet, self).run(
            url, path, pipe, headers=headers, cookies=cookies)

        self.handle_response(response, with_data=True)


class HttpPost(HttpVerb):
    def __init__(self, args, logger):
        super(HttpPost, self).__init__(args, logger, "POST")

    def run(self, url, path, pipe=None, body=None, headers=None, cookies=None):
        response = super(HttpPost, self).run(
            url, path, pipe, body, headers, cookies)

        self.handle_response(response, with_data=True)


class HttpPut(HttpVerb):
    def __init__(self, args, logger):
        super(HttpPut, self).__init__(args, logger, "PUT")

    def run(self, url, path, pipe=None, body=None, headers=None, cookies=None):
        response = super(HttpPut, self).run(
            url, path, pipe, body, headers, cookies)

        self.handle_response(response, with_data=True)


class HttpDelete(HttpVerb):
    def __init__(self, args, logger):
        super(HttpDelete, self).__init__(args, logger, "DELETE")

    def run(self, url, path, pipe=None, headers=None, cookies=None):
        response = super(HttpDelete, self).run(
            url, path, pipe, headers=headers, cookies=cookies)

        self.handle_response(response, with_data=True)
