#!/usr/bin/env python
##############################################################################
##							Live Sectional Script							##
##																			##
##																			##
##############################################################################

import time
start = time.time()
import os
import sys
import socket
import urllib2
import xml.etree.ElementTree as ET
import time
import datetime
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_WS2801
import ConfigParser

######################################################
##################### Functions ######################
######################################################

#Function to make the LEDs do stuff when the script is called from rc.local prior to the first cron job call
def startUpLEDs():
	#Startup LED check and cool effect
	debug("Setting All LEDs to WHITE(255,255,255)")
	setPixelsRGB([255 ,255 ,255])
	showPixels()
	time.sleep(1)
	debug("Setting All LEDs to RED(255,0,0)")
	setPixelsRGB([255 ,0 ,0])
	showPixels()
	time.sleep(0.5)
	debug("Setting All LEDs to GREEN(0,255,0)")
	setPixelsRGB([0 ,255 ,0])
	showPixels()
	time.sleep(0.5)
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
		time.sleep(0.075)
		clearPixels()

def settingsCheck():
	errors = False
	debug("Checking for errors in the config data")
	#Check totalLEDs
	if (sum(1 for line in open(airportListFile)) > totalLEDs):
		print("ERROR: totalLEDs in " + configFile + " less then total entries in " + airportList)
		errors = True
	if not (maxBrightness in range(0,256)):
		print("ERROR: maxBrightness is not 0-255")
		errors = True
	if ((not sleepStart in range(0,24)) or (not sleepStop in range(0,24))) and sleepOn :
		print("ERROR: sleepStart and sleepStop values must be between 0-23 or disable by setting sleepOn to False")
		errors = True
	if ((not dimStart in range(0,24)) or (not dimStop in range(0,24))) and dimOn :
		print("ERROR: dimStart and dimStop values must be between 0-23 or disable by setting dimOn to False")
		errors = True
	if not (0 <= Dimming <= 1):
		print("ERROR: Dimming is not a valid value. Valid range is 0 - 1 in .01 increments.")
		errors = True
	if not windMax in range(3,51):
		print("ERROR: windMax is not a valid value. Valid range is 3 - 50 in increments of 1.")
		errors=True
	if not gustMax in range(3,51):
		print("ERROR: gustMax is not a valid value. Valid range is 3 - 50 in increments of 1.")
		errors=True
	if not (0 <= windDim <= 1):
		print("ERROR: windDim is not a valid value. Valid range is 0-1 in increments of .01")
		errors=True
	for checkRGB in colorRGBs:
		if not (int(colorRGBs[checkRGB][0]) in range(0,256)):
			print("ERROR: colorsRGB RED for color " + checkRGB + " is not in range. Must be 0-255")
			errors=True
		if not (int(colorRGBs[checkRGB][1]) in range(0,256)):
			print("ERROR: colorsRGB GREEN for color " + checkRGB + " is not in range. Must be 0-255")
			errors=True
		if not (int(colorRGBs[checkRGB][2]) in range(0,256)):
			print("ERROR: colorsRGB BLUE for color " + checkRGB + " is not in range. Must be 0-255")
			errors=True
		stationLEDs = getAirportLEDs()
		miscLEDs = config.items("extraLEDs")
		for stationLED in stationLEDs:
			for miscLED in miscLEDs:
				if int(stationLEDs[stationLED]) == int(miscLED[1]):
					print("ERROR: An LED address mismatch was found.")
					print("ERROR: " + stationLED + " LED location conflicts with " + miscLED[0])
					errors = True
	if errors:
		return False
	else:
		return True

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
		if (int(stationsData[ID]["WS"]) > windMax) or (int(stationsData[ID]["GS"]) > gustMax):
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
	pixels.set_pixels_rgb(int(rgb[0]), int(rgb[1]), int(rgb[2]))

# Set an individual LED color if the address of the LED is >= 0
def setPixelRGB(addr, rgb):
	if (addr >= 0):
		pixels.set_pixel_rgb(addr, int(rgb[0]), int(rgb[1]), int(rgb[2]))

def showPixels():
	pixels.show()

def clearPixels():
	pixels.clear()

def is_hour_between(now, start, end):
	if (start <= end):
		return start <= now < end
	else: # over midnight e.g., 23:30-04:15
		return start <= now or now < end

def debug(var):
	if debugOn:
		print(var)

######################################################
#################### End Functions ###################
######################################################

#A few vars
debugOn = False
configFile = "config.txt"
airportListFile = "airports.txt"
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

# The WS2801 library makes use of the BCM pin numbering scheme. See the README.md for details.
# Specify a software SPI connection for Raspberry Pi on the following pins:
#PIXEL_CLOCK = 18
#PIXEL_DOUT  = 23
#pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, clk=PIXEL_CLOCK, do=PIXEL_DOUT)

# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT = 0
SPI_DEVICE = 0
pixels = Adafruit_WS2801.WS2801Pixels(totalLEDs, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

#Test for script arguements present
#Call by adding "debug" as an arg
# LiveSectional.py debug
if ("debug" in sys.argv) or ("check" in sys.argv):
	debugOn = True


debug("\n-------------------------------------------\nSTARTING LIVE SECTIONAL\n-------------------------------------------\n")


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
	debug("Checking settings...")
	if not settingsCheck():
		debug("Settings check Failed. Flashing RED...")
		for x in range(5):
			setPixelsRGB([255 ,0 ,0])
			showPixels()
			time.sleep(0.5)
			clearPixels()
			showPixels()
			time.sleep(0.75)
		clearPixels()
		showPixels()
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
