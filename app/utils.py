from flask import session, render_template
from functools import wraps


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not any(item in session for item in ['username']):
            print('login is required')
            return render_template('main.html')
        return func(*args, **kwargs)

    return inner

