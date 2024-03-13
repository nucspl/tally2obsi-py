# Tallysidian Project — Porting Notally notes to Obsidian with regard to creation timestamps.

import os, re, sqlite3, subprocess # windows only!
from datetime import datetime, timedelta, timezone

cfd = f'{os.path.dirname (os.path.abspath (__file__))}' # current file directory
con = sqlite3.connect (f'{cfd}\{"NotallyDatabase"}')
cur = con.cursor()

def substringer (d, s):
	for n in os.listdir (d):
		if s in n:
			return True
	return False

def unixStamper (ms):
	whole = ms / 1000.0
	dtobj = datetime.utcfromtimestamp (whole).replace (tzinfo = timezone.utc).astimezone()
	human = dtobj.strftime ('%Y-%m-%d %H:%M:%S.%f')[:-3] # del micro
	return human

def holoStamper (ms):
	whole = ms / 1000.0
	dtobj = datetime.utcfromtimestamp (whole).replace (tzinfo = timezone.utc).astimezone()
	human = dtobj.strftime ('117%y%m%d')
	return human

def powershell (command):
	subprocess.run (["powershell", "-Command", command], shell = True)

def sanitiser (string):
	evils = re.compile (r'[<>:"/\\|?*\x00-\x1F]')
	clean = evils.sub('#', string)
	return clean

i = 1
for row in cur.execute ('''SELECT * FROM BaseNote'''):
	id, type, folder, color, title, pinned, timestamp, labels, body, spans, items, images = row
	
	if folder == 'DELETED' or type == 'LIST':
		continue
	
	if substringer (cfd, holoStamper (timestamp)):
		stamp = f'{holoStamper (timestamp)} {str (i).zfill (2)}'
		i += 1 # increment for next occurrence
	else:
		stamp = holoStamper (timestamp)
		i = 1 # reset
	
	if title != '':
		name = f'{stamp} – {title}. {timestamp}'.strip()
	else:
		name = f'{stamp} – {timestamp}'.strip()

	path = f'{cfd}\{sanitiser (name)}.md'

	with open (path, 'w', encoding = "utf-8") as file:
		file.write (str (body))
	
	powershell (f'(Get-Item "{path}").CreationTime = (Get-Date "{unixStamper (timestamp)}")')	

con.close()
print ('Database to Markdown export success!')