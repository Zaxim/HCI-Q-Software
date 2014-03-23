import requests
import csv
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

URL_API="http://starwars.wikia.com/api.php"
#http://starwars.wikia.com/api.php?action=query&list=categorymembers&cmtitle=Category:Females&cmlimit=max&cmprop=title
parms_f = {'format':'xml', 'action':'query', 'list' : 'categorymembers', 'cmtitle':'Category:Females', 'cmlimit':'500','cmprop': 'title', 'cmcontinue':''}
parms_m = {'format':'xml', 'action':'query', 'list' : 'categorymembers', 'cmtitle':'Category:Males', 'cmlimit':'500','cmprop': 'title', 'cmcontinue':''}


female_names=[]
male_names=[]




for i in range(0,10):
	resp = requests.get(URL_API, params=parms_f)
	#print resp.text
	tree = resp.text.encode('utf-8')
	root = ET.fromstring(tree)
	for elem in root.iter('cm'):
		female_names.append(elem.get('title'))

	for elem in root.iter('categorymembers'):
		parms_f['cmcontinue'] = elem.get('cmcontinue')

print female_names
myfile = open('female_names.csv', 'wb')
wr = csv.writer(myfile)
wr.writerow([s.encode("utf-8") for s in female_names])
myfile.close()

for i in range(0,35):
	resp = requests.get(URL_API, params=parms_m)
	#print resp.text
	tree = resp.text.encode('utf-8')
	root = ET.fromstring(tree)
	for elem in root.iter('cm'):
		male_names.append(elem.get('title'))

	for elem in root.iter('categorymembers'):
		parms_m['cmcontinue'] = elem.get('cmcontinue')

print male_names
myfile = open('male_names.csv', 'wb')
wr = csv.writer(myfile)
wr.writerow([s.encode("utf-8") for s in male_names])
myfile.close()
