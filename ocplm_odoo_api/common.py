"""Common methods"""
import werkzeug.wrappers
import logging
_logger = logging.getLogger(__name__)

try:
    import simplejson as json
    from simplejson.errors import JSONDecodeError
except ModuleNotFoundError as identifier:
    _logger.error(identifier)
else:
    import json


def valid_response(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    data = {"message": data,"code":status}
    va_data = werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(data),
    )
    return va_data


def invalid_response(typ, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    # return json.dumps({})
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(
            {
                "message": str(message)
                if str(message)
                else "wrong arguments (missing validation)",
                "code":status
            }
        ),
    )


def extract_arguments(payload, offset=0, limit=0, order=None):
    """."""
    fields, domain = [], []
    
    data = str(payload.get("domain"))[2:-2]
    data_list=data.split(',')
    if len(data_list)%3==0:
        domain.append(tuple([data_list[0], data_list[1], data_list[2]]))
    else:
        domain=[]
    if payload.get("fields"):
        fields = payload.get("fields")
    if payload.get("offset"):
        offset = int(payload.get("offset"))
    if payload.get("limit"):
        limit = int(payload.get("limit"))
    if payload.get("order"):
        order = payload.get("order")
    return [domain, fields, offset, limit, order]
