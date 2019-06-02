# LiveSectional_RaspberryPi
This is a Live Sectional for a Raspberry Pi

As of 6/262019 This code is not at all tested or working on in this branch. Please see the master branch for a working version:
https://github.com/peepsnet/LiveSectional_RaspberryPi

I will hope to release a V1.0 soon. 

Use at your own risk!

ToDo:
- [ ] 1) Finish setup.sh - This script will install and then config or just config
  - [ ] a) add code to modify settings in config.txt

- [ ] 2) Documentation
  - [ ] a) Install Steps - Till better documentation can be finished here is a quick & dirty list
    - [ ] i)    google How to install Raspbian
    - [ ] ii)   google How to enable SSH(headless)
    - [ ] iii)  google How to connect to WiFi on boot(headless)
    - [ ] iv)   google Change TimeZone (so sleep and dim functions work)
    - [ ] iv)   google Expand Filesystem
    - [ ] v)    Power on RPI and connect to with SSH client
    - [ ] vi)    Download setup.sh (wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/Threading-Dev/LiveSectional/setup.sh)
    - [ ] vii)   chmod +x setup.sh
    - [ ] viii)  ./setup.sh
  - [ ] b) Error Flashing LED
  - [ ] c) Status and Metar LEDs
  - [ ] d) Legend LEDs

- [ ] 3) Document Build

- [ ] 4) continue to tweak LiveSectional.py code till I am satified or bored

 
Required Libraries:
https://pypi.org/project/rpi_ws281x/
https://pypi.org/project/RPi.GPIO/
https://pypi.org/project/python-crontab/



Other Hubs Used:

[gilyes/pi-shutdown](https://github.com/gilyes/pi-shutdown)
