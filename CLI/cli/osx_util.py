import time
import subprocess
import os
import sys
from termcolor import colored


def spawn_server():
    os.system("killall CAV_server > /dev/null 2>&1")
    os.system("killall -9 vlc > /dev/null 2>&1")
    time.sleep(1)

    from util import resource_path

    proc = subprocess.Popen(
        resource_path("CAV_server"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    for line in iter(proc.stdout.readline, ""):
        if b"npm ERR!" in line:
            print(colored(line, "red"))
            print(
                f"[{colored('-','red')}] An error has occured while starting the server\nRestarting the server"
            )
            os.system("killall node")
            os.system("killall npm")
            sys.exit(-1)
        if b"Press CTRL-C to stop" in line:
            break

    time.sleep(1)


def kill_dependencies():
    os.system("killall node 2> /dev/null")
    os.system("killall npm 2> /dev/null")
    os.system("killall CAV_server")


def kill_self():
    sys.exit(0)


def print_qr():
    """ Prints a QR code using the URL that we received from the server. """
    subprocess.Popen("open invite_link.png".split())


def start_server(args):
    from server_comm import ServerConnection

    return ServerConnection(args)


def get_ffmpeg():
    return "ffmpeg"
