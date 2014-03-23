
#Uncomment in production
#if not auth.has_membership('admin'):
	#redirect(auth.settings.login_url)

@auth.requires_login()
def index():
	studies = db((db.study.id==db.participant.study) & (db.participant.auth_user == auth.user_id)).select(db.study.ALL)
	test_stuff = studies
	sql = db._lastsql
	return locals()

@auth.requires_login()
def edit_study_profile():
	gender_options = ['Male', 'Female', 'Neutral']
	change_study_alias=SQLFORM.factory(Field('Gender',requires=IS_IN_SET(gender_options), default='Male', widget=SQLFORM.widgets.radio.widget), submit_button=T('Change your alias'))
	
	return locals()