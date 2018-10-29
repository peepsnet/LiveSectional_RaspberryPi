# LiveSectional_RaspberryPi
This is a Live Sectional for a Raspberry Pi

Still a work in progress! The code it still being worked on as of 10/29/2018. 

I will hope to release a V1.0 soon. 

Use at your own risk!

ToDo:
- [ ] 1) Finish StartHere.sh - This script will install and then config or config
  - [ ] a) edit /home/pi/.local/lib/python2.7/site-packages/Adafruit_WS2801/WS2801.py line 124 to call ## self.set_pixel_rgb(i, r, g, b)
  - [ ] b) edit rc.local to call /usr/bin/python ~/LiveSectional/pishutdown.py
  - [ ] c) edit rc.local to call /usr/bin/python ~/LiveSectional/LiveSectional.py startup
  - [ ] d) Add Cron for LiveSectional.py to be called as user specified interval
  - [ ] e) add code to modify settings in config.txt

- [ ] 2) Documentation
  - [ ] a) Install Steps
    - [ ] i)    How to install Raspbian
    - [ ] ii)   How to enable SSH(headless)
    - [ ] iii)  How to connect to WiFi on boot(headless)
    - [ ] iv)   Expand Filesystem
    - [ ] v)    Download install.sh to get scripts(wget)
    - [ ] vi)   chmod +x install.sh
    - [ ] vii)  ./install.sh
  - [ ] b) Error Flashing
  - [ ] c) Status and Metar LEDs
  - [ ] d) Legend LEDs

- [ ] 3) Document Build

- [ ] 4) continue to tweak LiveSectional.py code till I am satified or bored

 
Required Library [adafruit/Adafruit_Python_WS2801](https://github.com/adafruit/Adafruit_Python_WS2801)


Required Library [adafruit/Adafruit_Python_GPIO](https://github.com/adafruit/Adafruit_Python_GPIO)

