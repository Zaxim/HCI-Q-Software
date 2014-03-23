
def get_random_alias(gender="Male"):
	random_record = []
	while True:
		random_record = db(db.participant_alias.gender == gender).select(db.participant_alias.ALL,orderby='<random>',limitby= (0,1))[0]
		if not db(db.participant.participant_alias == random_record.id).select():
			break

	return random_record