# Info

An interactive shell for issuing HTTP commands to a web server or REST API.

![A picture of httpsh in action](http://i.imgur.com/3RPIS.png)

Issue HTTP commands (HEAD, GET, POST, PUT, DELETE) to a server with visual
feedback.   Makes debugging REST services much more interactive than cURL.

# Usage

###Treats the server like a filesystem

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

###Use relative or absolute paths just like bash 

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

###Use familiar shell commands

```
api.twitter.com:/1/statuses> cd ..
api.twitter.com:/1/> cd /
api.twitter.com:/>
```

###Pipe output to external commands for formatting, etc.

```
api.twitter.com:/1/statuses> get public_timeline.xml | xmllint --format -
...
<?xml version="1.0" encoding="UTF-8"?>
<statuses type="array">
  <status>
    <created_at>Wed Dec 14 00:57:12 +0000 2011</created_at>
...
```

###Post data to server

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

###Use JSON to post to web forms using special "@{}" notation!

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

###Set headers

```
localhost:28017:/> headers Cookie:session=5cb9586618eea2374377bb1584f7de74
localhost:28017:/> headers User-Agent:AppleWebKit/535.13
localhost:28017:/> headers
<Cookie: session=5cb9586618eea2374377bb1584f7de74
<User-Agent: AppleWebKit/535.13
```

###Remove header by passing no value

```
localhost:28017:/> headers User-Agent:
localhost:28017:/> headers
<Cookie: session=5cb9586618eea2374377bb1584f7de74
```

###Tack on query parameters.  

If you're using an API that requires a key tacked on every URL rather than 
typing it every time set a tack on and it will be send automatically:

```
example.com:/> tackons apikey=8821f6c8df5265e99d36cf5a3971d667
example.com:/> tackons
apikey=8821f6c8df5265e99d36cf5a3971d667
example.com:/> head /api/1/user
Connecting to http://example.com/api/1/user?apikey=8821f6c8df5265e99d36cf5a3971d667

HTTP/1.1 200 OK
...
```

Or use headers to send OAuth to Twitter, etc:

```
$ httpsh https://api.twitter.com/1/statuses/mentions.json?include_entities=true
api.twitter.com:/1/statuses/mentions.json> headers Authorization: OAuth oauth_consumer_key="...", oauth_nonce="...", oauth_signature="...", oauth_signature_method="HMAC-SHA1", oauth_timestamp="1324040697", oauth_token="...", oauth_version="1.0"
api.twitter.com:/1/statuses/mentions.json> get
Connecting to https://api.twitter.com/1/statuses/mentions.json?include_entities=true

HTTP/1.1 200 OK
...
```

###Supports SSL

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
  tackons [<name>]:[<value>]
  quit
```

# Installation

    $ python setup.py install

Or if pip is installed:

    $ pip install httpshell

May require sudo to install!
