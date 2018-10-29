#!/usr/bin/bash
#This will install and correct a few library errors for the LiveSectional Script
#WIP
## https://github.com/adafruit/Adafruit_Python_GPIO
## https://github.com/adafruit/Adafruit_Python_WS2801

sudo apt-get update
sudo apt-get install build-essential python-pip python-dev python-smbus git
cd ~/
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO
sudo /usr/bin/python setup.py install
sudo pip install adafruit-ws2801
sudo rm -r Adafruit_Python_GPIO

## edit /home/pi/.local/lib/python2.7/site-packages/Adafruit_WS2801/WS2801.py line 124
## self.set_pixel_rgb(i, r, g, b)

## Add CronJob

## edit rc.local to call /usr/bin/python ~/LiveSectional/pishutdown.py
## edit rc.local to call /usr/bin/python ~/LiveSectional/LiveSectional.py startup
