# tally2obsi-py — Porting Notally notes to Obsidian with regard to creation timestamps.

import json, os, re, sqlite3, subprocess
from datetime import datetime, timezone

# process start

print ("Starting conversion.")

pyDirectory = f"{os.path.dirname (os.path.abspath (__file__))}{os.path.sep}"
sqlConnect = sqlite3.connect (f"{pyDirectory}NotallyDatabase")
sqlCursor = sqlConnect.cursor()

# converts unix time to windows-parsable or human-readable time
def chrono (unixtime, formatted):
	stamp = datetime.fromtimestamp (unixtime / 1000.0)

	if formatted:
		return stamp.strftime ("%Y-%m-%d %H:%M:%S.%f")[:-3]
	else:
		return stamp.strftime ("%Y%m%d")

# converts list json arrays
def enlist (string, state):
	if state:
		state = "- [x]"
	else:
		state = "- [ ]"
	return f"{state} {string}"

# calls a system terminal to execute commands, windows
def system (command):
	subprocess.run (['powershell', '-Command', command], shell = True)

# purifies note title if invalid as NTFS file name
def purify (string):
	evils = re.compile (r'[<>:"/\\|?*\x00-\x1F]')
	return evils.sub ('_', string)

# retrieve number of notes
sqlCursor.execute ("""SELECT COUNT(*) FROM 'BaseNote' WHERE folder != 'DELETED'""") # skip deleted, lists to be done later
indices = sqlCursor.fetchone()[0]

i = 0 # same-day note iteration
preceedingTimestamp = None # same-day note comparison
for z in range (indices):
	# retrieve current row
	sqlCursor.execute ("""SELECT * FROM 'BaseNote' WHERE folder != 'DELETED' ORDER BY timestamp LIMIT ?, 1""", (z,))
	currentId, currentType, currentFolder, currentColor, currentTitle, currentPinned, currentTimestamp, currentLabels, currentBody, currentSpans, currentItems, currentImages = sqlCursor.fetchone()

	# retrieve succeeding row unless final
	if z < indices - 1: # -1 because range() counts from 0, as it should
		sqlCursor.execute ("""SELECT * FROM 'BaseNote' WHERE folder != 'DELETED' ORDER BY timestamp LIMIT ?, 1""", (z + 1,))
		succeedingId, succeedingType, succeedingFolder, succeedingColor, succeedingTitle, succeedingPinned, succeedingTimestamp, succeedingLabels, succeedingBody, succeedingSpans, succeedingItems, succeedingImages = sqlCursor.fetchone()

	# check if succeeding or preceeding notes were made on the same day
	if chrono (currentTimestamp, False) == chrono (succeedingTimestamp, False) or chrono (currentTimestamp, False) == chrono (preceedingTimestamp, False):
		prefix = f"{chrono (currentTimestamp, False)} {str(i).zfill(2)}"
		i += 1
	else:
		prefix = chrono (currentTimestamp, False)
		i = 0
	preceedingTimestamp = currentTimestamp

	# if file has title, use it; if none, omit
	if currentTitle != '':
		filename = f"{prefix} – {currentTitle}. {currentTimestamp}"
	else:
		filename = f"{prefix} – {currentTimestamp}"
	
	filepath = f"{pyDirectory}{purify (filename)}.md"

	# show progress
	print (f"Writing {filepath}...")

	# create file; if list, write currentBody from currentItems
	with open (filepath, 'w', encoding = 'utf-8') as file:
		if currentType == "LIST":
			currentItems = json.loads (currentItems)
			for item in currentItems:
				currentBody += f"{enlist (item["body"], item["checked"])}\n"
		file.write (currentBody.strip())

		# update NTFS file creation timestamp, windows // unreliable if not under with
		system (f'(Get-Item "{filepath}").CreationTime = (Get-Date "{chrono (currentTimestamp, True)}")')

print ("No more rows retrievable; conversion complete!")
sqlConnect.close()
