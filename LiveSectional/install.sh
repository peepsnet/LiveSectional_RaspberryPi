#!/bin/bash
#This will install and correct a few library errors for the LiveSectional Script
#WIP
## https://github.com/adafruit/Adafruit_Python_GPIO
## https://github.com/adafruit/Adafruit_Python_WS2801
## https://github.com/adafruit/Adafruit_Python_WS2801/pull/3 (need to modify file because of unaddresses typo)

#sudo pip install rpi_ws281x
#https://pypi.org/project/rpi_ws281x/

parm="*"
err="####"
att="+++"

#Set fonts for Help.
BOLD=$(tput bold)
STOT=$(tput smso)
DIM=$(tput dim)
UNDR=$(tput smul)
REV=$(tput rev)
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
MAGENTA=$(tput setaf 5)
WHITE=$(tput setaf 7)
NORM=$(tput sgr0)
NORMAL=$(tput sgr0)

function HEAD {
	clear
	echo "#######################################################################"
	echo "#              LIVE SECTIONAL IINSTALL AND CONFIG TOOL                #"
	echo "#######################################################################"
	echo " "
}

function WELCOME {
	echo ""
	echo "Welcome to ..."
	echo ""
}

function STARTINSTALL {
	HEAD
	echo " "
	echo 
}

function INSTALL_LIVESECTIONAL {
	cd ~/
	sudo mkdir LiveSectional
	cd LiveSectional
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/LiveSectional.py
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/airports.txt
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/config.txt
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/pishutdown.py
}

finction INSTALL_PIP_RPI_WS281X {
	#sudo pip install rpi_ws281x
}

function INSTALL_PIP_GPIO {
	#sudo pip install RPi.GPIO
	echo ""
}

function EDIT_RC_LOCAL {
	## edit rc.local to call /usr/bin/python ~/LiveSectional/pishutdown.py
	## edit rc.local to call /usr/bin/python ~/LiveSectional/LiveSectional.py startup
	echo ""
}

function ADD_CRON {
	## Add CronJob
	echo ""
}

function INSTALL_APTGET_EXTRAS {
	sudo apt-get install build-essential python-pip python-dev python-smbus git -y
}

function APTGETUPDATE {
	sudo apt-get update
}

function APTGETUPGRADE {
	sudo apt-get upgrade -y
}

## Start of work
clear

HEAD
WELCOME

choices=( 'Change Settings' 'Install and Configure' 'Exit' )
select choice in "${choices[@]}"; do
	[[ -n $choice ]] || { echo "Invalid choice." >&2; continue; }
	case $choice in
    	'Change Settings')
			echo "Change Settings"
    	    ;;
    	'Install and Configure')
			echo "Install and Config"
			APTGETUPDATE
			INSTALL_APTGET_EXTRAS
			INSTALL_PIP_RPI_WS281X
			#INSTALL_PIP_GPIO
			#EDIT_RC_LOCAL
			#ADD_CRON
			;;
		'Exit')
			exit 0
		;;
		exit)

    exit 0
  	esac
break
done

if [ $(whoami) != 'root' ]; then
	echo "${BOLD}${RED}This script must be executed as root, exiting...${WHITE}${NORMAL}"
	echo "${BOLD}${RED}USAGE${WHITE}${NORMAL}"
	exit 1
fi




#cd ~/
#git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
#cd Adafruit_Python_GPIO
#sudo /usr/bin/python setup.py install
#sudo pip install adafruit-ws2801
#sudo rm -r Adafruit_Python_GPIO

## edit /home/pi/.local/lib/python2.7/site-packages/Adafruit_WS2801/WS2801.py line 124
## self.set_pixel_rgb(i, r, g, b)

## Add CronJob

## edit rc.local to call /usr/bin/python ~/LiveSectional/pishutdown.py
## edit rc.local to call /usr/bin/python ~/LiveSectional/LiveSectional.py startup
