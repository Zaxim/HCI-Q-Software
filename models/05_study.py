#Information associated with a study

db.define_table('study',
	Field('name', notnull=True),
	Field('description', 'text', widget=ckeditor.widget),
	Field('study_stage', requires=IS_IN_SET(stages), default='Initial'),
	Field('consent_form', 'text', widget=ckeditor.widget),
	Field('qstatement_prompt', 'text'),
	Field('num_questions', 'integer', requires=IS_INT_IN_RANGE(0,501)),
	format='%(name)s')

db.define_table('participant',
	Field('participant_alias', 'reference participant_alias', unique=True),
	Field('auth_user', 'reference auth_user'),
	Field('study', 'reference study'),
	Field('study_stage', requires=IS_IN_SET(stages)),
	format='%(participant_alias)s'
	)

db.define_table('qstatement',
	Field('participant', 'reference participant'),
	Field('study', 'reference study'),
	Field('description', 'text', notnull=True),
	Field('modified', 'datetime', default=request.utcnow, update=request.utcnow),
	format='%(description)s')

db.define_table('q_answer',
	Field('qstatement', 'reference qstatement'),
	Field('participant', 'reference participant'),
	Field('study', 'reference study'),
	Field('ranking', 'integer'),
	Field('box', requires=IS_IN_SET([None, 'Disagree', 'Neutral', 'Agree'])),
	format='%(ranking)s'
	)

