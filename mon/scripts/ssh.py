import os
from time import sleep
import paramiko
from dotenv import load_dotenv
load_dotenv()



def ssh(ip):
    count = 1
    delay = 0.8
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    comm = None
    cont = True

    # Handling multiple SSH sessions
    while cont and count <= 3:
        try:
            username = os.environ[f"user_{count}"]
            password = os.environ[f"password_{count}"]
            port = os.environ["port"]
            conn.connect(ip, port, username, password)
            comm = conn.invoke_shell()
            cont = False
        except paramiko.ssh_exception.AuthenticationException:
            cont = True
            count += 1
            continue
        break
    
    def enter():
        comm.send(" \n")
        comm.send(" \n")
        sleep(delay)

    def command(cmd):
        print(cmd)
        comm.send(cmd)
        sleep(delay)
        enter()

    def quit():
        conn.close()

    if ip == "181.232.180.5" or ip == "181.232.180.6" or ip == "181.232.180.7":
        command("enable")
        command("config")
        command("scroll 512")
    else:
        command("sys")

    return (comm, command, quit)
