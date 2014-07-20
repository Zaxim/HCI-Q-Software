
#Uncomment in production
# if not auth.has_membership('admin'):
#	redirect(auth.settings.login_url)


def index():
    redirect(URL('studies'))


def studies():
    """Returns a list of all studies"""
    studies = db(db.study).select(orderby=db.study.name)
    return locals()


def study():
    """
    Returns the study associated with the study ID or redirects back to the
    list of studies.

    The page allows you to modify study details, create new participants for
    studies, or invite new users to become participants.
    """
    study_id = db.study(request.args(0)) or redirect(URL('studies'))

    # Modify study name or description form
    db.study.id.readable = False
    db.study.id.writeable = False
    study_form = SQLFORM(db.study, study_id)
    if study_form.process().accepted:
        response.flash = T("Study Updated")
    elif study_form.errors:
        response.flash = T("Form has Errors")

    # Modify Q Statement prompts
    q_prompts = db(db.q_prompt.study == study_id).select(
        orderby=~db.q_prompt.id)
    db.q_prompt.study.default = study_id
    study = db(db.study.id == study_id).select().first()
    unanswered_num = study.num_questions - len(q_prompts)
    field_list = []
    for i, q in enumerate(q_prompts):
        # Hack to add q_prompt ID to Field
        field_list.append(
            Field('prev:' + str(q.id), 'text', default=q.description,
                  label=''))
    f = SQLFORM.factory(*field_list)
    if f.process().accepted:
        for nam in f.vars:
            if 'prev' in nam:
                q_prompt_id = nam.split(':')[1]  # Get the id of the record
                q_prompt = db.q_prompt[q_prompt_id]
                db(db.q_prompt.id == q_prompt_id).update(
                    description=f.vars[nam])
                session.flash = T("Study Updated")
        redirect(URL('study', args=study_id.id), client_side=True)
    elif f.errors:
        response.flash = T("Form has Errors")

    # List participants associated with a study
    participants = db(db.participant.study == study_id.id).select()
    p_list = []
    for p in participants:
        p_list.append(p.auth_user)

    # Add existing users to the study form
    # Returns a list of users not associated with the study
    users = db(~db.auth_user.id.belongs(p_list)).select()
    # Create multiple select form by generating a list of user IDs and the
    # names of the users as labels
    user_list_id = []
    user_list_label = []
    for user in users:
        user_list_id.append(user.id)
        user_list_label.append('{0} {1}'.format(user.first_name, user.last_name))
    add_user_form = SQLFORM.factory(Field('Users', requires=IS_IN_SET(
        user_list_id, labels=user_list_label, multiple=True)), table_name="no_table_add_user")
    if add_user_form.process().accepted:
        for user_id in add_user_form.vars.Users:
            db.participant.insert(participant_alias=get_random_alias(
            ), auth_user=user_id, study=study_id, study_stage='Consenting')
        session.flash = T("Study Updated")
        redirect(URL('study', args=study_id.id), client_side=True)
    elif add_user_form.errors:
        response.flash = T("Form has Errors")

    # Invite or add users to study via email form
    invalid_emails = []
    new_users = []
    invite_user_form = SQLFORM.factory(
        Field('Emails'), table_name='no_table_invite_user')
    auth_stuff = []
    if invite_user_form.process().accepted:
        email_list = invite_user_form.vars.Emails.split(',')
        for e in email_list:
            # Returns a tuple with the first value being email, the second
            # being None if it's a valid email
            em, valid = IS_EMAIL()(e)
            if valid is not None:
                invalid_emails.append(em)
            else:
                user_id = db(db.auth_user.email == em).select().first()
                auth_stuff = user_id
                if not user_id:
                    auth.random_password()
                    password = db.auth_user.password.validate(
                        auth.random_password())[0]
                    user_id = auth.get_or_create_user(
                        {'email': em, 'password': password})
                    new_users.append(user_id)
                if user_id not in p_list:
                    db.participant.insert(participant_alias=get_random_alias(
                    ), auth_user=user_id, study=study_id, study_stage='Consenting')
        session.flash = T(
            "Study Updated\nThe following emails were not added\n" + str(invalid_emails))
        redirect(URL('study', args=study_id.id), client_side=True)
    elif invite_user_form.errors:
        response.flash = T("Form has Errors")

    return locals()


def add_study():
    """A page to create new study"""
    study_form = SQLFORM(db.study)
    study_form.add_button("Cancel", URL('admin', 'studies'))
    if study_form.process().accepted:
        db.q_prompt.study.default = study_form.vars.id
        db.auth_group.insert(role=study_form.vars.name)
        for i in range(study_form.vars.num_questions):
            db.q_prompt.insert(description='')
        redirect(URL('study', args=study_form.vars.id))
    elif study_form.errors:
        response.flash = T("Form has Errors")
    return locals()


def participant():
    """
    Returns the participant associated with the participant ID or redirects
    back the list of studies
    """
    participant = db.participant(request.args(0)) or redirect(URL('studies'))

    db.participant.id.readable = False
    db.participant.id.writeable = False
    participant_form = SQLFORM(db.participant, participant, deletable=True)
    participant_form.add_button(
        "Cancel", URL('admin', 'study', args=participant.study))
    if participant_form.process().accepted:
        response.flash = T("Form Accepted")
    elif participant_form.errors:
        response.flash = T("Form has Errors")
    return locals()


def modify_q_solicitations():
    study = db.study(request.args(0)) or redirect(URL('studies'))
    query = (db.q_solicitation.study == study)

    def add_qstatements(ids):
        for id in ids:
            q_solicitation = db(db.q_solicitation.id == id).select().first()
            db.q_statement.insert(study=q_solicitation.study, description=q_solicitation.description)
        session.flash = T("Solicitations copied to Statements")
    
    grid = SQLFORM.grid(query, args=[study.id], selectable=[('Copy to Q-Statements', lambda ids: add_qstatements(ids))])
    return locals()


def modify_q_statements():
    study = db.study(request.args(0)) or redirect(URL('studies'))
    query = (db.q_statement.study == study)

    def del_qstatements(ids):
        for id in ids:
            db(db.q_statement.id ==id).delete()
        session.flash = T("Q Statements deleted")
    
    grid = SQLFORM.grid(query, args=[study.id], selectable=[('Delete', lambda ids: del_qstatements(ids))])
    return locals()