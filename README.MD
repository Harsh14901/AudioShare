# AudioShare

A desktop application to watch video on a common screen with friends and stream the audio on your individual device so that you are never frustrated by the sound quality of your laptop speaker.

## Installing
Grab the latest .zip or .deb from [releases](https://github.com/Harsh14901/AudioShare/releases).

### Linux
This project requires 2 additional dependencies - `ffmpeg` and `vlc`.
The deb file already contains these, and you can install the dependencies along with the deb file using apt - 
``` bash
$ sudo apt install <Path to .deb file>
```
 but if you are using the zipped release, install these first from your package manager, eg: 
``` bash 
$ sudo apt install vlc ffmpeg
```
### Windows
Download the setup from the releases section and install it. Once the setup finishes installing the required components, search for `audioshare` in windows start menu and click on it. This will launch the `audioshare` window on the host machine and use it to party with your friends.

## Building

We have provided build scripts for building the executables from source code itself.

### Linux
To build for your current system, execute the following - 
``` bash
$ git clone https://github.com/Harsh14901/AudioShare
$ cd AudioShare/
$ make -f build_script
```
the above build_script creates temporary virtual env and installs every node module and is meant for a freshly cloned repo.
For regular development, consider using the default makefile that expects that all packages and node modules are already installed.
``` bash
$ make
```

### Windows
Similar to the linux environment a powershell script `build_script.ps1` is provided to generate the setup and executables for the project from scratch. This is meant for a freshly cloned repo and will install all the components from scratch.

**Note:** Building for windows requires the ffmpeg executable. It can be downloaded from the official [ffmpeg build page](https://ffmpeg.org/download.html). Place the executable in the `AudioShare\CLI\cli\` directory to prevent any build errors.

Execute the following command on a powershell terminal after satisfying the above dependencies.
``` powershell
$ .\build_script.ps1
```

## Development
This repo tracks 3 repos where the initial development took place.
- [NodeServer](https://github.com/Harsh14901/CommonAudioVideoServer)
- [PythonCLI](https://github.com/Harsh14901/CommonAudioVideoCLI)
- [ElectronGUI](https://github.com/saptarshi1234/CommonAudioVideoGUI)

A standalone release for CLI is also available in [CLI_release](https://github.com/Harsh14901/CommonAudioVideoCLI/releases) and instructions to build the standalone CLI is present in [CLI](https://github.com/Harsh14901/CommonAudioVideoCLI).
