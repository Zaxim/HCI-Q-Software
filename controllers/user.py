
# Needed for random.sample
import random

#Require users to login before accessing this page
if not auth.is_logged_in():
    redirect(auth.settings.login_url)


def index():
    """
    Returns a list of all studies associated with the user
    """
    studies = db((db.study.id == db.participant.study) & (
        db.participant.auth_user == auth.user_id)).select(db.study.ALL)
    test_stuff = studies
    sql = db._lastsql
    return locals()


@is_in_study(request.args(0))
def study():
    """
    Returns study details associated with the study ID

    The page allows the user to read the consent form and continue the study
    """
    participant = db.participant((db.participant.study == request.args(0)) & (
        db.participant.auth_user == auth.user_id)) or redirect(URL('index'))
    study = db.study(participant.study)

    return locals()


@is_in_study(request.args(0))
def collect():
    """
    The method checks to see what stage the participant/study is in, &
    redirects correctly
    """
    participant = db.participant((db.participant.study == request.args(0)) & (
        db.participant.auth_user == auth.user_id)) or redirect(URL('index'))
    study = db.study(participant.study)

    if stages.index(participant.study_stage) <= stages.index(study.study_stage):
        if participant.study_stage == "Consenting":
            redirect(URL('consent', args=study.id))
        elif (participant.study_stage == "Soliciting") & (study.study_stage == 'Soliciting'):
            redirect(URL('solicit', args=study.id))
        elif (participant.is_unsuitable):
            if participant.study_stage != 'Presenting':
                participant.update_record(study_stage='Presenting')
            redirect(URL('stages_complete', args=study.id))
        elif (study.study_stage == 'Sorting'):
            if participant.study_stage != 'Sorting':
                participant.update_record(study_stage='Sorting')
            redirect(URL('sort', args=study.id))
        else:
            redirect(URL('stages_complete', args=study.id))
    else:
        redirect(URL('stages_complete', args=study.id))

    sql = db._lastsql
    return locals()


@is_in_study(request.args(0))
def consent():
    """
    Returns the associated study consent form, & asks the user to agree
    """
    participant = db.participant((db.participant.study == request.args(0)) & (
        db.participant.auth_user == auth.user_id)) or redirect(URL('index'))
    study = db.study(participant.study)

    if stages.index(participant.study_stage) > stages.index(study.study_stage):
        redirect(URL('collect', args=study.id))

    if participant.study_stage == "Consenting":
        cform = FORM.confirm(T("I agree to participate"), {
                             T("I DO NOT agree to participate"): URL('default', 'contact')})
        consent_text = study.consent_form
        if cform.accepted:
            participant.update_record(study_stage='Soliciting')
            redirect(URL('collect', args=study.id))
    else:
        redirect(URL('collect', args=study.id))

    return locals()


@is_in_study(request.args(0))
def solicit():
    """
    Solicit & collect Q Sollicitations from participants
    """
    participant = db.participant((db.participant.study == request.args(0)) & (
        db.participant.auth_user == auth.user_id)) or redirect(URL('index'))
    study = db.study(participant.study)

    if stages.index(participant.study_stage) > stages.index(study.study_stage):
        redirect(URL('collect', args=study.id))

    if (participant.study_stage == "Soliciting") & (study.study_stage == 'Soliciting'):
        q_solicitations = db(db.q_solicitation.participant == participant).select(
            orderby=~db.q_solicitation.id)

        # All solicitations collected, redirect to edit solicitations
        unanswered_num = study.num_questions - len(q_solicitations)
        if unanswered_num == 0:
            redirect(URL('edit_solicit', args=study.id))

        q_prompt = db(db.q_prompt.study == study).select()
        q_prompt = q_prompt[unanswered_num - 1]

        db.q_solicitation.participant.default = participant.id
        db.q_solicitation.participant.writable = db.q_solicitation.participant.readable = False
        db.q_solicitation.study.default = study.id
        db.q_solicitation.study.writable = db.q_solicitation.study.readable = False
        db.q_solicitation.q_prompt.default = q_prompt.id
        db.q_solicitation.q_prompt.writable = db.q_solicitation.q_prompt.readable = False

        f = SQLFORM(db.q_solicitation, labels={'description': ''})
        if f.process().accepted:
            session.flash = T("Statement submitted")
            redirect(URL('collect', args=study.id))
        elif f.errors:
            response.flash = T("Form has Errors")
    else:
        redirect(URL('collect', args=study.id))

    sql = db._lastsql
    return locals()


@is_in_study(request.args(0))
def edit_solicit():
    """
    Allows participants to edit Q Solicitations
    """
    participant = db.participant((db.participant.study == request.args(0)) & (
        db.participant.auth_user == auth.user_id)) or redirect(URL('index'))
    study = db.study(participant.study)

    if stages.index(participant.study_stage) > stages.index(study.study_stage):
        redirect(URL('collect', args=study.id))

    if (participant.study_stage == "Soliciting") & (study.study_stage == 'Soliciting'):
        q_solicitations = db(db.q_solicitation.participant == participant).select(
            orderby=~db.q_solicitation.id)
        db.q_solicitation.participant.default = participant.id
        db.q_solicitation.study.default = study.id

        field_list = []
        for i, q in enumerate(q_solicitations):
            prompt = db(db.q_prompt.id == q.q_prompt).select().first()
            # Hack to add q_solicitation ID to Field
            field_list.append(Field(
                'prev:' + str(q.id), 'text', default=q.description, label=prompt.description))

        f = SQLFORM.factory(*field_list)
        for e in f.elements('textarea'):
            e['_rows'] = 4
            e['_class'] = 'text span12'

        if f.process().accepted:
            for nam in f.vars:
                if 'prev' in nam:
                    # Get the id of the record
                    q_solicitation_id = nam.split(':')[1]
                    q_solicitation = db.q_solicitation[q_solicitation_id]
                    if q_solicitation.participant == participant:
                        db(db.q_solicitation.id == q_solicitation_id).update(
                            description=f.vars[nam])
                        # Do we need to add a delete function?
                    else:
                        response.flash = T("Error in updating statements")
            participant.update_record(study_stage='Sorting')
            session.flash = T("Thank you for submitting your statements.")
            redirect(URL('collect', args=study.id))
        elif f.errors:
            response.flash = T("Form has Errors")
    else:
        redirect(URL('collect', args=study.id))

    sql = db._lastsql
    return locals()


@is_in_study(request.args(0))
def sort():
    """
    The method checks if the box sort/rank sort have been completed, &
    redirects appropriately
    """
    participant = db.participant((db.participant.study == request.args(0)) & (
        db.participant.auth_user == auth.user_id)) or redirect(URL('index'))
    study = db.study(participant.study)

    if stages.index(participant.study_stage) > stages.index(study.study_stage):
        redirect(URL('collect', args=study.id))

    if (participant.study_stage == "Sorting") & (study.study_stage == 'Sorting'):
        q_statements = db(db.q_statement.study == study).select()
        answered = db(db.q_answer.participant == participant).select()

        q_list = [a.q_statement for a in answered]

        # Retrieve q_statements that have not been boxed before
        unboxed = db((db.q_statement.study == study) & (
            ~db.q_statement.id.belongs(q_list))).select()
        #PEP8 complains about is vs ==, in this case the DAL defines its own
        #equality op
        unsorted = db((db.q_answer.participant == participant) & (
            db.q_answer.ranking == None)).select()

        if participant.is_sort_complete:
            redirect(URL('final_sort_answer', args=study.id))
        elif len(unboxed) > 0:
            redirect(URL('box_sort', args=study.id))
        elif len(unsorted) > 0:
            redirect(URL('rank_sort', args=study.id))
        else:
            redirect(URL('final_sort', args=study.id))
    else:
        redirect(URL('collect', args=study.id))

    sql = db._lastsql
    return locals()


@is_in_study(request.args(0))
def box_sort():
    """
    Allows the user to box sort Q Statements they have not answered yet
    """
    participant = db.participant((db.participant.study == request.args(0)) & (
        db.participant.auth_user == auth.user_id)) or redirect(URL('index'))
    study = db.study(participant.study)

    if stages.index(participant.study_stage) > stages.index(study.study_stage):
        redirect(URL('collect', args=study.id))

    if (participant.study_stage == "Sorting") & (study.study_stage == 'Sorting'):
        db.q_answer.participant.default = participant.id
        db.q_answer.study.default = study.id

        q_statements = db(db.q_statement.study == study).select()
        answered = db(db.q_answer.participant == participant).select()

        q_list = [a.q_statement for a in answered]

        # Retrieve q_statements that have not been boxed before
        unboxed = db((db.q_statement.study == study) & (
            ~db.q_statement.id.belongs(q_list))).select(orderby='<random>')
        if len(unboxed) > 0:
            q_statement_to_answer = unboxed[0]
            box_form = FORM(INPUT(_type='submit', _name='disagree', _value='Avoid Technology'),
                            INPUT(_type='submit', _name='neutral', _value='Neutral/Not Sure'),
                            INPUT(_type='submit', _name='agree', _value='Use Technology'),
                            INPUT(_name='qid', _type='hidden', _value=q_statement_to_answer.id))
            if box_form.process().accepted:
                # Ensure that Q statement ID is part of the set
                # TODO: WHAT AM I DOING HERE?!?!
                is_valid_answer = db((db.q_statement.study == study) & (
                    ~db.q_statement.id.belongs(q_list))).select()
                if is_valid_answer:
                    if box_form.vars.disagree:
                        db.q_answer.insert(
                            q_statement=box_form.vars.qid, box='Disagree')
                    elif box_form.vars.agree:
                        db.q_answer.insert(
                            q_statement=box_form.vars.qid, box='Agree')
                    elif box_form.vars.neutral:
                        db.q_answer.insert(
                            q_statement=box_form.vars.qid, box='Neutral')
                    redirect(URL('sort', args=study.id))
                else:
                    response.flash = T("Invalid Q Statement ID")
            elif box_form.errors:
                response.flash = T("Form has Errors")
        else:
            redirect(URL('collect', args=study.id))

    sql = db._lastsql
    return locals()


@is_in_study(request.args(0))
def rank_sort():
    participant = db.participant((db.participant.study == request.args(0)) & (
        db.participant.auth_user == auth.user_id)) or redirect(URL('index'))
    study = db.study(participant.study)

    if stages.index(participant.study_stage) > stages.index(study.study_stage):
        redirect(URL('collect', args=study.id))

    if (participant.study_stage == "Sorting") & (study.study_stage == 'Sorting'):

        answered = db(db.q_answer.participant == participant).select()
        q_list = [a.q_statement for a in answered]
        # Retrieve q_statements that have not been boxed before
        unboxed = db((db.q_statement.study == study) & (
            ~db.q_statement.id.belongs(q_list))).select()
        # Ensure that all statements have been boxed
        if len(unboxed) > 0:
            redirect(URL('box_sort', args=request.args(0)))

        unsorted = db((db.q_answer.participant == participant) & (
            db.q_answer.ranking == None)).select()
        sorted_ans = db((db.q_answer.participant == participant) & (
            db.q_answer.ranking != None)).select(orderby=db.q_answer.ranking)

        # HACK: probably more effecient to only iterate over unsorted list once
        unsorted_agree = [a for a in unsorted if a.box == 'Agree']
        unsorted_disagree = [a for a in unsorted if a.box == 'Disagree']
        unsorted_neutral = [a for a in unsorted if a.box == 'Neutral']

        sorted_agree = [a for a in sorted_ans if a.box == 'Agree']
        sorted_disagree = [a for a in sorted_ans if a.box == 'Disagree']

        unbalanced = [a for a in unsorted if a.is_balanced is False]
        if len(unbalanced) > 0:
            disagree_difference = study.box_size - len(unsorted_disagree)
            agree_difference = study.box_size - len(unsorted_agree)

            # Balance disagree with neutrals
            if disagree_difference > 0:
                if len(unsorted_neutral) < disagree_difference:
                    participant.update_record(is_unsuitable=True)
                    redirect(URL('collect'))
                else:
                    samp = random.sample(unsorted_neutral, disagree_difference)
                    # HACK: Perform disjoint set of two lists & convert back to
                    # list
                    unsorted_neutral = list(set(unsorted_neutral) - set(samp))
                    for a in samp:
                        a.update_record(box='Disagree')

            # Balance agrees by moving neutrals to agree
            if agree_difference > 0:
                if len(unsorted_neutral) < agree_difference:
                    participant.update_record(is_unsuitable=True)
                    redirect(URL('collect'))
                else:
                    samp = random.sample(unsorted_neutral, agree_difference)
                    # HACK: Perform disjoint set of two lists & convert back to
                    # list
                    unsorted_neutral = list(set(unsorted_neutral) - set(samp))
                    for a in samp:
                        a.update_record(box='Agree')

            db(db.q_answer.participant == participant).update(is_balanced=True)
            redirect(URL('sort', args=study.id))

        elif (len(unsorted_agree) > 0) or (len(unsorted_disagree) > 0):
            if len(unsorted_agree) > 0:
                is_agree = True
                instructions= T("Drag the bottom statement UP if you think that technology would be MORE useful, desirable, or beneficial.")
                pile_text = T("\"I think technology would be useful\"")
                ans_to_sort = unsorted_agree[0]
                sorted_list = sorted_agree
            elif len(unsorted_disagree) > 0:
                is_agree = False
                instructions = T("Drag the top statement DOWN if you think that technology would be MORE useless, undesirable, or problematic.")
                pile_text = T("\"I think technology should be avoided\"")
                ans_to_sort = unsorted_disagree[0]
                sorted_list = sorted_disagree

            if len(sorted_list) < 1:
                ans_to_sort.update_record(ranking=0)
                redirect(URL('collect', args=study.id))

            sort_list = pick_order_list(sorted_list)

            if not is_agree:
                start_val = len(sort_list)
            else:
                start_val = 0

            sort_form = FORM(
                INPUT(_id='rank', _name='rank', value=start_val,
                      requires=IS_IN_SET(range(0, len(sort_list) + 1)),
                      _type='hidden'), INPUT(_type='submit', _value='Submit'))

            if sort_form.process().accepted:
                rank = int(sort_form.vars.rank)
                if rank == len(sort_list):
                    ans_to_sort.update_record(
                        ranking=sorted_list[-1].ranking + 1)
                else:
                    # Get q_answer that needs to be incremented
                    start_pivot = sort_list[rank]
                    start_index = sorted_list.index(start_pivot)
                    ans_to_sort.update_record(ranking=start_pivot.ranking)
                    for a in sorted_list[start_index:]:
                        a.update_record(ranking=a.ranking + 1)
                redirect(URL('collect', args=study.id))
            elif sort_form.errors:
                response.flash = 'error'
        # Check if all answers have been ranked and then rank neutrals and fix
        # disagree rank
        elif (not unsorted_agree) and (not unsorted_disagree):
            full_answer_list = sorted_disagree + \
                unsorted_neutral + sorted_agree
            for count, a in enumerate(full_answer_list):
                a.update_record(ranking=count)
            redirect(URL('final_sort', args=study.id))
        else:
            redirect(URL('collect', args=study.id))

    return locals()


@is_in_study(request.args(0))
def final_sort():
    """
    Allows the user to perform a final sort of all the answers
    """
    participant = db.participant((db.participant.study == request.args(0)) & (
        db.participant.auth_user == auth.user_id)) or redirect(URL('index'))
    study = db.study(participant.study)

    if stages.index(participant.study_stage) > stages.index(study.study_stage):
        redirect(URL('collect', args=study.id))

    if participant.is_sort_complete:
        redirect(URL('collect', args=study.id))

    if (participant.study_stage == "Sorting") & (study.study_stage == 'Sorting'):
        answered = db(db.q_answer.participant == participant).select()
        q_list = [a.q_statement for a in answered]
        # Retrieve q_statements that have not been boxed before
        unboxed = db((db.q_statement.study == study) & (
            ~db.q_statement.id.belongs(q_list))).select()
        # Ensure that all statements have been boxed
        if len(unboxed) > 0:
            redirect(URL('box_sort', args=request.args(0)))

        # Ensure that all statements have been sorted
        unsorted = db((db.q_answer.participant == participant) & (
            db.q_answer.ranking == None)).select()
        if len(unsorted) > 0:
            redirect(URL('rank_sort', args=request.args(0)))

        sorted_ans = db((db.q_answer.participant == participant) & (
            db.q_answer.ranking is not None)).select(orderby=db.q_answer.ranking)
        sorted_ans_ids = [a.id for a in sorted_ans]
        sort_form = FORM(INPUT(_id='rank_list', _name='rank_list', _type='hidden'), INPUT(
            _type='submit', _value=T("I'm Done!")))
        if sort_form.process().accepted:
            new_order_list = sort_form.vars.rank_list.replace(
                'ans[]=', '').split('&')
            new_order_list = map(int, new_order_list)

            for count, i in enumerate(reversed(new_order_list)):
                if i in sorted_ans_ids:
                    db(db.q_answer.id == i).update(ranking=count)

            participant.update_record(is_sort_complete=True)
            redirect(URL('final_sort_answer', args=study.id))
        elif sort_form.errors:
            response.flash = 'error'
    else:
        redirect(URL('collect', args=study.id))

    return locals()


@is_in_study(request.args(0))
def final_sort_answer():
    """
    Allows the user to submit qualitative feedback about answers
    """
    participant = db.participant((db.participant.study == request.args(0)) & (
        db.participant.auth_user == auth.user_id)) or redirect(URL('index'))
    study = db.study(participant.study)

    if stages.index(participant.study_stage) > stages.index(study.study_stage):
        redirect(URL('collect', args=study.id))

    if (participant.study_stage == "Sorting") & (study.study_stage == 'Sorting'):
        sorted_ans = db((db.q_answer.participant == participant) & (
            db.q_answer.ranking is not None)).select(orderby=~db.q_answer.ranking)
        q_feedback_neg = db((db.q_feedback.participant == participant) & (
            db.q_feedback.box == 'Disagree')).select()
        q_feedback_pos = db((db.q_feedback.participant == participant) & (
            db.q_feedback.box == 'Agree')).select()

        if (len(q_feedback_pos) < study.feedback_questions) or (len(q_feedback_neg) < study.feedback_questions):
            if len(q_feedback_pos) < study.feedback_questions:
                prompt = T("How do you imagine technology being used")
                q_answer = sorted_ans[len(q_feedback_pos)]
                q_statement_id = q_answer.q_statement
                db.q_feedback.box.default = 'Agree'

            elif len(q_feedback_neg) < study.feedback_questions:
                prompt = T("Why would you avoid using technology")
                q_answer = sorted_ans[-len(q_feedback_neg) - 1]
                q_statement_id = q_answer.q_statement
                db.q_feedback.box.default = 'Disagree'

            db.q_feedback.box.writable = db.q_feedback.box.readable = False
            db.q_feedback.participant.default = participant.id
            db.q_feedback.participant.writable = db.q_feedback.participant.readable = False
            db.q_feedback.q_answer.default = q_answer.id
            db.q_feedback.q_answer.writable = db.q_feedback.q_answer.readable = False
            q_statement = db(
                db.q_statement.id == q_statement_id).select().first()

            f = SQLFORM(db.q_feedback, labels={'description': ''})
            if f.process().accepted:
                session.flash = T('Feedback submitted')
                redirect(URL('sort', args=study.id))
            elif f.errors:
                response.flash = T('Form has Errors')
        else:
            participant.update_record(study_stage='Presenting')
            redirect(URL('collect', args=study.id))

    else:
        redirect(URL('collect', args=study.id))

    return locals()


@is_in_study(request.args(0))
def stages_complete():
    study = db.study[request.args(0)] or redirect(URL('index'))

    completed_stage_text = study.end_study_msg
    return locals()
