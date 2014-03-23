import csv
import re

female_names = []
male_names = []
neutral_names = []
bad_vals = re.compile(r"\:\[|\(|[0-9]|\'s|slave|sex|maternal|praternal|sister|brother|wife|daughter|husband|unidentified|aunt|uncle|cousin|friend|mother|father|queen|king|captain|admiral|guardian", re.IGNORECASE)
bad_terms = re.compile(r"\[|\(|sex|slave|maternal|sister|brother|wife|daughter|husband|unidentified|aunt|uncle|cousin|friend|mother|father|queen|king|captain|admiral|guardian", re.IGNORECASE)
neutral_vals = re.compile(r"[0-9]")


with open('female_names.csv', 'rb') as f:
	reader = csv.reader(f)
	for r in reader:
		female_names = r

with open('female_names.csv', 'wb') as f:
	neutral_names = [x for x in female_names if neutral_vals.search(x)]
	female_names = [x for x in female_names if not bad_vals.search(x)]
	wr = csv.writer(f)
	wr.writerow(female_names)


with open('male_names.csv', 'rb') as f:
	reader = csv.reader(f)
	for r in reader:
		male_names = r

with open('male_names.csv', 'wb') as f:
	neutral_names.extend([x for x in male_names if neutral_vals.search(x)])
	male_names = [x for x in male_names if not bad_vals.search(x)]
	wr = csv.writer(f)
	wr.writerow(male_names)

print male_names

with open('neutral_names.csv', 'wb') as f:
	neutral_names = [x for x in neutral_names if not bad_terms.search(x)]
	wr = csv.writer(f)
	wr.writerow(neutral_names)

print("done")




