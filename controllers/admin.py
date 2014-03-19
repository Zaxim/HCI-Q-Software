
#Uncomment in production
#if not auth.has_membership('admin'):
	#redirect(auth.settings.login_url)


def index():
	redirect(URL('studies'))

def studies():
	studies = db(db.study).select(orderby=db.study.name)
	return locals()

def study():
	study_id = db.study(request.args(0)) or redirect (URL('studies'))
	db.study.id.readable = False
	db.study.id.writeable = False
	study_form = SQLFORM(db.study, study_id)
	if study_form.process().accepted:
		response.flash=T('Study Updated')
	elif study_form.errors:
		response.flash=T('Form has Errors')

	participants = db(db.participant.study==study_id.id).select()

	left_join = db.participant.on(db.auth_user.id==db.participant.auth_user)
	rows = db((db.participant.id == None) | (db.participant.study != study_id)).select(db.auth_user.ALL, db.participant.ALL,left=left_join)
	
	user_list_id=[]
	user_list_label = []
	for row in rows:
		user_list_id.append(row.auth_user.id)
		user_list_label.append('{0} {1}'.format(row.auth_user.first_name, row.auth_user.last_name))

	add_user_form=SQLFORM.factory(Field('Users',requires=IS_IN_SET(user_list_id, labels=user_list_label, multiple=True)))
	
	if add_user_form.process().accepted:
		for user_id in add_user_form.vars.Users:
			db.participant.insert(auth_user=user_id, study=study_id)
		redirect(URL('study', args=study_id))
		session.flash=T('Study Updated')
	elif add_user_form.errors:
		response.flash=T('Form has Errors')

	return locals()

def add_study():
	study_form = SQLFORM(db.study)
	study_form.add_button("Cancel", URL('admin','studies'))
	if study_form.process().accepted:
		redirect(URL('study',args=study_form.vars.id))
	elif study_form.errors:
		response.flash=T('Form has Errors')
	return locals()


#@auth.requires_membership('admin')
def participant():
	participant_id = db.participant(request.args(0)) or redirect (URL('studies'))
	db.participant.id.readable = False
	db.participant.id.writeable = False
	participant_form = SQLFORM(db.participant, participant_id, deletable=True)
	participant_form.add_button("Cancel", URL('admin','study', args=participant_id.study))
	if participant_form.process().accepted:
		response.flash=T('Form Accepted')
		redirect(URL('admin','study', args=participant_id.study))
	elif participant_form.errors:
		response.flash=T('Form has Errors')
	return locals()

def invite_users():
	invalid_emails=[]
	new_users=[]
	invite_user_form=SQLFORM.factory(Field('Emails'))
	auth_stuff = []
	if invite_user_form.process().accepted:
		email_list = invite_user_form.vars.Emails.split(',')
		for e in email_list:
			em, valid = IS_EMAIL() (e)
			if valid is not None:
				invalid_emails.append(em)
			else:
				if db(db.auth_user.email != em).select():
					password = db.auth_user.password.requires[0](auth.random_password)[0]
					auth.get_or_create_user({'email':em, 'password':password})
					new_users.append(em)
		
		session.flash=T('Study Updated')

	elif invite_user_form.errors:
		response.flash=T('Form has Errors')
	return locals()

