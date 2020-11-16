# Common Audio Video

## Description
This repo tracks 3 repos which make up this project -- 
- [NodeServer](https://github.com/Harsh14901/CommonAudioVideoServer)
- [PythonCLI](https://github.com/Harsh14901/CommonAudioVideoCLI)
- [ElectronGUI](https://github.com/saptarshi1234/CommonAudioVideoGUI)

A standalone release for CLI is also available in [CLI_release](https://github.com/Harsh14901/CommonAudioVideoCLI/releases) and instructions to build the standalone CLI is present in [CLI](https://github.com/Harsh14901/CommonAudioVideoCLI).

## Installing
Grab the latest .zip or .deb from [releases](https://github.com/Harsh14901/CAV/releases).
This project requires 2 additional dependencies - ffmpeg and vlc.
The deb file already contains these, and you can install the dependencies along with the deb file using apt - 
``` bash
$ sudo apt install <Path to .deb file>
```
 but if you are using the zipped release, install these first from your package manager, eg: 
``` bash 
$ sudo apt install vlc ffmpeg
```


## Building
To build for your current system, (currently for linux) execute the following - 
``` bash
$ git clone https://github.com/Harsh14901/CAV
$ cd CAV
$ git submodule update --init
$ make -f build_script
$ make clean
```
the above build_script creates temporary virtual env and installs every node module and is meant for a freshly cloned repo.
For regular development, consider using the default makefile that expects that all packages and node modules are already installed.
``` bash
$ make
```

