import socketio
import time
import os

from util import path2title, platform_dependent
from termcolor import colored

SERVER_ADDR = "localhost"

# this is used internally by ServerConnection
class SignalReceiver(socketio.ClientNamespace):

    def __init__(self, *args , **kwargs):
        self.ARGS = kwargs['params']
        del kwargs['params']
        super().__init__(*args ,**kwargs)

    def on_createRoom(self, *args, **kwargs):
        self.roomId = args[0]["roomId"]

        url = "http://%s:5000/client/stream/?roomId=%s"
        if self.ARGS["web"]:
            url = url % (SERVER_ADDR, self.roomId)
        else:
            url = url % (self.ARGS["localIP"], self.roomId)
        
        
        platform_dependent(f"start \"\" {url.replace('client','host')}", windows=os.system)

        from util import print_url
        print_url(url)

        from util import print_qr,generate_qr
        generate_qr(url)
        if self.ARGS["qr"]:
            print(f"\n[{colored('$','blue')}] Or scan the QR code given below")
            print_qr()


    def bind(self):
        """ Binds the player instance to this class instance. """
        from vlc_comm import player

        self.player = player

    """ Functions with name like on_event are executed when a signal named 'event' is recieved from the server. """

    
    def on_connect(self):
        print("connected")

    def on_userId(self, data):
        print("userId is ", colored(data, "blue"))

    def on_disconnect(self):
        print(
            colored("\nDisconnected...", "red")
            + colored("\nExiting Now...Goodbye!", "green")
        )

    def on_play(self, *args, **kwargs):
        try:
            state = args[0]
            print(f"[{colored('$','blue')}] Play signal recieved")
            self.player.play()
        except:
            pass
        

    def on_pause(self, *args, **kwargs):
        try:
            state = args[0]
            print(f"[{colored('$','blue')}] Pause signal recieved")
            self.player.pause()
        except:
            pass
        

    def on_seek(self, *args, **kwargs):
        try:
            state = args[0]
            seek_time = int(time.time() - state["last_updated"] + state["position"])
            print(
                f"[{colored('$','blue')}] Seek signal recieved ==> seeking to {colored(seek_time,'yellow')}"
            )
            self.player.seek(seek_time)
        except:
            pass
        

    


class ServerConnection:
    # Class that handles all connections to the server
    server_instance = None
    def __init__(self, args=None):
        if(ServerConnection.server_instance is not None):
            self = ServerConnection.server_instance
        else:
            try:
                self.ARGS = {}
                self.ARGS['web'] = args.web
                self.ARGS['qr'] = args.qr
                self.ARGS['onlyHost'] = args.onlyHost
                self.ARGS['localIP'] = args.localIP
            except:
                pass
            
            self.sio = socketio.Client()
            self.sio.connect(f"http://{SERVER_ADDR}:5000")
            self.tracks = {}
            
            self.start_listening()
            ServerConnection.server_instance = self

    def send(self, signal, data):
        """ Used to send data to the server with a corresponding signal"""
        self.sio.emit(signal, data)

    def start_listening(self):
        """ Establish connection to the server and start listening for signals from the server """

        self.signals = SignalReceiver("/",params = self.ARGS)

        platform_dependent(windows=self.signals.bind)

        self.sio.register_namespace(self.signals)

    def track_change(self,videoPath,state):
        print(f"[{colored('#','yellow')}] Changing track to ", colored(path2title(videoPath),'green') )
        self.send('changeTrack',{
            self.tracks[videoPath][0] : self.tracks[videoPath][1],
            "state": state
        })

    def add_track(self, videoPath):
        self.send(
            "addTrack",
            {
                "title": path2title(videoPath),
                self.tracks[videoPath][0]: self.tracks[videoPath][1],
            },
        )

    def create_room(self):
        self.send('createRoom',{
            "onlyHost": self.ARGS["onlyHost"]
        })

    def upload(self, videoPath ,audioPath):
        """ Uploads audio file to the webserver """
        print(f"[{colored('+','green')}] Uploading {colored(path2title(audioPath),'green')} to server ...")
        import requests

        url = f"http://{SERVER_ADDR}:5000/api/upload/"
        files = {"file": (path2title(videoPath), open(audioPath, "rb"), "audio/ogg")}
        r = requests.post(url=url, files=files, data={"title": path2title(videoPath)})

        self.tracks[videoPath]= ("trackId" ,r.json()['trackId'])
        print(
            f"[{colored('+','green')}] Upload complete for file {colored(path2title(audioPath),'green')}")

    def addAudioPath(self, videoPath, audioPath):
        self.tracks[videoPath] = ("audioPath", audioPath)

