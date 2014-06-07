#Information associated with a study

db.define_table('study',
	Field('name', notnull=True),
	Field('description', 'text', widget = ckeditor.widget),
	Field('consent_form', 'text', widget = ckeditor.widget),
	Field('num_questions', 'integer', requires=IS_INT_IN_RANGE(0,501)),
	Field('box_size', 'integer', requires=IS_INT_IN_RANGE(0,501)),
	Field('feedback_questions', 'integer', requires=IS_INT_IN_RANGE(0,501)),
	Field('study_stage', requires=IS_IN_SET(stages), default='Initial'),
	format='%(name)s')

db.define_table('participant',
	Field('participant_alias', 'reference participant_alias', unique=True),
	Field('auth_user', 'reference auth_user'),
	Field('study', 'reference study'),
	Field('study_stage', requires=IS_IN_SET(stages)),
	Field('is_unsuitable', 'boolean', default=False),
	Field('is_sort_complete', 'boolean', default=False),
	format=lambda r: r.participant_alias.alias_name
	)

db.define_table('qprompt',
	Field('study', 'reference study'),
	Field('description', 'text', notnull=True),
	format='%(description)s'
	)

db.define_table('qstatement',
	Field('participant', 'reference participant'),
	Field('study', 'reference study'),
	Field('qprompt', 'reference qprompt'),
	Field('description', 'text', notnull=True),
	format='%(description)s')

db.define_table('q_answer',
	Field('qstatement', 'reference qstatement'),
	Field('participant', 'reference participant'),
	Field('study', 'reference study'),
	Field('ranking', 'integer'),
	Field('box', requires=IS_IN_SET([None, 'Disagree', 'Neutral', 'Agree'])),
	Field('is_balanced', 'boolean', default=False),
	Field('is_done', 'boolean', default=False)
	)

db.define_table('q_feedback',
	Field('q_answer', 'reference q_answer'),
	Field('participant', 'reference participant'),
	Field('box', requires=IS_IN_SET(['Disagree', 'Agree'])),
	Field('description', 'text', notnull=True),
	format='%(description)s')

