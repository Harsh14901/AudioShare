import argparse
import sys
import signal
import time
import os
import colorama

from multiprocessing import Process, freeze_support
from termcolor import colored

from vlc_comm import player
from util import (
    get_videos,
    getLocalIP,
    spawn_server,
    platform_dependent,
    Unbuffered,
    nop,
)
from audio_extract import convert_async, path2title

import linux_util
import win_util
import osx_util


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
    # parser.add_argument(
    #     "--force-rebuild",
    #     help="Force rebuild of the local server",
    #     dest="rebuild",
    #     action="store_true",
    # )
    # parser.add_argument(
    #     "--audio-quality",
    #     dest="q",
    #     help="Audio quality to sync from",
    #     choices=["low", "medium", "good", "high"],
    #     type=str,
    #     default="medium",
    # )

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
        files = []
        if not os.path.exists(args.f[i]):
            print("Path doesnot exist: ", args.f[i])
        if os.path.isdir(args.f[i]):
            for file in os.listdir(args.f[i]):
                files.append(os.path.join(args.f[i], file))
        elif os.path.isfile(args.f[i]):
            files = [args.f[i]]
        videos.extend(files)
        # videos.extend(get_videos(args.f[i], TO_CLEAR))
    args.f = videos
    return args


def initialize(video_paths, server, first=False):
    converted = convert_async(video_paths, args)
    # print("Video paths: ", video_paths, "converted: ", converted)
    if first and converted[0] == (None, None):
        raise ValueError("Invalid video path")

    for video_path, (audio_path, temp_mkv) in zip(video_paths, converted):
        if temp_mkv is not None:
            video_path = temp_mkv
            TO_CLEAR.append(temp_mkv)
        
        if args.web:
            server.upload(video_path, audio_path)
        else:
            server.addAudioPath(video_path, audio_path)
            TO_CLEAR.append(audio_path)

        platform_dependent(video_path, linux=player.enqueue)

        if first:
            server.create_room()

            def init_player(player):
                player.play()
                player.pause()
                player.seek(0)

            platform_dependent(player, linux=init_player)

        server.add_track(video_path)


def clear_files():
    for file in TO_CLEAR:
        if os.path.exists(os.path.abspath(file)):
            try:
                os.remove(file)
            except:
                pass


def exitHandler(*args, **kwargs):
    platform_dependent(
        linux=linux_util.kill_dependencies,
        windows=win_util.kill_dependencies,
        osx=osx_util.kill_dependencies,
    )
    clear_files()
    platform_dependent(
        linux=linux_util.kill_self, windows=win_util.kill_self, osx=osx_util.kill_self
    )


if __name__ == "__main__":
    print(sys.argv)

    platform_dependent(windows=freeze_support, osx=freeze_support)

    sys.stdout = Unbuffered(sys.stdout)
    signal.signal(signal.SIGINT, exitHandler)
    platform_dependent(windows=colorama.init)
    args = parse()

    platform_dependent(
        linux=nop if args.web else spawn_server,
        windows=spawn_server,
        osx=nop if args.web else spawn_server,
    )

    platform_dependent(linux=player.launch)
    server = platform_dependent(
        args,
        linux=linux_util.start_server,
        windows=win_util.start_server,
        osx=osx_util.start_server,
    )
    platform_dependent(linux=Process(
        target=player.update, args=(server,)).start)
    done = False
    while not done and len(args.f) > 0:
        try:
            initialize([args.f[0]], server=server, first=True)
            done = True
            args.f.pop(0)
        except ValueError:
            args.f.pop(0)
            

    if len(args.f) > 0:
        initialize(args.f, server)

    print("\n" + colored("#" * 70, "green") + "\n")
    sys.stdout.flush()
    while True:
        time.sleep(1)
