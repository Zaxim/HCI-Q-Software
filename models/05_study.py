# Information associated with a study

db.define_table('study',
                Field('name', notnull=True),
                Field('description', 'text', widget=ckeditor.widget),
                Field('consent_form', 'text', widget=ckeditor.widget),
                Field('num_questions', 'integer',
                      requires=IS_INT_IN_RANGE(0, 501)),
                Field('box_size', 'integer', requires=IS_INT_IN_RANGE(0, 501)),
                Field('feedback_questions', 'integer',
                      requires=IS_INT_IN_RANGE(0, 501)),
                Field('end_study_msg', 'text', widget=ckeditor.widget),
                Field('study_stage', requires=IS_IN_SET(stages),
                      default='Initial'), format='%(name)s'
                )

db.define_table('participant',
                Field('auth_user', 'reference auth_user'),
                Field('study', 'reference study'),
                Field('study_stage', requires=IS_IN_SET(stages)),
                Field('is_unsuitable', 'boolean', default=False),
                Field('is_sort_complete', 'boolean', default=False),
                format='Participant %(id)s'
                )

db.define_table('q_prompt',
                Field('study', 'reference study'),
                Field('description', 'text', notnull=True),
                format='%(description)s'
                )

db.define_table('q_solicitation',
                Field('participant', 'reference participant'),
                Field('study', 'reference study'),
                Field('q_prompt', 'reference q_prompt'),
                Field('description', 'text', notnull=True, requires=IS_LENGTH(1000)),
                format='%(description)s'
                )

db.define_table('q_statement',
                Field('study', 'reference study'),
                Field('description', 'text', notnull=True),
                format='%(description)s'
                )

db.define_table('q_answer',
                Field('q_statement', 'reference q_statement'),
                Field('participant', 'reference participant'),
                Field('study', 'reference study'),
                Field('ranking', 'integer'),
                Field('box', requires=IS_IN_SET(
                    [None, 'Disagree', 'Neutral', 'Agree'])),
                Field('is_balanced', 'boolean', default=False),
                Field('is_done', 'boolean', default=False)
                )

db.define_table('q_feedback',
                Field('q_answer', 'reference q_answer'),
                Field('participant', 'reference participant'),
                Field('box', requires=IS_IN_SET(['Disagree', 'Agree'])),
                Field('description', 'text', notnull=True),
                format='%(description)s'
                )
