import re
from mon.helpers.handlers import request, spid, port_condition
from mon.helpers.finder import last_down_onu, table
from mon.helpers.constants import definitions, regex_conditions
from mon.helpers.utils import portHandler
from mon.scripts.ssh import ssh

# FUNCTION IMPORT DEFINITIONS
db_request = request.db_request
calculate_spid = spid.calculate_spid
endpoints = definitions.endpoints
olt_devices = definitions.olt_devices
payload = definitions.payload
down_values = last_down_onu.down_values
clients_table = table.clients_table
ports = regex_conditions.ports
vp_count = regex_conditions.vp_count
condition = port_condition.condition
portCounter = portHandler.portCounter
dictToZero = portHandler.dictToZero


def check_pattern(string: str):
    # Define the regular expressions for the patterns
    pattern1 = r"^0/1/0$"
    pattern2 = r"^0/([1-9]|1[0-5])/([0-9]|1[0-5])$"

    # Check if the string matches any of the patterns
    return bool(re.match(pattern1, string) or re.match(pattern2, string))


def is_valid_float(value_str: str):
    try:
        float_value = float(value_str)
        print(float_value)
        return True
    except ValueError:
        return False


def client_ports(data):
    lookup_type = data["lookup_type"]
    lookup_value = data["lookup_value"]

    (comm, command, quit_ssh) = ssh(olt_devices[lookup_value["olt"]])
    command("scroll 512")

    lst = []

    # ERROR HANDLERS:
    valid_float = is_valid_float(str(lookup_value.get("pwr_lim")))

    if lookup_type == "VP" and lookup_value.get("port") is None:
        return {"error": True, "data": None, "message": "missing 'port' parameter"}

    if (
        lookup_type == "VP"
        and lookup_value.get("port") is not None
        and not check_pattern(str(lookup_value.get("port")))
    ):
        return {
            "error": True,
            "data": None,
            "message": "'port' parameter is not a valid port",
        }

    if lookup_value.get("olt") is None:
        return {"error": True, "data": None, "message": "missing 'olt' parameter"}

    if lookup_value.get("pwr_lim") is not None and not valid_float:
        return {
            "error": True,
            "data": None,
            "message": "pwr_lim parameter is not a valid parsable float",
        }

    # LOOKUP PORTS
    payload["lookup_type"] = lookup_type
    payload["lookup_value"] = lookup_value["port"] if "VP" in lookup_type else None

    # PWR LIMIT SCENARIO
    pwr_monitor = bool(lookup_value.get("pwr_lim") is not None)
    pwr_limit = abs(float(lookup_value["pwr_lim"])) if pwr_monitor else None
    lst = (
        [{"fsp": payload["lookup_value"]}]
        if "VP" in lookup_type
        else ports["olt"][str(lookup_value["olt"])]
    )

    CLIENTS = []
    SUMMARY = []
    req = db_request(endpoints["get_clients"], payload)
    if req["error"]:
        return {"error": True, "message": "an error occurred", "data": None}

    clients = req["data"]
    client_list = clients_table(comm, command, lst)

    for client in clients:
        for client_lst in client_list:
            if client["fspi"] == client_lst["fspi"]:
                name = f"{client['name_1']} {client['name_2']} {client['contract']}"
                client["name"] = name
                client["pwr"] = client_lst["pwr"]
                client["status"] = client_lst["status"]
                client["last_down_time"] = client_lst["last_down_time"]
                client["last_down_date"] = client_lst["last_down_date"]
                client["last_down_cause"] = client_lst["last_down_cause"]
                alert = condition(client)
                portCounter(alert, client["plan_name_id"])
                vp_count["1"]["vp_ttl"] += 1
                if lookup_type == "CA" and alert in ["los", "los+"]:
                    CLIENTS.append(client)
                if lookup_type == "DT" and alert in ["suspended", "suspended+"]:
                    CLIENTS.append(client)
                if lookup_type in ["VT", "VP"]:
                    CLIENTS.append(client)

    SUMMARY = {
        "ttl": vp_count["1"]["vp_ttl"],
        "active": vp_count["1"]["vp_active_cnt"],
        "deactivated": vp_count["1"]["vp_deactive_cnt"],
        "los": vp_count["1"]["vp_los_cnt"],
        "off": vp_count["1"]["vp_off_cnt"],
        "vnet": vp_count["2"]["vp_vnet"],
        "inter": vp_count["2"]["vp_inter"],
        "public_ip": vp_count["2"]["vp_public_ip"],
        "OZ_0": vp_count["2"]["OZ_0"],
        "OZ_MAX": vp_count["2"]["OZ_MAX"],
        "OZ_SKY": vp_count["2"]["OZ_SKY"],
        "OZ_MAGICAL": vp_count["2"]["OZ_MAGICAL"],
        "OZ_NEXT": vp_count["2"]["OZ_NEXT"],
        "OZ_PLUS": vp_count["2"]["OZ_PLUS"],
        "OZ_DEDICADO": vp_count["2"]["OZ_DEDICADO"],
        "OZ_CONECTA": vp_count["2"]["OZ_CONECTA"],
        "NA": vp_count["2"]["NA"],
    }

    dictToZero(vp_count["1"])
    dictToZero(vp_count["2"])

    quit_ssh()

    return {
        "error": False,
        "message": "success",
        "data": {"clients": CLIENTS, "summary": SUMMARY},
    }
