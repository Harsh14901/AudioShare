import time
import subprocess
import os
import sys
from termcolor import colored

def spawn_server():
    try:
        subprocess.Popen('taskkill /IM "CAV_server.exe" /F', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()
    except:
        pass
    time.sleep(1)

    from util import resource_path
    proc = subprocess.Popen(resource_path('CAV_server.exe'),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # for line in iter(proc.stdout.readline, ""):
    #     if b"npm ERR!" in line:
    #         print(colored(line, "red"))
    #         print(
    #             f"[{colored('-','red')}] An error has occured while starting the server\nRestarting the server"
    #         )
    #         os.system("taskkill /IM node /F")
    #         os.system("taskkll /IM npm /F")
    #         sys.exit(-1)
    #     if b"Press CTRL-C to stop" in line:
    #         break

    time.sleep(1)


def kill_dependencies():
    # print(colored('Disconnected','red'))
    # print(colored('Exiting Now, Goodbye!', 'green'))
    subprocess.call('taskkill /IM "node.exe" /F',shell= True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def kill_self():
    subprocess.call(f"taskkill /F /PID {os.getpid()}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def print_qr():
    """ Prints a QR code using the URL that we received from the server. """
    subprocess.Popen('start invite_link.png'.split())
        
def start_server(args):
    from server_comm import ServerConnection
    return ServerConnection(args)