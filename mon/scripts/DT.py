from mon.helpers.request import db_request
from mon.helpers.definitions import endpoints


def deactivates_data():
    clients = db_request(
        endpoints["get_clients"], {"lookup_type": "VT", "lookup_value": None}
    )["data"]

    clients_deactivated = [item for item in clients if item["state"] == "deactivated"]

    return {
        "error": False,
        "message": "success",
        "data": clients_deactivated,
    }
