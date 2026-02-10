# Requestfile

Human-friendly HTTP requests as plain text files.

[![Python package](https://github.com/rshk/requestfile/actions/workflows/python-package.yml/badge.svg)](https://github.com/rshk/requestfile/actions/workflows/python-package.yml)

## Features

- Store HTTP requests as text files, with a familiar syntax
- Easily specify query arguments, headers, cookies, form data, and file uploads
- Include data from files
- Interpolate variables passed from the command line
- And more!


## Usage

Requestfile can be used as either a command line tool, or as a library
to use the format from third party tools.


## Example

File `request.txt`:

```
POST http://httpbin.org/post
User-Agent: requestfile-example/0.1

%FIELD: username "user@example.com"
%FIELD: password "SuperSecret"
```

```
% requestfile send request.txt
{
  "args": {},
  "data": "",
  "files": {},
  "form": {
    "password": "SuperSecret",
    "username": "user@example.com"
  },
  "headers": {
    "Accept-Encoding": "identity",
    "Content-Length": "48",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "httpbin.org",
    "User-Agent": "requestfile-example/0.1",
  },
  "json": null,
  "origin": "68.516.160.290",
  "url": "http://httpbin.org/post"
}
```

## Quick overview

See [SYNTAX.md](SYNTAX.md) for more details.

Commands to set query parameters, headers, cookies, form fields,
multipart file uploads...

```
# Comments are ignored

POST http://example.com/signup
%PARAM: user_id "100"
%HEADER: x-auth-token <<EOF
th15-15-4-l0ng-s3cr3t-t0k3n
EOF
%COOKIE: session "eyJpZCI6MX0K"

%PARAM: username "admin"
%PARAM: password "TmljZSB0cnkK"|from-base64
%PART: picture <"profile-picture.png"
```


## Passing arguments as variables

Variables can be used anywhere, and passed from the command line!

File `request.txt`:

```
# Edit a user's display name

%SET-DEFAULT: display_name "world"

POST "http://example.com/user/${user_id}"|interpolate
%HEADER: x-auth-token $auth_token

%FIELD: display_name $display_name
%FIELD: greeting "Hello, ${display_name}!"|interpolate
```

Fill in those variables from the command line:


```
requestfile send request.txt -a user_id=1 -a display_name="foobar"
```
