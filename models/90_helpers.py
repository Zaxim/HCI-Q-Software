import random

def get_random_alias(gender="Male"):
	"""
	Returns a random participant_alias, retries until it picks an alias not already used
	"""
	while True:
		random_record = db(db.participant_alias.gender == gender).select(db.participant_alias.ALL,orderby='<random>',limitby= (0,1))[0]
		if not db(db.participant.participant_alias == random_record.id).select():
			break

	return random_record

def is_in_study(study_id):
	"""
	Decorator that prevents access to function if not a member of a specified study ID
	"""
	def real_decorator(f):
		def wrapper(*args, **kwargs):
			studies = db((db.study.id==db.participant.study) and (db.participant.auth_user == auth.user_id) and (db.study.id == study_id)).select(db.study.id)
			if not studies:
				redirect(URL('user', 'index'))
			else:
				return f(*args, **kwargs)
		return wrapper
	return real_decorator

def pick_order_list(sorted_ans):
	if len(sorted_ans) == 0:
		return []
	elif (len(sorted_ans) == 1) or (len(sorted_ans) == 2):
		return sorted_ans[:]
	else:
		return [sorted_ans[0], sorted_ans[len(sorted_ans)//2], sorted_ans[-1]]