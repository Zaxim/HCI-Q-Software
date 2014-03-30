db.define_table('participant_alias',
	Field('alias_name', notnull=True),
	Field('gender', requires= IS_IN_SET(['Female', 'Male', 'Neutral'])),
	format='%(alias_name)s'
	)