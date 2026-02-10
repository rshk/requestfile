import io

from requests_toolbelt.utils import dump

from requestfile.builder.request import Request as GenericRequest
from requestfile.builder.request import RequestContentType
from requests import Request, Response, Session


def build_requests_request(grq: GenericRequest) -> Request:
    req = Request(
        method=grq.method,
        url=grq.url,
        params=grq.params,
        cookies=grq.cookies,
        headers=grq.headers,
    )

    if grq.content_type in (RequestContentType.BYTES, RequestContentType.TEXT):
        req.data = grq.raw_body
    else:
        req.data = grq.fields

        # IMPORTANT! The requests library doesn't seem to support a
        # way to specify two files with the same name, so only one
        # will be kept.
        # This is usually not critical, but something to keep in mind.

        req.files = {
            part.name: (part.filename, part.body, part.mimetype, part.headers)
            for part in grq.files.values()
        }

    return req


def send(req: Request | GenericRequest) -> Response:
    if isinstance(req, GenericRequest):
        req = build_requests_request(req)
    return Session().send(req.prepare())


def dump_request(req: Request) -> bytearray:
    prefixes = dump.PrefixSettings("", "")
    data = bytearray()
    dump._dump_request_data(req.prepare(), prefixes, data)
    return data


def dump_response(resp: Response) -> bytearray:
    prefixes = dump.PrefixSettings("", "")
    data = bytearray()
    dump._dump_response_data(resp, prefixes, data)
    return data


def dump_request_text(req: Request) -> str:
    data = dump_request(req)
    return _reqresp_data_to_string(data)


def dump_response_text(resp: Response) -> str:
    data = dump_response(resp)
    return _reqresp_data_to_string(data)


def _reqresp_data_to_string(raw: bytearray) -> str:
    output = io.StringIO()
    data = raw.split(b"\r\n\r\n", 1)
    headers = data[0].decode()
    output.write(headers)
    output.write("\r\n\r\n")  # We stripped this earlier
    body = ""
    if len(data) > 1:
        try:
            body = data[1].decode()
        except UnicodeDecodeError:
            body = f"[binary data not shown ({len(data[1])} bytes)]\n"
    output.write(body)
    return output.getvalue()


def dump_reqresp(resp: Response) -> bytearray:
    return dump.dump_response(resp)
