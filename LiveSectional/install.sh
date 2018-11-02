#!/bin/bash
#This will install and correct a few library errors for the LiveSectional Script
#WIP
## https://github.com/adafruit/Adafruit_Python_GPIO
## https://pypi.org/project/rpi_ws281x/

parm="*"
err="####"
att="+++"

#Set fonts
BOLD=$(tput bold)
STOT=$(tput smso)
STOTX=$(tput rmso)
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

function HEAD() {
	clear
	echo "${REV}#######################################################################"
	echo "#              ${NORM}LIVE SECTIONAL IINSTALL AND CONFIG TOOL${REV}                #"
	echo "#######################################################################"
	echo "${NORM} "
}

function WELCOME() {
	echo ""
	echo "Welcome to ..."
	echo ""
}

function INSTALL_LIVESECTIONAL() {
	echo "${GREEN}${BOLD}=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=${NORM}"
	echo "${BOLD}Getting Live Sectional WS2811 files from the github...${NORM}"
	cd ~/
	mkdir LiveSectional
	cd LiveSectional
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/LiveSectional.py
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/airports.txt
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/config.txt
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/pipowerbtn.py
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/pipowerbtn.service
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/livesectional.service
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/single.py
	#wget https://raw.githubusercontent.com/peepsnet/LiveSectional_RaspberryPi/master/LiveSectional/test.py
	#sudo chmod +x LiveSectional.py
	#sudo chmod +x single.py
	#sudo chmod +x test.py
	
	echo ""
}

function INSTALL_PIP_RPI_WS281X() {
	echo "${GREEN}${BOLD}=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=${NORM}"
	echo "${BOLD}Installing the RPI_WS281x python library using PIP...${NORM}"
	#sudo sudo pip install rpi_ws281x
	echo ""
}

function INSTALL_PIP_GPIO() {
	echo "${GREEN}${BOLD}=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=${NORM}"
	echo "${BOLD}Installing the RPI.GPIO python library using PIP...${NORM}"
	#sudo sudo pip install RPi.GPIO
	echo ""
}

function CREATE_SYSTEMD_ENTRIES() {
	echo "${GREEN}${BOLD}=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=${NORM}"
	echo "${BOLD}Copying .service files to /etc/systemd/system/ and updating the systemctrl...${NORM}"
	#cp  ~/LiveSectional/pipowerbtn.service /etc/systemd/system/
	#cp  ~/LiveSectional/livesectional.service /etc/systemd/system/
	#sudo systemctl daemon-reload
	#sudo systemctl enable livesectional.service --now.
	#sudo systemctl enable pipowerbtn.service --now.
	echo ""
}

function ADD_CRON() {
	echo "Choose your METAR update interval:"
	choices=( 'Every 15 min' 'Every 20 min' 'Every 30 min' 'Top of every hour' 'Every X min')
		select choice in "${choices[@]}"; do
			[[ -n $choice ]] || { echo "Invalid choice." >&2; continue; }
			case $choice in
				'Every 15 min')
					echo "Setting schedule to every 15 min"
					LINE='*/15 * * * * sudo /usr/bin/python ~/LiveSectional/LiveSectional.py'
					;;
				'Every 20 min')
					echo "Setting schedule to every 20 min"
					LINE='*/20 * * * * sudo /usr/bin/python ~/LiveSectional/LiveSectional.py'
					;;
				'Every 30 min')
					echo "Setting schedule to every 30 min"
					LINE='*/30 * * * * sudo /usr/bin/python ~/LiveSectional/LiveSectional.py'
					;;
				'Top of every hour')
					echo "Setting schedule to top of every hour"
					LINE='	0 * * * * sudo /usr/bin/python ~/LiveSectional/LiveSectional.py'
					;;
				'Every X min')
					echo "Setting schedule to every X min"
					;;
				'Exit')
					exit 0
				;;
				exit)
				exit 0
			esac
		break
	done
	echo "${GREEN}${BOLD}=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=${NORM}"
	echo "${BOLD}Adding cronjob...${NORM}"
	#write out current crontab
	FILE="mycron.tmp"
	crontab -l > $FILE
	#echo new cron into cron file
#	grep -q "^LiveSectional" $FILE && sed -i "s/^LiveSectional.*/$LINE/" $FILE || echo "$LINE" >> $FILE
	sed -i '/LiveSectional/d' $FILE
	echo "$LINE" >> $FILE
	#install new cron file
	crontab $FILE
	rm $FILE
	echo ""
}

function INSTALL_APTGET_EXTRAS() {
	echo "${GREEN}${BOLD}=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=${NORM}"
	echo "${BOLD}Installing APT-GET packages..."
	sudo apt-get install build-essential python-pip python-dev python-smbus git -y
	echo ""
}

function APTGETUPDATE() {
	echo "${GREEN}${BOLD}=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=${NORM}"
	echo "${BOLD}Lets start by gathering the lastest packages...${NORM}"
	sudo apt-get update
	echo ""
}

function APTGETUPGRADE() {
	echo "${GREEN}${BOLD}=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=${NORM}"
	echo "${BOLD}Now we need to update your Raspberry Pi to the latest software...${NORM}"
	sudo apt-get upgrade -y
	echo ""
}

function REBOOTSYS() {
	echo "REBOOTING!!!"
	#sleep 5s; sudo shutdown -r now
	echo ""
}

function CHECKINTERNET() {
	echo "Checking for internet connection..."
	wget -q --spider http://google.com
	if [ $? -eq 0 ]; then
		echo "${GREEN}Internet connection detected..${NORM}"
		return 0
	else
		echo "${RED}${err} No internet found. ${err}"
		echo "${BOLD}This script requires an internet connection. Files must be downloaded from the internet."
		echo "Please refer to the readme..md at: https://github.com/peepsnet/LiveSectional_RaspberryPi${NORM}"
		echo "Exiting..."
		return 1
	fi
}

function ROOTCHECK() {
	echo "${BOLD}Checking if script is run as root...${NORM}"
	if [ $(whoami) != 'root' ]; then
		echo "${BOLD}${RED}This script must be executed as root${WHITE}${NORM}"
		echo "${BOLD}Please run as root: ${STOT}sudo ./install.sh${NORM}"
		echo "Exiting..."
		exit 1
	else
		echo "${GREEN}Root Check passed...${NORM}"
		echo "${GREEN}Continuing...${NORM}"
	fi
}

function COMPLETEDINSTALL() {
	HEAD
	echo "Basic instalation and configuration of LiveSectional is complete..."
	echo "The next step is to set up your LEDs and Airports."
	echo ""
	echo "Prese enter/return to continue..."
	read -p "" readDamKey
}

function EDITLEDSAIRPORTS() {
	echo ""
	echo "Description on how to edit the airports.txt file"
	echo ""
	echo "Prese enter/return to begin editing the airport list..."
	read -p "" readDamKey
	nano airports.txt
}
###################################
###################################
## Start of work
###################################
###################################

clear

HEAD
#ROOTCHECK
if ! CHECKINTERNET; then
	exit 0
fi
sleep 2s
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
			HEAD
			echo "Installing and configuring files"
			APTGETUPDATE
			APTGETUPGRADE
			INSTALL_APTGET_EXTRAS
			INSTALL_LIVESECTIONAL
			INSTALL_PIP_RPI_WS281X
			INSTALL_PIP_GPIO
			CREATE_SYSTEMD_ENTRIES
			ADD_CRON
			sleep 5s
			COMPLETEDINSTALL
			EDITLEDSAIRPORTS
			sleep 1s
			REBOOTSYS
			;;
		'Exit')
			exit 0
		;;
		exit)
		exit 0
		esac
	break
	done

#################################
##  Useful code storage
#################################

# Screen Params
#_COLUMNS=$(tput cols)
#_LINES=$(tput lines)
#_MESSAGE="HELLO AND WELCOME\nPRESS ANY KEY TO CONTINUE"
#x=$(( $_LINES / 2 ))
#y=$(( ( $_COLUMNS - ${#_MESSAGE} )  / 2 ))
#tput clear
#tput cup $x $y
#read -p "" readDamKey 

# Start cleaning up our screen...
#tput clear
#tput sgr0
#tput rc