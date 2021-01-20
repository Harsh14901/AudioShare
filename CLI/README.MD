# Common Audio Video CLI

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Getting Started

### Prerequisites

To run this project you need to have python 3.6 or higher installed

**Note:** Windows users need to have the `ffmpeg` executable in the `CLI\cli\` directory for running the CLI.

### Installing

- Cloning the Repository

    ```bash
    $ git clone https://github.com/Harsh14901/AudioShare.git
    $ cd CLI/
    ```

- Installing dependencies

    ```bash
    pip3 install -r requirements.txt
    ```

- Running the CLI

    ```bash
    cd CLI/cli
    python3 main.py [--flags]
    ```


## Build

### Linux
Run the following command in the root directory of the repo
```bash
$ make -f build_script build_cli
```

You will find the built CLI as `./cache/LocalParty`

### Windows
- Build the Server by running the npm script to generate a server binary. It should be named CAV_server
  ``` powershell
  $ cd Server
  $ npm run create-executable
  $ cp CAV_server ..\CLI\cli\
  $ cd ..\CLI\
  ```

- install requirements.txt and dev-requirements.txt
    ```bash
    $ pip3 install -r requirements.txt
    $ pip3 install -r dev-requirements.txt
    ```
- Build the CLI
    ```bash
    $ cd cli
    $ pyinstaller -F --add-data '.\CAV_server.exe;.' --add-data 'ffmpeg.exe;.' '.\main.py' -n LocalParty

    ```
- Find the executable as `dist\LocalParty.exe` and enjoy the Party
## CLI flags

| FLAG NAME | arguments | usage | required | default
|--|--|--|--|--
| - - file / -f | path to one or more video files or directories(in which case all video files inside the directory are taken to form a playlist) | indicates which videos are to be converted and queued | yes
| -- qr| - |encodes the invite link as a qr code and prints it to the console| no| false
| --audio-quality| low/medium/good/high | the quality of the audio to be extracted from the video file| no | medium
|--web| - | use already hosted webserver | no | false 
|--control| - | only the host can control playback | no | false
## Socket events

| EVENT NAME | action
|--|--
|connect | emitted at the beginning to establish connection
|disconnect| emitted when session ends
| play | has 2 functions -- starts the playback of enqueued song, if no video is loaded, otherwise resumes the playback from where it was paused
| pause | pauses the playback
| seek  | seeks to the given time in the playback

Socket events, both sent and received follow the same structure as shown above and additionally, each event has the following information along with the event type :--

- epoch time -- the time in milliseconds when the command is being issued
- position -- the position of the video/audio playback

**Note:** The server has to create a room when 'connect' message is sent from the CLI, and return in response, the room URL. Any further messages from this socket should be considered as being emitted by the host of that room.

## Built With

- Python
- [ArgParser](https://pypi.org/project/argparse/) - create the command line interface
- [ffmpeg](https://pypi.org/project/ffmpeg-python/) - extract audio from vidoe file
- [subprocess](https://docs.python.org/3/library/subprocess.html) - issue bash commands from python and read VLC logs to catch play/pause events.
- [socket-io Client](https://python-socketio.readthedocs.io/en/latest/) - websocket to connect and send signals to server
- [socket](https://docs.python.org/3/library/socket.html) - tcp sockets to issue commands to VLC player



## License

[MIT](LICENSE)
