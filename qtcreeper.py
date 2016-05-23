#!/usr/bin/env python

# qtcreeper.py
# https://github.com/anonimousse12345/qtcreeper
# Based on interpals-autovisit.py by Hexalyse, https://github.com/Hexalyse
# Requires python 2.7 and the python requests module

import os
import json
import random
import time
import requests
import re

from lxml.html import fromstring


# Number of users shown by interpals per search page
MATCHES_PER_SEARCH = 20

# Masquerade as a random one of these web browsers
USER_AGENTS = [
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/601.5.17 (KHTML, like Gecko) Version/9.1 Safari/601.5.17",
	"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"
]

CONTINENTS = [
	("AF", "Africa"),
	("AS", "Asia"),
	("EU", "Europe"),
	("NA", "North America"),
	("OC", "Oceania"),
	("SA", "South America")
]

DEFAULT_CONFIG = {
	"continents" : [ x[0] for x in CONTINENTS ],
	"countries" : [],
	"age1" : 40,
	"age2" : 80,
	"sex" : ["MALE"],
	"email" : "",
	"password" : "",
	"creepspeed" : 1,
	"useragent" : random.choice(USER_AGENTS)
}


DATA_DIR = os.path.join( os.path.expanduser("~"), ".qtcreeper" )
CONFIG_FILE = os.path.join( DATA_DIR, "config.json" )
USERS_VISITED_FILE = os.path.join( DATA_DIR, "users_visited.txt" )

if not os.path.exists(DATA_DIR):
	os.makedirs(DATA_DIR)


def get_number(promptText):
	print promptText
	
	while True:
		try:
			r = int(raw_input("> "))
			return r
		except ValueError:
			pass
		
		print "Invalid selection, try again!"

def get_number_from_list(promptText, allowedOptions):
	print promptText
	
	while True:
		try:
			r = int(raw_input("> "))
			
			if r in allowedOptions:
				return r
		except ValueError:
			pass
		
		print "Invalid selection, try again!"

def get_iso_codes(promptText, allowedOptions = None):
	print promptText
	
	while True:
		r = raw_input("> ")
		
		if r == "":
			return []
		
		isoCodes = [x.strip().upper() for x in r.split(",")]
		
		fail = False
		
		# We just check they are two characters
		for isoCode in isoCodes:
			if len(isoCode) != 2 or (allowedOptions and isoCode not in allowedOptions):
				fail = True
				break
		
		if not fail:
			return isoCodes
		
		print "Input invalid, try again!"


config = {}

print "Welcome to qtcreeper!"
print "--> https://github.com/anonimousse12345/qtcreeper"

if os.path.exists(CONFIG_FILE):
	with open(CONFIG_FILE, "r") as f:
		config = json.loads(f.read())
	
	# Ensure any later added default keys exist
	for k, v in DEFAULT_CONFIG.iteritems():
		if not k in config:
			config[k] = v
else:
	# Default config
	config = DEFAULT_CONFIG


usersVisited = set()

# Load users already visited
if os.path.exists(USERS_VISITED_FILE):
	with open(USERS_VISITED_FILE, "r") as f:
		for line in f:
			usersVisited.add(line.strip())


while True:
	command = get_number_from_list("\nPlease select an option and press enter:"
		+ "\n 1 - set account email and password (%s)" % (config["email"] or "NOT SET!")
		+ "\n 2 - set gender and age range (%s, %d to %d)" % (",".join(config["sex"]), config["age1"], config["age2"])
		+ "\n 3 - set continents (%s)" % (",".join(config["continents"]))
		+ "\n 4 - set countries (%s)" % (",".join(config["countries"] or ["All"]))
		+ "\n 5 - set creeper speed (%d)" % (config["creepspeed"])
		+ "\n 6 - clear users already visited file (%d users visited)" % len(usersVisited)
		+ "\n 7 - run creeper!"
		,[1,2,3,4,5,6,7])

	if command == 1:
		print "\nEnter email address:"
		config["email"] = raw_input("> ").strip().lower()
		print "\nEnter password:"
		config["password"] = raw_input("> ")

	elif command == 2:
		# Get genders
		genders = get_number_from_list("\nWhat genders to crawl? 1 = female, 2 = male, 3 = both", [1,2,3])
		config["sex"] = {1 : ["FEMALE"], 2 : ["MALE"], 3 : ["MALE", "FEMALE"]}[genders]
		
		# Get age range
		config["age1"] = get_number("\nMinimum age?")
		config["age2"] = get_number("\nMaximum age?")
		
		if config["age1"] < 16:
			config["useragent"] = "Pedovision 9000"

	elif command == 3:
		# Continents
		config["continents"] = get_iso_codes("\nEnter a comma separated list of any of these continent codes, or nothing for all continents:\n"
			+ "\n".join([(x[0] + " - " + x[1] + " ") for x in CONTINENTS]), [ x[0] for x in CONTINENTS ])
		
		if len(config["continents"]) == 0:
			config["continents"] = [ x[0] for x in CONTINENTS ]

	elif command == 4:
		# Countries
		config["countries"] = get_iso_codes("\nEnter a comma separated list of two letter country codes, or nothing for all countries:")
	
	elif command == 5:
		# Set creep speed
		config["creepspeed"] = get_number_from_list("\nEnter a speed between 1 and 10 (1 = slow and realistic, 10 = stupid fast):",
			range(1,11))
	
	elif command == 6:
		# Clear users visited
		if os.path.exists(USERS_VISITED_FILE):
			os.remove(USERS_VISITED_FILE)
		usersVisited = set()
	
	elif command == 7:
		if config["email"] == "" or config["password"] == "":
			print "\nSet email and password first!"
		else:
			print "\nRunning creeper..."
			break
	
	# Save any changes
	with open(CONFIG_FILE, "w") as f:
		f.write( json.dumps(config, indent=4) )
	
	print "\n* Changes saved..."


# File to log users already visited
usersVisitedFp = open(USERS_VISITED_FILE, "a")

def record_user_visited(username):
	username = username.strip()
	usersVisited.add(username)
	usersVisitedFp.write(username + "\n")
	usersVisitedFp.flush()


# Main crawler code below


# Short pause between regular pageloads
def default_wait():
	print "\nWaiting..."
	time.sleep(random.uniform(2,5))

# Longer(?) pause between user views
def user_view_wait():
	sleepTime = random.uniform(5,15) / config["creepspeed"]
	print "\nWaiting %f seconds..." % sleepTime
	time.sleep(sleepTime)


# Start a session
client = requests.Session()
client.headers["Host"] = "www.interpals.net"
client.headers["User-Agent"] = config["useragent"]

print "\nVisiting main page..."

r = client.get("https://www.interpals.net/")
client.headers["Referer"] = "https://www.interpals.net/"

tree = fromstring(r.text)
csrf_token = tree.xpath('//meta[@name="csrf-token"]/@content')[0]

print "\n* Got CSRF Token: %s" % csrf_token

default_wait()

print "\nAttempting login..."

params = {
	"username": config["email"],
	"auto_login": "1",
	"password": config["password"],
	"csrf_token" : csrf_token
}

r = client.post("https://www.interpals.net/app/auth/login", data=params)
client.headers["Referer"] = "https://www.interpals.net/account.php"

print "\n", r.request.headers

if r.text.find("My Profile") == -1:
    print "\nError: login failed. Either email/password incorrect or qtcreeper needs updating."
    
    #with open("debug.txt", "w") as f:
	#	f.write(r.text)
    
    exit(1)
else:
    print "\n* Successfully logged in!"

default_wait()

print "\nVisiting search page..."
r = client.get("https://www.interpals.net/app/search")
client.headers["Referer"] = "https://www.interpals.net/app/search"

default_wait()


def build_search_url(previousPageNum, desiredPageNum, onlineOnly):
	# Age
	url = "https://www.interpals.net/app/search?age1=%d&age2=%d" % (config["age1"], config["age2"])
	
	# Gender(s)
	for i in range(0, len(config["sex"])):
		url += "&sex[%d]=%s" % (i, config["sex"][i])
	
	# Sorting method
	url += "&sort=last_login"
	
	# Continents
	for i in range(0, len(config["continents"])):
		url += "&continents[%d]=%s" % (i, config["continents"][i])
	
	# "Looking for"
	url += "&lfor[0]=lfor_email&lfor[1]=lfor_snail&lfor[2]=lfor_langex&lfor[3]=lfor_friend&lfor[4]=lfor_flirt&lfor[5]=lfor_relation"
	
	# First offset, the previous offset/page we were on
	url += "&offset=%d" % (previousPageNum * MATCHES_PER_SEARCH)
	
	# Online?
	if onlineOnly:
		url += "&online=on"
	
	# Countries (some strange variable length array)
	url += "&countries[0]=---"
	
	for i in range(0, len(config["countries"])):
		url += "&countries[%d]=%s" % (i+1, config["countries"][i])
	
	if len(config["countries"]) > 0:
		url += "&countries[%d]=---" % (len(config["countries"])+1)
	
	# Second offset, the actual offset/page to get
	url += "&offset=%d" % (desiredPageNum * MATCHES_PER_SEARCH)
	
	return url


currentSearchPage = 0
onlineOnly = True # online only by default, but disabled automatically if no users found???
totalViewedCount = 0
totalSkippedCount = 0
ranOutOfUsers = False

while True:
	# Query search page
	
	userSearchUrl = build_search_url(max(0,currentSearchPage-1), currentSearchPage, onlineOnly)
	print "\nQuerying search page %d using search URL: %s" % (currentSearchPage, userSearchUrl)
	
	r = client.get(userSearchUrl)
	client.headers["Referer"] = userSearchUrl
	
	# Extract usernames
	usernames = re.findall(r'Report ([a-zA-Z0-9\-_]+) to moderators', r.text, re.M)
	print "\nFound %d users on search page %d." % (len(usernames), currentSearchPage)
	
	default_wait()
	
	# No users were found?
	if len(usernames) == 0:
		print "\n!!!!!!! NO MORE USERS FOUND !!!!!!!"
		print "\nMay have reached end of users. Will now start again including offline users in search."
		print "\n(Otherwise, try using broader search terms.)"
		currentSearchPage = 0
		onlineOnly = False
		ranOutOfUsers = True
		default_wait()
		continue
	
	# Through users
	viewedCount = 0
	skippedCount = 0
	
	for username in usernames:
		if username not in usersVisited:
			print "\nVisiting user %s" % username
			client.get("https://www.interpals.net/" + username)
			
			record_user_visited(username)
			viewedCount += 1
			totalViewedCount += 1
			
			user_view_wait()
		else:
			print "\nAlready visited user %s, skipping..." % username
			skippedCount += 1
			totalSkippedCount += 1
	
	print "\n*** RESULTS SO FAR ***\n"
	print " Search page #%d" % currentSearchPage
	print " Visited %d new users this page, %d were already visited." % (viewedCount, skippedCount)
	print " Visited %d new users in total, %d were already visited." % (totalViewedCount, totalSkippedCount)
	
	if ranOutOfUsers:
		print "\n!!! WARNING: At one point the script ran out of online users, and started including offline users."
	
	# Next page of search
	currentSearchPage += 1
	default_wait()


# Close users visited file??
usersVisitedFp.close()

