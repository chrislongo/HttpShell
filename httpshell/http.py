import Cookie
import formatters
import httplib2
import json
import oauth2 as oauth
import os
import subprocess
import version


class Http(object):
    def __init__(self, args, logger, verb):
        self.args = args
        self.logger = logger
        self.verb = verb

    def run(self, url, path, pipe=None, headers=None, cookies=None, body=""):
        self.url = url
        host = self.url.netloc

        httpclient = self.init_httpclient()
        httpclient.follow_redirects = False
        httplib2.debuglevel = self.args.debuglevel

        # check for authentication credentials
        if "@" in host:
            split = host.split("@")
            if len(split) > 1:
                host = split[1]
                creds = split[0].split(":")
                httpclient.add_credentials(creds[0], creds[1])
            else:
                host = split[0]

        uri = "{0}://{1}{2}".format(self.url.scheme, host, path)

        if not self.args.disable_cookies:
            self.set_request_cookies(cookies, headers)

        if not "host" in headers:
            headers["host"] = host
        if not "accept-encoding" in headers:
            headers["accept-encoding"] = "gzip, deflate"
        if not "user-agent" in headers:
            headers["user-agent"] = "httpsh/" + version.VERSION

        self.logger.print_text("Connecting to " + uri)

        response, content = httpclient.request(
            uri, method=self.verb, body=body, headers=headers)

        self.handle_response(response, content, headers, cookies, pipe)

    def init_httpclient(self):
        http = None

        keysfile = os.path.join(os.path.expanduser("~"),
                                ".httpshell", self.url.netloc + ".json")

        if os.path.isfile(keysfile):
            try:
                with open(keysfile, "r") as file:
                    keys = json.load(file)
                    token = None

                    consumer = oauth.Consumer(keys["consumer"]["consumer-key"],
                                              keys["consumer"]["consumer-secret"])
                    if "access" in keys:
                        token = oauth.Token(keys["access"]["access-token"],
                                            keys["access"]["access-token-secret"])

                    http = oauth.Client(consumer, token)
                    self.logger.print_text("Using OAuth config in " + keysfile)
            except:
                self.logger.print_error(
                    "Failed reading OAuth data from: " + keysfile)
        else:
            http = httplib2.Http()

        return http

    def set_request_cookies(self, cookies, headers):
        if self.url.netloc in cookies:
            l = []
            cookie = cookies[self.url.netloc]
            #  very basic cookie support atm.  no expiry, etc.
            for morsel in cookie.values():
                l.append(morsel.key + "=" + morsel.coded_value)
            headers["cookie"] = "; ".join(l)

    def handle_response(self, response, content, headers, cookies, pipe=None):
        self.logger.print_response_code(response)
        if self.args.show_headers:
            self.logger.print_headers(headers.items(), True)
            self.logger.print_headers(response.items())

        if not self.args.disable_cookies:
            self.store_response_cookies(response, cookies)

        if self.args.auto_format:
            mimetype = response["content-type"]

            if mimetype:
                content = formatters.format_by_mimetype(
                    content, mimetype.split(";")[0])

        if pipe:
            content = self.pipe_data(pipe, content)

        self.logger.print_data(content)

    def store_response_cookies(self, response, cookies):
        if "set-cookie" in response:
            header = response["set-cookie"]
            cookie = Cookie.SimpleCookie(header)
            cookies[self.url.netloc] = cookie

    # pipes output to external commands like xmllint, tidy for filtering
    def pipe_data(self, command, data):
        result = None

        p = subprocess.Popen(command, shell=True, bufsize=-1,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE)
        output, error = p.communicate(data)

        if error:
            self.logger.print_text()
            self.logger.print_error(error.decode("utf-8"))
        else:
            result = output.decode("utf-8")

        return result
