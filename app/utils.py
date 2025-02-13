from app.consts import *
from flask import request, session, redirect, url_for, flash, get_flashed_messages
from functools import wraps



# Wrapper for login required but it also takes in a boolean indicating wether to return the data as json or not
def login_required(json=False):
    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if not session.get('logged_in'):
                flash('You must be logged in to access this resource', 'error')
                # redirect_to = f.__module__.split('.')[-1] + '.' + f.__name__
                redirect_to = request.url
                session['redirect_to'] = redirect_to

                if not json: return redirect(url_for(LOGIN_FAIL_REDIRECT))
                return {'message': 'You are not logged in', 'status': 'error'}, 401
            
            return f(*args, **kwargs)
        
        return inner
    return wrapper


