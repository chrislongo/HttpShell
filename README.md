# Info

An interactive shell for issuing HTTP commands to a web server or REST API.

![A picture of httpsh in action](http://i.imgur.com/3RPIS.png)

Issue HTTP commands (HEAD, GET, POST, PUT, DELETE) to a server with visual
feedback.   Makes debugging REST services much more interactive than cURL.

# Features

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
api.twitter.com:/1/statuses> get public_timeline.xml | xmllint -format -
...
<?xml version="1.0" encoding="UTF-8"?>
<statuses type="array">
  <status>
    <created_at>Wed Dec 14 00:57:12 +0000 2011</created_at>
...
```

Post data to server:

```
$ httpsh http://localhost:28017
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

# Installation

    $ python setup.py install

May require sudo!
