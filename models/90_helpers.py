
def get_random_alias(gender="Male"):
	#random_record = []
	while True:
		random_record = db(db.participant_alias.gender == gender).select(db.participant_alias.ALL,orderby='<random>',limitby= (0,1))[0]
		if not db(db.participant.participant_alias == random_record.id).select():
			break

	return random_record

def is_in_study(study_id):
	''' Decorator that prevents access to function if not a member of a specified study ID
	'''
	def real_decorator(f):
		def wrapper(*args, **kwargs):
			studies = db((db.study.id==db.participant.study) & (db.participant.auth_user == auth.user_id) & (db.study.id == study_id)).select(db.study.id)
			if not studies:
				redirect(URL('user', 'index'))
			else:
				return f(*args, **kwargs)
		return wrapper
	return real_decorator

		# study_id=1
		# studies = db((db.study.id==db.participant.study) & (db.participant.auth_user == auth.user_id) & (db.study.id == study_id)).select(db.study.id)
		# if not studies:
		# 	redirect(URL('user', 'index'))
		# else:
		# 	return f