
#Uncomment in production
if not auth.is_logged_in():
	redirect(auth.settings.login_url)


     

def index():
	studies = db((db.study.id==db.participant.study) & (db.participant.auth_user == auth.user_id)).select(db.study.ALL)
	test_stuff = studies
	sql = db._lastsql
	return locals()


@is_in_study(request.args(0))
def study():
	participant = db.participant((db.participant.study == request.args(0)) & (db.participant.auth_user == auth.user_id)) or redirect (URL('index'))
	study = db.study(participant.study)	
	gender_options = ['Male', 'Female', 'Neutral']
	current_gender = participant.participant_alias.gender
	change_study_alias=SQLFORM.factory(Field('Gender',requires=IS_IN_SET(gender_options), default=participant.participant_alias.gender, widget=SQLFORM.widgets.radio.widget), submit_button=T('Change your alias'))
	if change_study_alias.process().accepted:
		participant.update_record(participant_alias=get_random_alias(change_study_alias.vars.Gender))
		session.flash=T('Alias Changed')
		redirect(URL('study', args=request.args(0)))
	elif change_study_alias.errors:
		response.flash=T('Form has Errors')
	sql = db._lastsql
	return locals()

@is_in_study(request.args(0))
def collect():
	#study = db.study((db.participant.study == request.args(0)) & (db.participant.auth_user == auth.user_id)) or redirect (URL('index'))
	participant = db.participant((db.participant.study == request.args(0)) & (db.participant.auth_user == auth.user_id))
	study = db.study(participant.study)		
		
	is_consent = False

	if stages.index(participant.study_stage) <= stages.index(study.study_stage):
		if participant.study_stage == "Consenting":
			is_consent = True
			cform = FORM.confirm(T('I agree to the study'),{T('I DO NOT agree to the study'):URL('other_page')}) #TODO: Take user to complaints/email page
			consent_text = study.consent_form
			if cform.accepted:
				participant.update_record(study_stage=stages[stages.index('Consenting')+1]) #Hack to update entry to next stage
				redirect(URL('collect', args=study.id))
		elif (participant.study_stage == "Soliciting") & (study.study_stage=='Soliciting'):
			redirect(URL('solicit', args=request.args(0)))
		elif (study.study_stage == 'Sorting'):
			if participant.study_stage != 'Sorting':
				participant.update_record(study_stage='Sorting')
			redirect(URL('sort', args=request.args(0)))
		else:
			redirect(URL('stages_complete', args=request.args(0)))
	else:
		redirect(URL('stages_complete', args=request.args(0)))
	
	sql = db._lastsql

	return locals()

@is_in_study(request.args(0))
def solicit():
	participant = db.participant((db.participant.study == request.args(0)) & (db.participant.auth_user == auth.user_id))
	study = db.study(participant.study)

	if study.study_stage != 'Soliciting':
		redirect(URL('index'))

	qstatements = db(db.qstatement.participant == participant).select(orderby=~db.qstatement.id)
	db.qstatement.participant.default = participant.id
	db.qstatement.study.default = study.id
	unanswered_num = study.num_questions - len(qstatements)

	field_list = []

	for i in range(0,unanswered_num):
		field_list.append(Field('desc:'+str(i), 'text', label=''))

	for i,q in enumerate(qstatements):
		field_list.append(Field('prev:'+str(q.id), 'text', default=q.description, label=''))

	f = SQLFORM.factory(*field_list)

	prompt = study.qstatement_prompt
	keys = f.vars.items()
	if f.process().accepted:
		keys = f.vars.keys()
		for nam in f.vars:
			if 'prev' in nam:
				qstatement_id = nam.split(':')[1] #Get the id of the record
				if f.vars[nam] == '':
					db(db.qstatement.id == qstatement_id).delete()
				else:
					db(db.qstatement.id == qstatement_id).update(description=f.vars[nam])
			elif ('desc' in nam) & (f.vars[nam] != ''):
				db.qstatement.insert(description=f.vars[nam])
		session.flash=T('Study Updated')
		redirect(URL('solicit', args=request.args(0)))
	elif f.errors:
		response.flash=T('Form has Errors')

	sql = db._lastsql
	return locals()	

def stages_complete():
	study = db.study(db.participant.study == request.args(0)) or redirect (URL('index'))
	
	completed_stage_text = T('You have completed all available study stages. You will be notified if additional assistance is required.')
	return locals()

@is_in_study(request.args(0))
def sort():
	participant = db.participant((db.participant.study == request.args(0)) & (db.participant.auth_user == auth.user_id))
	study = db.study(participant.study)
	
	if study.study_stage != 'Sorting':
		redirect(URL('index'))

	db.q_answer.participant.default = participant.id
	db.q_answer.study.default = study.id
 
	qstatements = db(db.qstatement.study == study).select(orderby='<random>')
	answered = db(db.q_answer.participant == participant).select()

	
	q_list = [a.qstatement for a in answered]

	# Retrieve qstatements that have not been boxed before
	unboxed = db(~db.qstatement.id.belongs(q_list)).select()
	unsorted = db((db.q_answer.participant == participant) & (db.q_answer.ranking == None)).select()

	if len(unboxed) > 0:
		qstatement = unboxed[0]
		box_form = FORM(INPUT(_type='submit', _name='disagree', _value='Disagree'),INPUT(_type='submit', _name='neutral', _value='Neutral'), INPUT(_type='submit', _name='agree', _value='Agree'))
		test = []
		if box_form.process().accepted:
			if box_form.vars.disagree:
				db.q_answer.insert(qstatement=qstatement,box='Disagree')
			elif box_form.vars.agree:
				db.q_answer.insert(qstatement=qstatement,box='Agree')
			elif box_form.vars.neutral:
				db.q_answer.insert(qstatement=qstatement,box='Neutral')
			redirect(URL('sort', args=request.args(0)))
		else:
			response.flash==T('Form has Errors')
	#elif len(unsorted) > 0:
		#
	sql = db._lastsql


	return locals()