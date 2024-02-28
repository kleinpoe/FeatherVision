# Installation Feather Vision

## Operating System

1. Install Raspberry OS lite (64 bit)
2. Flash SD Card with custom options (SSH, Wifi, ...)
3. Test connect to raspberry with SSH
4. Setup connection without password (windows)
    1. On windows PC open Powershell window and navigate to \
    `~/.ssh/id_rsa.pub`
    2. Create key-pair \
    `ssh-keygen`
    3. Copy public key from windows pc to raspberry \
    `cat ~/.ssh/id_rsa.pub | ssh <USER>@<RASPBERRYPIHOSTNAME> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"`
    4. Test if connection without password works \
    `ssh <USER>@<RASPBERRYPIHOSTNAME>`

## Setup Development

1. In VS-Code on Windows install "Remote-SSH" Extension
    1. Configure Remote SSH Extension "Server-Install-Path": \
    `<RASPBERRYPIHOSTNAME> | /home/pi/VSRemote`
6. Connect to Raspberry home directory with VS
7. Create Directory for your project
8. Install git \
`sudo apt install git`
8. Initialize git repository or clone it
9. Install apt packages
    1. PiCamera2: Test using NP scripts \
    `sudo apt install -y python3-picamera2 --no-install-recommends`
    2. Maybe not needed? (at some point it would not work anymore) \
    `sudo apt-get install python3-dev`
10. Create a Virtual python environment \
`python -m venv .venv --system-site-packages`\
and activate it \
`source ./.venv/bin/activate`.\
 (for deactivation: `deactivate`)
11. Install necessary packages:
    1. Application needs to get ip and hostname of raspberry\
    `python -m pip install netifaces`
    2. To get Hardware information\
    `python -m pip install psutil`

