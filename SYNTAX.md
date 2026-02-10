# Requestfile syntax

The aim of `requestfile` is to provide a familiar interface for
writing HTTP requests as plain text files.


## Basic syntax

The basic request syntax closely resembles that of a HTTP request.

The first line contains the HTTP method and URL (not just path!), for
example:

```
GET http://example.com
GET "http://example.com?query=some%20search%20query"
POST "http://example.com/login"
```

Note that quoting is optional for simple strings, with no whitespaces
and symbols limited to `_-:/.`. For more complex strings, quoting is
recommended.

Headers can be specified in familiar `key: value` syntax.

A single blank line marks the end of the headers and the start of the
request body.

Example GET request:

```
GET "http://example.com?query=some%20search%20query"
```

Example POST request, with form data and a header:

```
POST http://example.com/login
x-im-not-a-bot: true
Content-type: application/x-www-form-urlencoded

username=admin&password=Passw0rd1
```

> [!NOTE]
> Note that `requestfile`s are meant to be (utf-8 encoded) plain text,
> so requestfiles containing "verbatim" binary data are not supported.
> Read along on how to properly include binary data in a request.


## Commands

The main strength of `requestfile` comes from the use of _commands_,
which provide a convenient interface for defining parts of the
request.

In general, commands take the form of a `%`-prefixed identifier,
followed by zero or more arguments.

For example, one can define the value of a "form" field like this:

```
%FIELD: name "some value"
```

Command names are case-insensitive.

## Argument types


### Unquoted strings

Any strings starting and ending with a letter or number, and only
containing letters, numers, or the symbols `_-:/.` can be written
unquoted.


### Quoted strings

More complex strings can be enclosed in double quoted. Special
characters can be represented using the familiar backslash-prefixed
"escape" character syntax common in many languages.

In particular, the `\n`, `\r`, `\t`, `\e` (ESCAPE), `\0` (NULL)
characters are supported, along with `\\` (literal backslash) and `\"`
(literal double-quote character).

One-byte non-printable characters can be represented as `\xXX` where
`XX` are two hexadecimal digits.

Unicode characters can be represented as `\uXXXX` or `\UXXXXXXXX`.


### Heredoc strings

Longer strings of text, spanning multiple lines, can be entered using
the "heredoc" syntax from Bash or Perl.

Example:

```
%INCLUDE: <<EOF
Some text
Spanning multiple
Lines
EOF
```

The label following `<<` can be any string following the rules for
unquoted strings above. When found on its own on a single line, it
indicates the end of the text is reached.


### File inclusions

To include data from a file (either binary or string), use the `<path`
or `<"path"` syntax.

Example:

```
%INCLUDE: <"/home/myuser/picture.jpg"
```


### Variables

Variables can also be used to store data and reuse in multiple places
(see the `%SET` and `%SET-DEFAULT` commands).

Example:

```
%SET: myPassword "SuperSecret"
%FIELD: password $myPassword
```

## Argument filters

Filters can be used to further modify the content of an argument.

For example, if we want to include some binary data verbatim in a
requestfile, we can use:

```
%INCLUDE: <<EOF|from-base64
... include your b64 encoded data here ...
EOF
```

## Comments

Any line starting with `# ` will be interpreted as a comment and ignored.


## Commands available everywhere

### `%SET` - set the value of a variable

Syntax: `%SET: <name> <value>`

### `%SET-DEFAULT` - set the default value of a variable

Syntax: `%SET-DEFAULT: <name> <value>`

## Header commands

### `%PARAM` - set a query parameter

Syntax: `%PARAM: <name> <value>`

### `%HEADER` - set a request header

Syntax: `%HEADER: <name> <value>`

### `%COOKIE` - set a request cookie

Syntax: `%COOKIE: <name> <value>`

## Body commands

### `%INCLUDE` - include text or data

Syntax: `%INCLUDE: <value>`

### `%FIELD` - specify a form field

Syntax: `%FIELD: <name> <value>`

### `%PART` - for multipart file uploads

Syntax: `%PART: <name> [<filename>] [<mimetype>] [<headers>] <value>`

Optional arguments `filename`, `mimetype`, `headers` can be specified
positionally or prefixed with the argument name.

For example, all of these are equivalent:

```
%PART: myfile "hello.txt" "text/plain" "Hello World"
%PART: myfile filename="hello.txt" mimetype="text/plain" "Hello World"
%PART: myfile mimetype="text/plain" filename="hello.txt" "Hello World"
%PART: myfile "hello.txt" "text/plain" <<EOF
Hello World
EOF
```

Specifying part headers:

```
%PART: myfile headers=<<HEADERS <<DATA
X-Some-Header: value
X-Other-Header: other value
HEADERS
This is the part data
DATA
```

Using a HEREDOC string is recommended for passing multiple
headers. They will be parsed automatically from any passed-in text.


## Builtin filters

- `base64`, `from-base64` encodes / decodes data using base64
- `urlquote`, `urlunquote` encodes / decodes data using URL
  percent-encoding
- `text` loads utf-8 encoded binary data into a unicode string
- `interpolate` interpolate variables in the argument value, using
  `$name` or `${name}` syntax.
