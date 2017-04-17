# Info

An interactive shell for issuing HTTP commands to a web server or REST API.

![A picture of httpsh in action](http://i.imgur.com/bDQha.png)

Issue HTTP commands (HEAD, GET, POST, PUT, DELETE, OPTIONS, TRACE) to a server 
with interactive feedback.  Makes debugging and testing REST services and 
public APIs much easier than with cURL.

# Usage

### Treats the server like a filesystem

```
$ httpsh http://api.twitter.com/1/statuses
api.twitter.com:/1/statuses> get public_timeline.json
Connecting to http://api.twitter.com/a/statuses/publc_timeline.json

HTTP/1.1 200 OK
>content-length: 40945
>vary: Accept-Encoding
>x-transaction-mask: a6183ffa5f8ca943ff1b53b5644ef1140f40ebd7
...
```

### Use familiar shell commands for navigation

```
api.twitter.com:/1/statuses> cd ..
api.twitter.com:/1/> cd /
api.twitter.com:/>
```

### Use relative or absolute paths just like bash 

```
api.twitter.com:/1/statuses> get /1/users/suggestions.json
Connecting to http://api.twitter.com/1/users/suggestions.json

HTTP/1.1 200 OK
...
api.twitter.com:/1/statuses> get public_timeline.json
Connecting to http://api.twitter.com/1/statuses/public_timeline.json

HTTP/1.1 200 OK
...
```

### Pipe output to external commands for formatting, validation, etc.

```
api.twitter.com:/1/statuses> get public_timeline.xml | xmllint --format -
...
<?xml version="1.0" encoding="UTF-8"?>
<statuses type="array">
  <status>
    <created_at>Wed Dec 14 00:57:12 +0000 2011</created_at>
...
```

### Easily post data to a server/service

MongoDB example:

```
localhost:28017:/> post /foo/bar
... { "a" : 123456 }
... 
HTTP/1.0 201 
>content-type: text/plain;charset=utf-8
>connection: close
>x-ns: foo._defaultCollection
>content-length: 15
>x-action: bar

{ "ok" : true }
```

### Use JSON to post to standard web forms using special ```@{}``` notation!

Post to standard web forms by using JSON notation prefaced with 
the "@" character:

```
example.com:/> headers Content-Type:application/x-www-form-urlencoded
example.com::/> post /some/form/handler
... @{
... "name": "Chris",
... "occupation": "Developer"  
... }
```

Converts the JSON definition above to: `name=Chris&occupation=Developer` for
form posting.

### Syntax highlighting

Syntax highlighting of response data for many formats (JSON, XML, HTML, 
Javascript, etc).

![Syntax hilighting](http://i.imgur.com/DxB9P.jpg) 

### Auto-format responses

The ```--format``` command-line parameter will tell httpsh to automatically 
format any JSON or XML response returned by a server.

```
chris@macbookpro:/$ httpsh http://localhost:8888 --format
localhost:8888:/> GET /movies/tt0118715
Connecting to http://localhost:8888/movies/tt0118715

HTTP/1.0 200 OK
<host: localhost:8888
<accept-encoding: identity
>date: Wed, 21 Dec 2011 02:32:18 GMT
>content-type: application/json
>server: RESTless/1.2

{
  "Title": "The Big Lebowski",
  "Rating": 9.5
}
```

### Set headers

```
localhost:28017:/> headers Cookie:session=5cb9586618eea2374377bb1584f7de74
localhost:28017:/> headers User-Agent:AppleWebKit/535.13
localhost:28017:/> headers
<Cookie: session=5cb9586618eea2374377bb1584f7de74
<User-Agent: AppleWebKit/535.13
```

### Remove a header by passing no value

```
localhost:28017:/> headers User-Agent:
localhost:28017:/> headers
<Cookie: session=5cb9586618eea2374377bb1584f7de74
```

### Set and get cookies
```
api.example.com:/> cookies api_key=8e7d1367cb1b466df014ceb2ad1b0202
```

```
www.google.com:/> cookies
Name: PREF
Value: ID=871a0e9212108e48:FF=0:TM=132244474:LM=132121074:S=oVVVAx3_LCZsaPaa
Expires: Fri, 20-Dec-2013 02:37:54 GMT
Domain: .google.com,
Path: /
```

### Tack on query parameters.  

If you're using an API that requires a key tacked on every URL, rather than 
typing it every time set a "tackon" and it will be sent automatically:

```
graph.facebook.com:/> tackons access_token=AAACEcEase0c...
graph.facebook.com:/> tackons
access_token=AAACEcEase0c...

graph.facebook.com:/> get /me
Connecting to https://graph.facebook.com/me?access_token=AAACEcEase0c...

HTTP/1.1 200 OK
...
```

Works for POSTs too:

```
graph.facebook.com:/> post /me/feed
... @{
... "message": "Posting from HttpShell",
... "picture": "http://i.imgur.com/3RPIS.png",
... "link": "https://github.com/chrislongo/HttpShell"
... }
... 
Connecting to https://graph.facebook.com/me/feed?access_token=AAACEcEase0c...

HTTP/1.1 200 OK
...

{"id":"100001681000101_24221026521205"}
```

### OAuth

Will automatically sign requests to APIs that use [OAuth](http://oauth.net/).

[See the wiki for examples](https://github.com/chrislongo/HttpShell/wiki/OAuth-How-To)


### Supports SSL

```
$ httpsh https://www.google.com
www.google.com:/> head
Connecting to https://www.google.com/

HTTP/1.1 200 OK
...
```

# Help
Command line help:

```
usage: httpsh [-h] [-f] [-c] [-i] [--version] URL

An interactive shell for issuing HTTP commands to a web server or REST API

positional arguments:
  URL               url to connect to

optional arguments:
  -h, --help        show this help message and exit
  -f, --format      Attempt to automatically format known mimetypes (JSON or
                    XML)
  -c, --no-cookies  Do not respect cookies sent by host
  -i, --no-headers  Suppress the display of headers
  --version         show program's version number and exit
```

In-app help:

```
Verbs
  head [</path/to/resource>]
  get [</path/to/resource>] [| <external command>]
  post [</path/to/resource>] [| <external command>]
  put [</path/to/resource>] [| <external command>]
  delete </path/to/resource>  [| <external command>]
  options [</path/to/resource>] [| <external command>]
  trace [</path/to/resource>] [| <external command>]
Navigation
  cd </path/to/resource> or ..
  open <url>
Metacommands
  headers [<name>]:[<value>]
  tackons [<name>]=[<value>]
  cookies [<name>]=[<value>]
  debuglevel [#]
  quit
```

# Installation

    $ python setup.py install

Or if pip is installed:

    $ pip install httpshell

May require sudo to install!

