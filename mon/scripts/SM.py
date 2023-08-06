from mon.helpers.request import db_request
from mon.helpers.definitions import endpoints


def summary_data():
    clients = db_request(
        endpoints["get_clients"], {"lookup_type": "VT", "lookup_value": None}
    )
    clients_alarms = len(db_request(endpoints["get_alarms"], {})["data"])

    def clients_state_qty(state):
        return len([item for item in clients["data"] if item["state"] == state])

    def clients_plan_qty(plan_name):
        return len(
            [item for item in clients["data"] if plan_name in item["plan_name_id"]]
        )

    return {
        "error": False,
        "message": "success",
        "data": {
            "ttl": clients_state_qty("active") + clients_state_qty("deactivated"),
            "active": clients_state_qty("active"),
            "deactivated": clients_state_qty("deactivated"),
            "los": clients_alarms,
            "vnet": clients_plan_qty("_2"),
            "inter": clients_plan_qty("_1"),
            "public_ip": clients_plan_qty("_IP"),
            "OZ_0": clients_plan_qty("OZ_0"),
            "OZ_MAX": clients_plan_qty("OZ_MAX"),
            "OZ_SKY": clients_plan_qty("OZ_SKY"),
            "OZ_MAGICAL": clients_plan_qty("OZ_MAGICAL"),
            "OZ_NEXT": clients_plan_qty("OZ_NEXT"),
            "OZ_PLUS": clients_plan_qty("OZ_PLUS"),
            "OZ_DEDICADO": clients_plan_qty("OZ_DEDICADO"),
            "OZ_CONECTA": clients_plan_qty("OZ_CONECTA"),
            "NA": clients_plan_qty("NA"),
        },
    }
