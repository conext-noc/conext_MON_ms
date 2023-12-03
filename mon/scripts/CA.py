from mon.helpers.request import db_request
from mon.helpers.definitions import endpoints


def alarms_data(olt):
    alarms = db_request(endpoints["get_alarms"], {"lookup_type": "CA", "lookup_value": {"olt":olt}})["data"]
    clients = db_request(
        endpoints["get_clients"], {"lookup_type": "VT", "lookup_value": {"olt":olt}}
    )["data"]
    merged_list = [
        {**client, **alarm}
        for client in clients
        for alarm in alarms
        if client["contract"] == alarm["contract_id"]
    ]

    return {
        "error": False,
        "message": "success",
        "data": merged_list,
    }
