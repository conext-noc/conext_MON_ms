from mon.helpers.request import db_request
from mon.helpers.definitions import endpoints


def all_clients(olt):
    clients = db_request(
        endpoints["get_clients"], {"lookup_type": "VT", "lookup_value": {"olt":olt}}
    )["data"]

    return {"error": False, "message": "success", "data": clients}
