# Requestfile syntax overview

**WARNING:** This document is still a very experimental draft. Things
are subject to change!

## Basic requests

At its core, a Requestfile looks very much like a raw HTTP request.

The first line contains the method and URL (http version is specified
elsewhere, as one request can be sent with many different protocols).

### Minimal GET request

```
GET http://example.com
```

### GET request with arguments and headers

```
GET http://example.com?foo=1&bar=2
Accept: application/json
```

### POST request with JSON body

```
POST http://example.com/login
Content-type: application/json

{"username": "foo", "password": "bar"}
```

### POST request, with form data

```
POST http://example.com/path/to/page
Accept: application/json
User-Agent: SomeAgent/1.0
Content-Type: application/x-www-form-urlencoded; charset=utf-8

foo=1&bar=aa&baz=hello%26world%3D
```

### POST request, with multipart form data

This is for a form containing a file upload.

But of course, typing all this out is starting to get quite cumbersome...

```
POST http://example.com/upload
Content-Type: multipart/form-data; boundary=fb289e5fd8894053b02ee373017311ad

--fb289e5fd8894053b02ee373017311ad
Content-Disposition: form-data; name="username"

foo@example.com
--fb289e5fd8894053b02ee373017311ad
Content-Disposition: form-data; name="password"

foo&bar^baz=quux!
--fb289e5fd8894053b02ee373017311ad
Content-Disposition: form-data; name="bio"

This is my complete biography.
As you can see, it's a fairly long bit of text.
--fb289e5fd8894053b02ee373017311ad
Content-Disposition: form-data; name="picture"; filename="image.jpg"
Content-Type: image/jpeg

<binary data suppressed>

--fb289e5fd8894053b02ee373017311ad--
```

## Friendlier syntax

The real power of Requestfile comes from the "commands" syntax, which
allows us to write things out in a more human-friendly way.

### Query parameters

For example, instead of manually url-encoding query parameters in the
URL, we can use the `%PARAM` command:

```
GET http://example.com/search
%PARAM: query "This is a search query"
%PARAM: path "/path/to/file.txt"
Accept: application/json
User-Agent: SomeAgent/1.0
```

Which is equivalent to:

```
GET http://example.com/search?query=This+is+a+search+query&path=%2Fpath%2Fto%2Ffile.txt
Accept: application/json
User-Agent: SomeAgent/1.0
```

### Headers

Use the `%HEADER` command to conveniently encode headers:

```
%HEADER x-some-header "My header value"
```

The benefit of later will come apparent soon, as you'll see
alternative ways of passing arguments to commands.


### Cookies

Use the `%COOKIE` command to add a cookie to the `Cookie:` header:

```
%COOKIE my-cookie "The cookie value"
```


### Form data

Use the `%CONTENT-TYPE` to tell the parser we want to interpret
commands in the "body" section, as opposed to loading it as raw text
(the default).

```
POST http://example.com/login
%CONTENT-TYPE: form

%FIELD: username "user@example.com"
%FIELD: password "foo&bar^baz=quux!"
```

### File upload

Compare this to the "raw request" example above:

```
POST http://example.com/upload
%CONTENT-TYPE: multipart

%FIELD: username "foo@example.com"
%FIELD: password "foo&bar^baz=quux!"
%FIELD: bio <<END-OF-BIO
This is my complete biography.
As you can see, it's a fairly long bit of text.
END-OF-BIO
%PART: picture filename="image.jpg" mimetype="image/jpeg" <"/path/to/image.jpg"
```

The `<"path"` syntax means "load from file".

If not explicitly provided, the file name and mime type will be
guessed from the file being uploaded.

### Embed file content

```
%PART: textfile filename="plain.txt" mimetype="text/plain" <<EOF
Hello world
EOF
```

### Base64-encoded file content

This is useful for binary data

```
%PART: picture filename="teal.png" mimetype="image/png" <<EOF|from-base64
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQAQMAAAAlPW0iAAAAIGNIUk0AAHomAACAhAAA+gAAAIDo
AAB1MAAA6mAAADqYAAAXcJy6UTwAAAAGUExURQBNQP///56uWxgAAAABYktHRAH/Ai3eAAAAB3RJ
TUUH6gIKDyYvDSXYAAAAAAxJREFUCNdjYCANAAAAMAABx6qFjgAAAABJRU5ErkJggg==
EOF
```

## Ways to specify arguments

### Symbol

Symbols are simple strings that do not need quoting,
i.e. strings not containing any spaces, and only using a handful of
allowed characters.

The exact character set is subject to change, currently this regex is
used for matching:

```
/[a-zA-Z_\/]([a-zA-Z0-9_:\/\.-]*[a-zA-Z0-9_\/])?/
```

### Quoted

If you need to use spaces, or more characters than the above, put the
value in double quotes.

Standard C-style escape characters are supported:

- `\\` -> `\`
- `\"` -> `"`
- `\n`, `\r`, `\t`, etc...
- `\xXX` to specify a single byte character
- `\uXXXX` to specify a two-byte unicode character
- `\UXXXXXXXX` to specify a four-byte unicode character


### Heredoc

Similar to Bash / Perl syntax: `<<MARKER` will read lines until a line
only containing `MARKER` is found. The marker string can be any Symbol
(see above).

Multiple arguments can use Heredoc arguments; they will be read in the
order they are specified, for example:

```
%HEADER <<KEY <<VALUE
foo
KEY
bar
VALUE
```

Is equivalent to:

```
%HEADER "foo" "bar"
```

or

```
%HEADER foo bar
```


### File input

Use the Shell-like `<path` syntax to load the argument from a file.

Simple paths that can fit in a symbol can be passed inline, but
double-quoting is recommended for more complex paths:

```
<path/to/file.txt
<"/path/to/some other file.pdf"
```

### Variables

While not yet supported, there are plans to add support for variables
using the `$name` syntax.

Variables can be set using the `%SET` command:

```
%SET csrf-token "sFoQOSh+vO+y1mG6H6Rt5elFvuk="
%HEADER: x-csrf-token $csrf-token

%FIELD: csrf_token $csrf-token
```

There currently are no plans for variable interpolation support inside
other argument types, but it might be added in the future.

A mechanism for loading variables from environment or command line
arguments is also in the works.


## Filters

Most arguments can be "filtered" with a series of built-in filters.

To apply a filter, simply use the `<value>|<filter>` syntax, eg:

```
"aGVsbG8="|from-base64
```

Multiple filters can be chained:

```
"aGVsbG8="|from-base64|urlencode
```
