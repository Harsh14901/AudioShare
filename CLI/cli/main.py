import argparse
import sys
import signal
import time
import os
import colorama

from multiprocessing import Process, freeze_support
from termcolor import colored

from vlc_comm import player
from util import get_videos, getLocalIP, spawn_server, platform_dependent, Unbuffered, nop
from audio_extract import convert_async

import linux_util
import win_util



TO_CLEAR = ["cache", "invite_link.txt", "invite_link.png", "debug.log"]


def parse():
    parser = argparse.ArgumentParser(
        description="Route audio of a video file through a local server."
    )
    group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "-f",
        "--file",
        required=True,
        dest="f",
        help="Path to video files or directory containing video files",
        type=str,
        action="append",
    )
    parser.add_argument(
        "--qr", help="Show qr code with the link", dest="qr", action="store_true"
    )
    parser.add_argument(
        "--control",
        help="only host can control play/pause signals",
        dest="onlyHost",
        action="store_true",
    )
    parser.add_argument(
        "--force-rebuild",
        help="Force rebuild of the local server",
        dest="rebuild",
        action="store_true",
    )
    parser.add_argument(
        "--audio-quality",
        dest="q",
        help="Audio quality to sync from",
        choices=["low", "medium", "good", "high"],
        type=str,
        default="medium",
    )

    group.add_argument(
        "--web",
        help="Force routing through a web server",
        dest="web",
        action="store_true",
    )
    args = parser.parse_args()
    args.localIP = getLocalIP()

    videos = []
    for i in range(len(args.f)):
        args.f[i] = os.path.abspath(args.f[i])
        videos.extend(get_videos(args.f[i], TO_CLEAR))
    args.f = videos
    return args



def initialize(videos, server, first=False):
    audio = convert_async(videos, args)

    for video in videos:

        if args.web:
            server.upload(video, video[:-3] + "ogg")
        else:
            server.addAudioPath(video, video[:-3] + "ogg")
            TO_CLEAR.append(video[:-3] + "ogg")

        platform_dependent(video, linux=player.enqueue)
        
        if(first):
            server.create_room()

            def init_player(player):
                player.play()
                player.pause()
                player.seek(0)
            
            platform_dependent(player ,linux=init_player)

            
        server.add_track(video)

def clear_files():    
    for file in TO_CLEAR:
        if os.path.exists(os.path.abspath(file)):
            try:
                os.remove(file)
            except:
                pass


def exitHandler(*args, **kwargs):
    platform_dependent(linux=linux_util.kill_dependencies, windows=win_util.kill_dependencies)
    clear_files()
    platform_dependent(linux=linux_util.kill_self, windows=win_util.kill_self)


if __name__ == "__main__":
    

    platform_dependent(windows=freeze_support)

    sys.stdout = Unbuffered(sys.stdout)
    signal.signal(signal.SIGINT, exitHandler)
    platform_dependent(windows=colorama.init)
    args = parse()

    platform_dependent(linux=nop if args.web else spawn_server, windows=spawn_server)
    
    platform_dependent(linux=player.launch)
    server = platform_dependent(args, linux=linux_util.start_server, windows=win_util.start_server)
    platform_dependent(linux=Process(target=player.update, args=(server,)).start)

    initialize([args.f[0]], server=server, first=True)

    if len(args.f) > 1:
        initialize(args.f[1:],server)

    print("\n" + colored("#" * 70, "green") + "\n")
    sys.stdout.flush()
    while True:
        time.sleep(1)
