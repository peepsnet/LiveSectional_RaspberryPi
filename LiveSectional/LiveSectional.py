#!/usr/bin/env python
##############################################################################
##							Live Sectional Script							##
##																			##
##																			##
##############################################################################

#todo:
# Error checking for settings.
# i.e. do not allow addressed > totalLEDs

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

#Load Config Data
config = ConfigParser.SafeConfigParser()
config.read("config.txt")

#Load enough data to get started
currentHour = int(datetime.datetime.now().strftime("%H"))
totalLEDs = int(config.get("generalSettings","totalLEDs"))
sleepStart = int(config.get("sleepHours","sleepStart"))
sleepStop = int(config.get("sleepHours","sleepStop"))

# The WS2801 library makes use of the BCM pin numbering scheme. See the README.md for details.
# Specify a software SPI connection for Raspberry Pi on the following pins:
#PIXEL_CLOCK = 18
#PIXEL_DOUT  = 23
#pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, clk=PIXEL_CLOCK, do=PIXEL_DOUT)

# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT = 0
SPI_DEVICE = 0
pixels = Adafruit_WS2801.WS2801Pixels(totalLEDs, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

#Should we even start all this stuff up or Sleep the Map
if ((currentHour >= sleepStart) and (sleepStart >= 0)) or ((currentHour < sleepStop) and (sleepStop >= 0)):
	pixels.clear()
	pixels.show()
	sys.exit()

######################################################
##################### Functions ######################
######################################################

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

def demoLEDsOn():
	if demoVFR > 0:
		setPixelRGB(demoVFR, int(colorVFR[0]),int(colorVFR[1]),int(colorVFR[2]))
	if demoMVFR > 0:
		setPixelRGB(demoMVFR, int(colorMVFR[0]),int(colorMVFR[1]),int(colorMVFR[2]))
	if demoIFR > 0:
		setPixelRGB(demoIFR, int(colorIFR[0]),int(colorIFR[1]),int(colorIFR[2]))
	if demoLIFR > 0:
		setPixelRGB(demoLIFR, int(colorLIFR[0]),int(colorLIFR[1]),int(colorLIFR[2]))
	if demoMissing > 0:
		setPixelRGB(demoMissing, int(colorMissing[0]),int(colorMissing[1]),int(colorMissing[2]))

def demoLEDsOff():
	if demoVFR > 0:
		setPixelRGB(demoVFR, 0, 0, 0)
	if demoMVFR > 0:
		setPixelRGB(demoVFR, 0, 0, 0)
	if demoIFR > 0:
		setPixelRGB(demoVFR, 0, 0, 0)
	if demoLIFR > 0:
		setPixelRGB(demoVFR, 0, 0, 0)
	if demoMissing > 0:
		setPixelRGB(demoVFR, 0, 0, 0)

def calcRGB(rgb, ID):
	debug("Winds: WindSpeed: " + str(stationsData[ID]["WS"]) + " MaxWind: " + str(windMax) + " GustSpeed: " + str(stationsData[ID]["GS"]) + " MaxGust: " + str(gustMax))
	if (int(stationsData[ID]["WS"]) > windMax) or (int(stationsData[ID]["GS"]) > gustMax):
		wd = windDim
	else:
		wd = 0
	newRGB = {}
	newRGB[0] = int(round(min(int(rgb[0]), int(maxBrightness)) * (1-Dimming) * (1-wd)))
	newRGB[1] = int(round(min(int(rgb[1]), int(maxBrightness)) * (1-Dimming) * (1-wd)))
	newRGB[2] = int(round(min(int(rgb[2]), int(maxBrightness)) * (1-Dimming) * (1-wd)))
	debug("RGB Value for LED is returned as: [" + str(newRGB[0]) + "," + str(newRGB[1]) + "," + str(newRGB[2]) + "]")
	return newRGB
	
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

def debug(var):
	if debugOn:
		print(var)

######################################################
#################### End Functions ###################
######################################################

#Load the Config.txt Vars
maxBrightness = float(config.get("generalSettings","maxBrightness"))
statusLED = int(config.get("extraLEDs","statusLED"))
metarLED = int(config.get("extraLEDs","metarLED"))

legendLEDs = {}
legendLEDs["VFR"] = int(config.get("extraLEDs", "legendVFR"))
legendLEDs["MVFR"] = int(config.get("extraLEDs", "legendMVFR"))
legendLEDs["IFR"] = int(config.get("extraLEDs", "legendIFR"))
legendLEDs["LIFR"] = int(config.get("extraLEDs", "legendLIFR"))
legendLEDs["Missing"] = int(config.get("extraLEDs", "legendMissing"))

windMax = int(config.get("windAlerts", "windMax"))
gustMax = int(config.get("windAlerts", "gustMax"))
windDim = float(config.get("windAlerts", "windDim"))

dimStart = int(config.get("dimHours", "dimStart"))
dimStop = int(config.get("dimHours", "dimStop"))
if ((currentHour >= dimStart) and (dimStart >= 0)) or ((currentHour < dimStop) and (dimStop >= 0)):
	Dimming = float(config.get("dimHours", "Dimming"))
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

#Test for script arguements present
if ("debug" in sys.argv):
	debugOn = True
else:
	debugOn = False

debug("\n-------------------------------------------\nSTARTING LIVE SECTIONAL\n-------------------------------------------\n")
	
if ("startup" in sys.argv):
	startUpLEDs()

if not connected():
	debug('Status: NOT Connected to internet. Setting statusLED Color to RED. \nNo use in continuing... Exiting Script!\n')
	setPixelRGB(statusLED, colorRGBs["Red"])
	sys.exit()
else:
	debug('Status: Connected to internet. Setting statusLED Color to GREEN\n')
	setPixelRGB(statusLED, colorRGBs["Green"])
	
	#Read in LED Address/Airport list
	with open("airports.txt") as f:
		ICAOs = f.readlines()
	ICAOs = [x.strip() for x in ICAOs]
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
		stationsData[sID]["FC"] = metar.find('flight_category').text
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
#print(stationsData)
showPixels()

debug("FINISHED")
debug("Script took: " + str(time.time() - start) + " Seconds")
