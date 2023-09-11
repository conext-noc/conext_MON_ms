import re
from time import sleep
from mon.helpers.decoder import decoder, check_iter
from mon.helpers.fail import fail_checker
from mon.helpers.file_formatter import data_to_dict
from mon.helpers.regex_conditions import condition_port_summary, port_summary


def clients_table(comm, command, lst):
    value = decoder(comm)
    clients = []
    for idx, lt in enumerate(lst):
        fsp = lt["fsp"]
        FRAME = int(fsp.split("/")[0])
        SLOT = int(fsp.split("/")[1])
        PORT = int(fsp.split("/")[2])
        command(f"display ont info summary {fsp} | no-more")
        sleep(2.5)
        value = decoder(comm)
        fail = fail_checker(value)
        if fail is None:
            states_summary = []
            names_summary = []
            re_summ = check_iter(value, condition_port_summary)
            for op in port_summary:
                name = op["name"]
                start = op["start"]
                end = op["end"]
                header = op["header"]
                (_, s) = re_summ[start]
                (e, _) = re_summ[end]
                if name == "names":
                    names_summary = data_to_dict(header, value[s:e])
                else:
                    states_summary = data_to_dict(header, value[s:e])
            for status, names in zip(states_summary, names_summary):
                if int(status["onu_id"]) == int(names["onu_id"]):
                    name = ""
                    for i in range(1, 4):
                        name += str(names[f"name{i}"]) + " "
                    clients.append(
                        {
                            "fsp": fsp,
                            "fspi": f'{fsp}/{status["onu_id"]}',
                            "frame": FRAME,
                            "slot": SLOT,
                            "port": PORT,
                            "onu_id": status["onu_id"],
                            "name": str(re.sub(" +", " ", name).replace("\n", "").strip()),
                            "status": str(status["state"]),
                            "last_down_time": str(status["down_time"]),
                            "pwr": str(names["rx_tx_power"].split("/")[0]),
                            "last_down_date": str(status["down_date"]),
                            "last_down_cause": str(status["down_cause_1"]),
                            "sn": names["sn"],
                            "device": names["device"],
                        }
                    )
        else:
            continue
    return clients
