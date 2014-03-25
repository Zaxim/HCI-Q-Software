
#Uncomment in production
if not auth.is_logged_in():
	redirect(auth.settings.login_url)


     

def index():
	studies = db((db.study.id==db.participant.study) & (db.participant.auth_user == auth.user_id)).select(db.study.ALL)
	test_stuff = studies
	sql = db._lastsql
	return locals()

@is_in_study(request.args(0))
def edit_study_profile():
	participant = db.participant((db.participant.study == request.args(0)) & (db.participant.auth_user == auth.user_id)) or redirect (URL('index'))
	user_id = auth.user_id
	gender_options = ['Male', 'Female', 'Neutral']
	change_study_alias=SQLFORM.factory(Field('Gender',requires=IS_IN_SET(gender_options), default='Male', widget=SQLFORM.widgets.radio.widget), submit_button=T('Change your alias'))
	if change_study_alias.process().accepted:
		participant.update(participant_alias=get_random_alias(change_study_alias.vars.Gender))
		response.flash=T('Study Updated')
	elif change_study_alias.errors:
		response.flash=T('Form has Errors')
	sql = db._lastsql
	return locals()

@is_in_study(request.args(0))
def collect():
	study = db.study((db.participant.study == request.args(0)) & (db.participant.auth_user == auth.user_id)) or redirect (URL('index'))
	participant = db.participant((db.participant.study == request.args(0)) & (db.participant.auth_user == auth.user_id))
	
	def consent():
		noway = "try this"
		return locals()
		

	consenting = consent()


	return locals()