#!/usr/bin/env python
##############################################################################
##							Live Sectional Script							##
##																			##
##																			##
##############################################################################
## To DO:
## Check for airport and config file before settings check
## Create visual error codes. Flash all LEDs red for count to indicate error.
## Flash connected and metar LEDs if test fails
#import pdb; pdb.set_trace()

import time
start = time.time()
import os
import sys
import socket
import urllib2
import xml.etree.ElementTree as ET
import time
import datetime
from rpi_ws281x import *
import ConfigParser

######################################################
##################### Functions ######################
######################################################

def dependencyCheck():
	f1 = os.path.isfile(airportListFile)
	f2 = os.path.isfile(configFile)
	if f1 and f2 :
		return True
	else:
		return False

def settingsCheck():
	errors = False
	debug("Checking for errors in the config data")
	#Check totalLEDs
	if (sum(1 for line in open(airportListFile)) > totalLEDs):
		print("\033[7mERROR:\033[m totalLEDs in " + configFile + " less then total entries in " + airportListFile)
		errors = True
	if not (maxBrightness in range(0,256)):
		print("\033[7mERROR:\033[m maxBrightness is not 0-255")
		errors = True
	if ((not sleepStart in range(0,24)) or (not sleepStop in range(0,24))) and sleepOn :
		print("\033[7mERROR:\033[m sleepStart and sleepStop values must be between 0-23 or disable by setting sleepOn to False")
		errors = True
	if ((not dimStart in range(0,24)) or (not dimStop in range(0,24))) and dimOn :
		print("\033[7mERROR:\033[m dimStart and dimStop values must be between 0-23 or disable by setting dimOn to False")
		errors = True
	if not (0 <= Dimming <= 1):
		print("\033[7mERROR:\033[m Dimming is not a valid value. Valid range is 0 - 1 in .01 increments.")
		errors = True
	if not windMax in range(3,51):
		print("\033[7mERROR:\033[m windMax is not a valid value. Valid range is 3 - 50 in increments of 1.")
		errors=True
	if not gustMax in range(3,51):
		print("\033[7mERROR:\033[m gustMax is not a valid value. Valid range is 3 - 50 in increments of 1.")
		errors=True
	if not (0 <= windDim <= 1):
		print("\033[7mERROR:\033[m windDim is not a valid value. Valid range is 0-1 in increments of .01")
		errors=True
	for checkRGB in colorRGBs:
		if not (int(colorRGBs[checkRGB][0]) in range(0,256)):
			print("\033[7mERROR:\033[m colorsRGB RED for color " + checkRGB + " is not in range. Must be 0-255")
			errors=True
		if not (int(colorRGBs[checkRGB][1]) in range(0,256)):
			print("\033[7mERROR:\033[m colorsRGB GREEN for color " + checkRGB + " is not in range. Must be 0-255")
			errors=True
		if not (int(colorRGBs[checkRGB][2]) in range(0,256)):
			print("\033[7mERROR:\033[m colorsRGB BLUE for color " + checkRGB + " is not in range. Must be 0-255")
			errors=True
		stationLEDs = getAirportLEDs()
		miscLEDs = config.items("extraLEDs")
		for stationLED in stationLEDs:
			for miscLED in miscLEDs:
				if int(stationLEDs[stationLED]) == int(miscLED[1]):
					print("\033[7mERROR:\033[m An LED address mismatch was found.")
					print("\033[7mERROR:\033[m " + stationLED + " LED location conflicts with " + miscLED[0])
					errors = True
	if errors:
		return False
	else:
		return True

#Function to make the LEDs do stuff when the script is called from rc.local prior to the first cron job call
def startUpLEDs():
	sleepTimeMS = 3000
	#Startup LED check and cool effect
	clearPixels()
	showPixels()
	time.sleep(sleepTimeMS/1000)
	debug("Setting All LEDs to WHITE(255,255,255)")
	setPixelsRGB([255 ,255 ,255])
	showPixels()
	time.sleep(sleepTimeMS/1000)
	debug("Setting All LEDs to RED(255,0,0)")
	setPixelsRGB([255 ,0 ,0])
	showPixels()
	time.sleep(sleepTimeMS/1000)
	debug("Setting All LEDs to GREEN(0,255,0)")
	setPixelsRGB([0 ,255 ,0])
	showPixels()
	time.sleep(sleepTimeMS/1000)
	debug("Setting All LEDs to BLUE(0,0,255)")
	setPixelsRGB([0 ,0 ,255])
	showPixels()
	time.sleep(1)
	clearPixels()
	showPixels()
	#Light each Pixel for 75ms for testing
	for x in range(totalLEDs):
		debug("Setting LED# " + str(x) + " to (255,255,255)")
		setPixelRGB(x, [255, 255, 255])
		showPixels()
		time.sleep(0.05)
		clearPixels()
		showPixels()

def getAirportList():
	#Read in LED Address/Airport list
	with open(airportListFile) as f:
		lines = f.readlines()
	return [x.strip() for x in lines]
	
def getAirportLEDs():
	airportList = getAirportList()
	x = 0
	notNulls = {}
	for IDs in airportList:
		if (airportList[x] != "NULL"):
			notNulls[IDs] = x
		x += 1
	return notNulls

def calcRGB(rgb, ID=None):
	wd = 0
	if ID:
		debug("Winds: WindSpeed: " + str(stationsData[ID]["WS"]) + " MaxWind: " + str(windMax) + " GustSpeed: " + str(stationsData[ID]["GS"]) + " MaxGust: " + str(gustMax))
		if (int(stationsData[ID]["WS"]) >= windMax) or (int(stationsData[ID]["GS"]) >= gustMax):
			debug("\033[7mMax wind or gust detected for:\033[m " + ID)
			wd = windDim

	newRGB = {}
	newRGB[0] = int(round(min(int(rgb[0]), int(maxBrightness)) * (1-Dimming) * (1-wd)))
	newRGB[1] = int(round(min(int(rgb[1]), int(maxBrightness)) * (1-Dimming) * (1-wd)))
	newRGB[2] = int(round(min(int(rgb[2]), int(maxBrightness)) * (1-Dimming) * (1-wd)))
	debug("RGB Value for LED is returned as: [" + str(newRGB[0]) + "," + str(newRGB[1]) + "," + str(newRGB[2]) + "]")

	return newRGB

def legendLEDsOn():
	if legendLEDs["VFR"] > 0:
		setPixelRGB(legendLEDs["VFR"], calcRGB(colorRGBs["VFR"]))
	if legendLEDs["MVFR"] > 0:
		setPixelRGB(legendLEDs["MVFR"], calcRGB(colorRGBs["MVFR"]))
	if legendLEDs["IFR"] > 0:
		setPixelRGB(legendLEDs["IFR"], calcRGB(colorRGBs["IFR"]))
	if legendLEDs["LIFR"] > 0:
		setPixelRGB(legendLEDs["LIFR"], calcRGB(colorRGBs["LIFR"]))
	if legendLEDs["Missing"] > 0:
		setPixelRGB(legendLEDs["Missing"], calcRGB(colorRGBs["Missing"]))
	debug("Set legendLEDs to colors")

def legendLEDsOff():
	if legendLEDs["VFR"] > 0:
		setPixelRGB(legendLEDs["VFR"], [0,0,0])
	if legendLEDs["MVFR"] > 0:
		setPixelRGB(legendLEDs["MVFR"], [0,0,0])
	if legendLEDs["IFR"] > 0:
		setPixelRGB(legendLEDs["IFR"], [0,0,0])
	if legendLEDs["LIFR"] > 0:
		setPixelRGB(legendLEDs["LIFR"], [0,0,0])
	if legendLEDs["Missing"] > 0:
		setPixelRGB(legendLEDs["Missing"], [0,0,0])
	debug("Set legendLEDs to OFF")

def connected():
	try:
		s = socket.create_connection((socket.gethostbyname("www.google.com"), 80), 2)
		return True
	except:
		return False

def setPixelsRGB(rgb):
	for i in range(totalLEDs):
		pixels.setPixelColorRGB(i, int(rgb[0]), int(rgb[1]), int(rgb[2]))

# Set an individual LED color if the address of the LED is >= 0
def setPixelRGB(addr, rgb):
	if (addr >= 0):
		pixels.setPixelColorRGB(addr, int(rgb[0]), int(rgb[1]), int(rgb[2]))

def showPixels():
	pixels.show()

def clearPixels():
	for i in range(totalLEDs):
		setPixelRGB(i, [0,0,0])

def colorWipe(pixels, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(pixels.numPixels()):
        pixels.setPixelColor(i, color)
        showPixels()
        time.sleep(wait_ms/1000.0)

def is_hour_between(now, start, end):
	if (start <= end):
		return start <= now < end
	else: # over midnight e.g., 23:30-04:15
		return start <= now or now < end

def errorLEDFlash(flash):
	debug("LEDs on RED")
	setPixelsRGB([255 ,0 ,0])
	showPixels()
	time.sleep(1)
	debug("LEDs Off")
	clearPixels()
	showPixels()
	time.sleep(1)
	for x in range(flash):
		debug("LEDs on RED: " + str(x+1))
		setPixelsRGB([255 ,0 ,0])
		showPixels()
		time.sleep(0.5)
		debug("LEDs Off")
		clearPixels()
		showPixels()
		time.sleep(0.25)
	clearPixels()
	showPixels()

def debug(var):
	if debugOn:
		print(var)

######################################################
#################### End Functions ###################
######################################################
#print("\033[7mReversed\033[m Normal")

#A few vars
debugOn = False
configFile = "/home/pi/LiveSectional/config.txt"
airportListFile = "/home/pi/LiveSectional/airports.txt"
currentHour = int(datetime.datetime.now().strftime("%H"))

#Load Config Data
config = ConfigParser.SafeConfigParser()
config.read(configFile)

#Load the Config.txt Vars
totalLEDs = config.getint("generalSettings","totalLEDs")
maxBrightness = config.getint("generalSettings","maxBrightness")
statusLED = config.getint("extraLEDs","statusLED")
metarLED = config.getint("extraLEDs","metarLED")

sleepOn = config.getboolean("sleepHours","sleepOn")
sleepStart = config.getint("sleepHours","sleepStart")
sleepStop = config.getint("sleepHours","sleepStop")

legendLEDs = {}
legendLEDs["VFR"] = config.getint("extraLEDs", "legendVFR")
legendLEDs["MVFR"] = config.getint("extraLEDs", "legendMVFR")
legendLEDs["IFR"] = config.getint("extraLEDs", "legendIFR")
legendLEDs["LIFR"] = config.getint("extraLEDs", "legendLIFR")
legendLEDs["Missing"] = config.getint("extraLEDs", "legendMissing")

windMax = config.getint("windAlerts", "windMax")
gustMax = config.getint("windAlerts", "gustMax")
windDim = config.getfloat("windAlerts", "windDim")

dimOn = config.getboolean("dimHours", "dimOn")
dimStart = config.getint("dimHours", "dimStart")
dimStop = config.getint("dimHours", "dimStop")
if ((currentHour >= dimStart) and (dimStart >= 0)) or ((currentHour < dimStop) and (dimStop >= 0)):
	Dimming = config.getfloat("dimHours", "Dimming")
else:
	Dimming = 0

colorRGBs = {}
colorRGBs["VFR"] = str(config.get("colorsRGB", "colorVFR")).split(",")
colorRGBs["MVFR"] = str(config.get("colorsRGB", "colorMVFR")).split(",")
colorRGBs["IFR"] = str(config.get("colorsRGB", "colorIFR")).split(",")
colorRGBs["LIFR"] = str(config.get("colorsRGB", "colorLIFR")).split(",")
colorRGBs["Missing"] =  str(config.get("colorsRGB", "colorMissing")).split(",")
colorRGBs["Red"] =  str(config.get("colorsRGB", "colorRed")).split(",")
colorRGBs["Green"] =  str(config.get("colorsRGB", "colorGreen")).split(",")

LED_COUNT 		= totalLEDs					# Number of LED pixels.
LED_PIN        	= 18      					# GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      					# GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    	= 800000  					# LED signal frequency in hertz (usually 800khz)
LED_DMA        	= 5       					# DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS 	= 255     					# Set to 0 for darkest and 255 for brightest
LED_INVERT     	= False   					# True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    	= 0       					# set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      	= ws.WS2811_STRIP_RGB   	# Strip type and colour ordering

pixels = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
pixels.begin()
#Test for script arguements present
#Call by adding "debug" as an arg
# LiveSectional.py debug
if ("debug" in sys.argv) or ("check" in sys.argv):
	debugOn = True

if ("shutdown" in sys.argv):
	setPixelsRGB([128,128,128])
	showPixels()
	time.sleep(.1)
	colorWipe(pixels, Color(0,0,0), 10)
	sys.exit()

debug("\n\033[7m-------------------------------------------\033[m\n          STARTING LIVE SECTIONAL\n\033[7m-------------------------------------------\033[m\n")


#Should we even start all this stuff up or Sleep the Map
#if ((sleepStart >= 0) and (sleepStop >= 0)) or :
if is_hour_between(currentHour, sleepStart, sleepStop) and sleepOn:
	debug("Within Sleep Time. Shutting off LED and quitting... Add skip to commandline to overwrite")
	pixels.clear()
	pixels.show()
	if ("skip" not in sys.argv):
		sys.exit()

#When the script is called from rc.local with the arg "startup"
#Check settings and if successful fun startUpLEDs function
# "LiveSectional.py startup"

if ("startup" in sys.argv) or ("check" in sys.argv):
	clearPixels()
	showPixels()
	debug("Checking settings...")
	if not settingsCheck():
		debug("Settings check Failed. Flashing RED...")
		errorLEDFlash(5)
		sys.exit()
	else:
		debug("All Settings Passed Checks!")
	startUpLEDs()


if not connected():
	debug('Status: NOT Connected to internet. Setting statusLED Color to RED. \nNo use in continuing... Exiting Script!\n')
	setPixelRGB(statusLED, colorRGBs["Red"])
	sys.exit()
else:
	debug('Status: Connected to internet. Setting statusLED Color to GREEN\n')
	setPixelRGB(statusLED, colorRGBs["Green"])
	legendLEDsOn()
	
	ICAOs = getAirportList()
	debug(ICAOs)

	#This builds the ICAO list from the LED/Airport List for injecting into the METAR URL
	url = ""
	urlICAOs = ""
	for ICAO in ICAOs:
		if (ICAO != "NULL"):
			urlICAOs += ICAO + ","
	urlICAOs = urlICAOs[:-1]
	
	#FAA METAR URL and Variables  as a DICT for easy readming and adding in the future
	metarUrl = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
	urlParms = {}
	urlParms["datasource"] = "metars"
	urlParms["requestType"] = "retrieve"
	urlParms["format"] = "xml"
	urlParms["mostRecentForEachStation"] = "constraint"
	urlParms["hoursBeforeNow"] = "3" 
	urlParms["stationString"] = urlICAOs
	
	#Loop through the FAAA METAR URL to build the full URL
	for urlKey, urlVal in urlParms.iteritems():
		url += urlKey + "=" + urlVal + "&"
	debug(metarUrl + url[:-1])

	#Retrieve the XML file from the FAA and set metarLED color
	try:
		metarsXML = urllib2.urlopen(metarUrl + url[:-1]).read()
	except Exception as e:
		debug("\nMetar Fetch Error: " + str(e) + "\nSetting metarLED to RED\n")
		setPixelRGB(metarLED, colorRGBs["Red"])
	else:
		debug("\nMetarData fetched successfully. Setting metarLED to GREEN\n")
		setPixelRGB(metarLED, colorRGBs["Green"])
	
	#Load retrieved XML data to Variable
	metarsData = ET.fromstring(metarsXML)
	
	#Loop though the <METAR> XML tag for each stations data and store in stationsData
	stationsData = {}
	for metar in metarsData.iter('METAR'):
		sID = metar.find('station_id').text
		stationsData[sID] = {}
		if (metar.find('flight_category') is not None):
			stationsData[sID]["FC"] = metar.find('flight_category').text
		else:
			stationsData[sID]["FC"] = "Missing"
		if metar.find('wind_speed_kt') is None:
			stationsData[sID]["WS"] = 0
		else:
			stationsData[sID]["WS"] = metar.find('wind_speed_kt').text
		
		if metar.find('wind_gust_kt') is None:
			stationsData[sID]["GS"] = 0
		else:
			stationsData[sID]["GS"] = metar.find('wind_gust_kt').text

	#Counter to keep track of the LED we are working on
	currentLED = 0
	
	#Go through ICAOs(LIST of LEDs/Airports) and set LEDs to the FC value if they match a METAR in stationsData
	for ICAO in ICAOs:
		debug("Checking for " + ICAO + " in METAR List")
		if (ICAO != "NULL") and (ICAO in stationsData):
			debug("Found match in METAR for station " + ICAO + "\nSetting LED color for Station " + ICAO)
			if (stationsData[ICAO]["FC"] == "VFR"):
				setPixelRGB(currentLED, calcRGB(colorRGBs["VFR"], ICAO))
			elif (stationsData[ICAO]["FC"] == "MVFR"):
				setPixelRGB(currentLED, calcRGB(colorRGBs["MVFR"], ICAO))
			elif (stationsData[ICAO]["FC"] == "IFR"):
				setPixelRGB(currentLED, calcRGB(colorRGBs["IFR"], ICAO))
			elif (stationsData[ICAO]["FC"] == "LIFR"):
				setPixelRGB(currentLED, calcRGB(colorRGBs["LIFR"], ICAO))
			else:
				setPixelRGB(currentLED, calcRGB(colorRGBs["Missing"], ICAO))
		else:
			debug("Unable to find a match for " + ICAO)
		debug("--------------------------------------------------------")
		currentLED += 1

debug("Sending all colors to LEDs - showPixels()")
showPixels()

debug("FINISHED")
debug("Script took: " + str(time.time() - start) + " Seconds")
