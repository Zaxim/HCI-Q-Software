import requests
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

URL_API="http://starwars.wikia.com/api.php"
#http://starwars.wikia.com/api.php?action=query&list=categorymembers&cmtitle=Category:Females&cmlimit=max&cmprop=title
parms = {'format':'xml', 'action':'query', 'list' : 'categorymembers', 'cmtitle':'Category:Females', 'cmlimit':'500','cmprop': 'title', 'cmcontinue':''}


female_names=[]




for i in range(0,10):
	resp = requests.get(URL_API, params=parms)
	#print resp.text
	tree = resp.text.encode('utf-8')
	root = ET.fromstring(tree)
	for elem in root.iter('cm'):
		female_names.append(elem.get('title'))

	for elem in root.iter('categorymembers'):
		parms['cmcontinue'] = elem.get('cmcontinue')

print female_names
