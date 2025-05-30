# Installation

## Operating System

This section is independent of the project but I wrote it down to remember
1. Install Raspberry OS lite (64 bit) on Raspberry PI 5 8GB
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

## Setup Application

1. Clone this git repository
9. Install apt packages
    1. PiCamera2: Test using NP scripts \
    `sudo apt install -y python3-picamera2 --no-install-recommends`
    2. Maybe not needed? (at some point it would not work anymore) \
    `sudo apt-get install python3-dev`
    3. FFMPEG for conversion of h264 to MP4\
    `sudo apt-get install ffmpeg`
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
    3. The Web framework\
    `python -m pip install tornado`
    4. Numpy (may be already satisfied)\
    `python -m pip install numpy`
    5. OpenCV\
    `python -m pip install opencv-python`
    6. Tensorflow lite for object detection. Only Runtime because we do not train models\
    `python -m pip install tflite-runtime`
    7. The clips are stored in a database but very basic\
    `python -m pip install tinydb`\
    `python -m pip install tinydb-serialization`

12. Run the script as a test
    1. Execute `./main.py` and observe console output
    2. Connect to the camera's web interface by navigating to the displayed ip adress, contained in one of the first logs. in my case: `192.168.1.4:8000`

13. Autorun Application on System Start (sorry that this is not so convenient)
    1. Edit `Application/Start.sh` and replace the paths with the ones from your installation location
    2. Run `crontab -e` and add the line `@reboot sleep 10 && /home/pi/FeatherVision/Application/Start.sh &`
    3. Reboot `sudo reboot` and check if you can connet.
    4. In case you want to stop the autostarted application, you can execute `Kill.sh`

13. Configure the camera by editing the `Application/Config/Config.py` file

14. Download and add the object detection model (see next section

## Object detection models

14. For the camera to work you need object detection models. These come not from me so I don't want to add it to the repos. You need to download it yourself (in the confi file you can set the name). You always need some tflite model and the matching labels file. Put it in the `ApplicationData\TensorFlowLiteModels` directory. 
I am no expert in this. 

I have used the efficientdet models which worked fine for me. There are different quality levels of it you may experiment with them. You can find them here:
https://www.kaggle.com/models/tensorflow/efficientdet/tfLite/lite2-detection-metadata

(I have not used this for some time I hope you can find it)




## Wifi-Dongle (optional)

The RPI5 gets pretty hot so we put it in a metal enclosure with integrated passive cooling. As this metal hunk screens the wifi signal, we use an external wifi antenna. I chose the *BrosTrend AC650*.
    1. `sh -c 'wget linux.brostrend.com/install -O /tmp/install && sh /tmp/install'`
    2. Turn in *predictable network names* with `sudo raspi-config` -> advanced
    3. Reboot
    3. Run `iwconfig` and note down the wifi name (something like `wlxa09f10bf0064`. Built in is `wlan0`)
    3. Copy the `/etc/wpa_supplicant/wpa_supplicant.conf` to the name `/etc/wpa_supplicant/wpa_supplicant-wlxa09f10bf0064.conf` but replace with your wifi name.
    3. Open `/boot/config.txt` and add the line `dtoverlay=disable-wifi` to disable the internal wifi

