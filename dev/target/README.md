# Target webserver for testing

## Start a server

From the `dev/target` directory:

```
python -m http.server 8880
```

## Start mitmproxy

```
mitmproxy -p 8888
```

## Send a request

```
http_proxy=http://localhost:8888 requestfile send samples/dev-get
```

Or, if you're running the "target" server on a different port (eg. `8000`)

```
http_proxy=http://localhost:8888 requestfile send samples/dev-get -a target=http://localhost:8000
```

> [!NOTE]
> If you're running commands from a local copy of the git repo
> (installed with `uv sync`), you'll need to prefix the `requestfile`
> command with `uv run`, for example:
>
> ```
> http_proxy=http://localhost:8888 uv run requestfile send samples/dev-get
> ```


## Comparing requests

The goal when developing a `requestfile from ...` command is to make
the generated requestfile make an HTTP request that matches the
original request from the original tool as closely as possible.

To test that using CURL, you can for example use the following
commands:

```
export http_proxy=http://localhost:8888
curl -X POST http://localhost:8880/post -F foo=Hello -F bar=World

requestfile from curl -X POST http://localhost:8880/post -F foo=Hello -F bar=World > req.txt
requestfile send req.txt
```

Then compare the two received requests in `mitmproxy` to ensure
they're equivalent.
