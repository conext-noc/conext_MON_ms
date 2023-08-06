from mon.helpers.request import db_request
from mon.helpers.definitions import endpoints, olt_devices
from mon.helpers.available_ports import available_ports
from mon.helpers.table import clients_table
from mon.scripts.ssh import ssh


def port_data(fsp, olt):
    clients_db = db_request(
        endpoints["get_clients"], {"lookup_type": "VP", "lookup_value": fsp}
    )["data"]
    clients_db = [item for item in clients_db if item["olt"] == int(olt)]
    alarms = db_request(endpoints["get_alarms"], {})["data"]
    ports = available_ports(olt)

    if not any(fsp in item["fsp"] for item in ports):
        return {
            "error": True,
            "message": "this port either doesn't exist or is unavailable/closed",
            "data": None,
        }

    lst = [{"fsp": fsp}]
    (comm, command, quit_ssh) = ssh(olt_devices[str(olt)])
    command("scroll 512")
    clients_port = clients_table(comm, command, lst)

    client_list = [
        {**client, **port}
        for client in clients_db
        for port in clients_port
        if client["fspi"] == port["fspi"]
    ]

    clients = []
    for client in client_list:
        for alarm in alarms:
            if alarm["contract_id"] == client["contract"]:
                res = client.copy()
                res["state"] = "los"
                clients.append(res)
            else:
                clients.append(client)

    los_clients = [item for item in clients if item["state"] == "los"]
    return {"error": False, "message": "success", "data": clients, "los": los_clients}
