# Info

An interactive shell for issuing HTTP commands to a web server or REST API.

![A picture of httpsh in action](http://i.imgur.com/3RPIS.png)

Issue HTTP commands (HEAD, GET, POST, PUT, DELETE) to a server with visual
feedback.   Makes debugging REST services much more interactive than cURL.

# Usage

Treats the server like a filesystem:

```
$ httpsh http://api.twitter.com/a/statuses
api.twitter.com:/1/statuses> get public_timeline.json

HTTP/1.1 200 OK
>content-length: 40945
>vary: Accept-Encoding
>x-transaction-mask: a6183ffa5f8ca943ff1b53b5644ef1140f40ebd7
...
```

Use familiar shell commands:

```
api.twitter.com:/1/statuses> cd ..
api.twitter.com:/1/> cd /
api.twitter.com:/>
```

Pipe output to external commands for formatting, etc:

```
api.twitter.com:/1/statuses> get public_timeline.xml | xmllint --format -
...
<?xml version="1.0" encoding="UTF-8"?>
<statuses type="array">
  <status>
    <created_at>Wed Dec 14 00:57:12 +0000 2011</created_at>
...
```

Post data to server:

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

Use JSON to post to web forms using special "@{}" notation!

```
somewebsite:/> headers Content-Type:application/x-www-form-urlencoded
somewebsite:/> post /some/form/handler
... @{
... "name": "Chris",
... "occupation": "Developer"  
... }
```

Converts the JSON definition above to: `name=Chris&occupation=Developer` for
form posting.

Set headers:

```
localhost:28017:/> headers Cookie:session=5cb9586618eea2374377bb1584f7de74
localhost:28017:/> headers User-Agent:AppleWebKit/535.13
localhost:28017:/> headers
<Cookie: session=5cb9586618eea2374377bb1584f7de74
<User-Agent: AppleWebKit/535.13
```

Remove header by passing no value:

```
localhost:28017:/> headers User-Agent:
localhost:28017:/> headers
<Cookie: session=5cb9586618eea2374377bb1584f7de74
```

Supports SSL

```
$ httpsh https://www.google.com
www.google.com:/> head
Connecting to https://www.google.com/

HTTP/1.1 200 OK
...
```

# Help

```
Verbs
  head [</path/to/resource>]
  get [</path/to/resource>] [| <external command>]
  post [</path/to/resource>] [| <external command>]
  put [</path/to/resource>] [| <external command>]
  delete </path/to/resource> [| <external command>]
Navigation
  cd </path/to/resource> or ..
  open <url>
Metacommands
  headers [<name>]:[<value>]
  quit
```

# Installation

    $ python setup.py install

Or if pip is installed:

    $ pip install httpshell

May require sudo to install!
