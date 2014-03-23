import csv
import re

file_names = ['female_names.csv','male_names.csv','neutral_names.csv']
genders = ['Female', 'Male', 'Neutral']



csv_file = open('aliases.csv', 'wb')
wr = csv.writer(csv_file)
wr.writerow(['participant_alias.id','participant_alias.alias_name','participant_alias.gender'])

for f, g in zip(file_names,genders):
	with open (f, 'rb') as fh:
		reader = csv.reader(fh)
		rows = []
		for r in reader:
			rows.extend(r)
		for n in rows:
			wr.writerow(["", n, "|"+g+"|"])

csv_file.close()