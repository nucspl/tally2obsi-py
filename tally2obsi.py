# tally2obsi-py — Porting Notally notes to Obsidian with regard to creation timestamps.

import os, re, sqlite3, subprocess
from datetime import datetime, timezone

print ('Conversion start.')

fdir = f'{os.path.dirname (os.path.abspath (__file__))}{os.path.sep}'
scon = sqlite3.connect (f'{fdir}NotallyDatabase')
scur = scon.cursor()

def sstri (directory, substring):
	for filename in os.listdir (directory):
		if substring in filename:
			return True
	return False

def ustam (unixtime, formatted):
	local = datetime.fromtimestamp (unixtime / 1000.0, tz = timezone.utc)
	
	if formatted:
		human = local.strftime ('%Y-%m-%d %H:%M:%S.%f')[:-3]
	else:
		human = local.strftime ('%Y%m%d')
		
	return human

def scons (command):
	subprocess.run (['powershell', '-Command', command], shell = True)

def nclea (string):
	evils = re.compile (r'[<>:"/\\|?*\x00-\x1F]')
	clean = evils.sub ('_', string)
	return clean

i = 1
for row in scur.execute ('''SELECT * FROM BaseNote ORDER BY timestamp'''):
	id, type, folder, color, title, pinned, timestamp, labels, body, spans, items, images = row

	if folder == 'DELETED' or type == 'LIST': # lists are weirdly implemented, won't bother for now
		continue

	if sstri (fdir, ustam (timestamp, False)):
		stamp = f'{ustam (timestamp, False)} {str (i).zfill (2)}'
		i += 1
	else:
		stamp = ustam (timestamp, False)
		i = 1
	
	if title != '':
		name = f'{stamp} – {title}. {timestamp}'.strip()
	else:
		name = f'{stamp} – {timestamp}'.strip()
	
	path = f'{fdir}{nclea (name)}.md'

	with open (path, 'w', encoding = 'utf-8') as file:
		file.write (body)
	
	scons (f'(Get-Item "{path}").CreationTime = (Get-Date "{ustam (timestamp, True)}")')

scon.close()
print ('Conversion complete!')
