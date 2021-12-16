import socket
import subprocess
import time
import re
import json
from util import send_until_writable, wait_until_error, path2title
from audio_extract import get_duration
import os
from termcolor import colored
from urllib.parse import unquote

PORT = 1234


class VLCplayer:  # Class that manages the VLC player instance on the machine.
    def __init__(self, port=PORT):
        self.port = port
        self.proc = None

    @wait_until_error
    def readState(self):
        """ This reads the JSON state from cache of the video that is currently playing """

        return json.loads(open("cache", "r").read())

    def launch(self):
        """ Launches a VLC instance """

        bashCommand = "vlc --extraintf rc --rc-host localhost:%d -vv --one-instance" % (
            self.port)

        # Start a subprocess to execute the VLC command
        self.proc = subprocess.Popen(
            bashCommand.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        # Create a socket connection to the RC interface of VLC that is listening for commands at localhost:1234
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ("localhost", self.port)
        wait_until_error(self.sock.connect, timeout=-1)(self.server_address)

        # Dump any trash data like welcome message that we may recieve from the server after connecting
        self.sock.recv(1024)

    """ The following functions send a specific command to the VLC instance using the socket connection """

    def play(self):
        message = "play\n".encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def pause(self):
        message = "pause\n".encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def seek(self, position):
        message = f"seek {position}\n".encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def enqueue(self, filePath):
        message = f"enqueue {filePath}\n".encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def faster_playback(self):
        message = "faster\n".encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def slower_playback(self):
        message = "slower\n".encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def update(self, server):
        """ Keeps the VLC instance state updated by parsing the VLC logs that are generated """
        parse_logs(self, server)

    def getState(self):
        """ Interprets the dumped data in cache
        by calculating the live position of the video from the last_updated
        and postition keys in the data. It returns the live state of the video """

        player = self
        state = player.readState()
        if state is None:
            return
        if "last_updated" in state.keys():
            initial_pos = state["position"]
            extra = (
                time.time() - float(state["last_updated"]
                                    ) if state["is_playing"] else 0
            )
            final_pos = initial_pos + extra
            state["position"] = final_pos
            state.pop("last_updated")
            return state


def on_start(match, state, server):

    file = unquote(match.groups()[0])

    state["path"] = file
    state["title"] = path2title(file)
    state["duration"] = get_duration(file) * 1000
    state["is_playing"] = True
    state["position"] = 0.0
    state["last_updated"] = time.time()

    server.track_change(videoPath=file, state=state)


def on_stop(match, state, server):
    state["is_playing"] = False
    try:
        del state["duration"]
    except:
        print("No duration found")
    try:
        del state["path"]
        del state["title"]
    except:
        print("No path found")

    state["position"] = 0.0
    state["last_updated"] = time.time()


def on_play(match, state, server):
    if not state["is_playing"]:
        state["is_playing"] = True
        state["last_updated"] = time.time()
        server.send("play", state)


def on_pause(match, state, server):
    if state["is_playing"]:
        state["is_playing"] = False
        state["position"] = (
            player.getState()[
                "position"] if player.getState() is not None else 0
        )
        state["last_updated"] = time.time()
        server.send("pause", state)


def on_seek(match, state, server):
    match = match.groups()[0] or match.groups()[1]
    if "i_pos" in match:
        # Match is the absolute duratoin
        match = match.split("=")[1].strip()
        state["position"] = float(match) / 1000000.0
        state["last_updated"] = time.time()

    # This is used when seek occurs through the slider
    elif "%" in match:
        # Match is the percentage of the total duration
        match = match[:-1]
        state["position"] = float(match) * float(state["duration"]) / 100000.0
        state["last_updated"] = time.time()

    # this is for mp4 files
    else:
        state["position"] = int(match) / 1000
        state["last_updated"] = time.time()
    # server.send("seek", state)


def on_seek_complete(match, state, server):
    state["last_updated"] = time.time()
    server.send("seek", state)


def get_regex_match(line):
    for regex in REGEX_DICT:
        match = re.search(regex, line)
        if match:
            return regex, match
    return None, None


REGEX_DICT = {
    "seek request to (.*)%*$": on_seek,
    "toggling resume$": on_pause,
    "toggling pause$": on_play,
    "main input debug: `file://(.*)' successfully opened": on_start,
    "dead input": on_stop,
    "Stream buffering done": on_seek_complete,
}


def parse_logs(player, server):
    """ A function that is to be run in a seperate process to parse VLC logs
    and get user events like START,STOP,PLAY,PAUSE,SEEK and accordingly respond
    by sending the data to the server. """

    # import server_comm
    # Another instance to send the data since somehow sockets were inaccessible by this process
    # other_connection = server_comm.ServerConnection()

    state = player.readState()
    if state is None:
        state = {}

    # Continuosly read the VLC logs
    for line in iter(player.proc.stdout.readline, ""):

        regex, match = get_regex_match(line)
        if match:
            REGEX_DICT[regex](match, state, server)

        # Dump the parsed data into cache
        open("cache", "w").write(json.dumps(state))


player = VLCplayer()
