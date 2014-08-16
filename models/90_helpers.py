
def is_in_study(study_id):
    """
    Decorator that prevents access to function if not a member of a specified
    study ID
    """
    def real_decorator(f):
        def wrapper(*args, **kwargs):
            studies = db((db.study.id == db.participant.study) and (
                db.participant.auth_user == auth.user_id) and (db.study.id == study_id)).select(db.study.id)
            if not studies:
                redirect(URL('user', 'index'))
            else:
                return f(*args, **kwargs)
        return wrapper
    return real_decorator


def pick_order_list(sorted_ans):
    if len(sorted_ans) == 0:
        return []
    elif (len(sorted_ans) == 1) or (len(sorted_ans) == 2):
        return sorted_ans[:]
    else:
        return [sorted_ans[0], sorted_ans[len(sorted_ans) // 2], sorted_ans[-1]]
