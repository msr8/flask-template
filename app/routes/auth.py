from app.models     import *
from app.consts     import *
from app.utils      import login_required, check_email
from app.extensions import db

from flask import Blueprint, redirect, url_for, session, render_template, request
from flask_restful import Resource
from flask_dance.contrib.google import google
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

from bcrypt import hashpw, gensalt, checkpw

auth_bp = Blueprint('auth', __name__)





@auth_bp.route('/login/')
def page_login():
    return redirect(url_for('google.login'))





@auth_bp.route('/google-authorised/')
def page_google_authorised():
    # Get his info
    try: resp:Response = google.get('/oauth2/v1/userinfo')
    except TokenExpiredError: return redirect(url_for('auth.page_login'))
    except: return 'Internal Server Error', 500
    # Check if the responses are valid
    if not resp.ok:                    return f'Failed to fetch user info, please <a href="{url_for("auth.page_login")}">login again</a>', 500
    resp:dict = resp.json()
    if not resp.get('verified_email'): return 'Email not verified', 403
    if not resp.get('email'):          return 'Unable to fetch email', 500
    
    email = resp['email']
    user  = db.session.get(User, email)

    # If we have never seen this user before, add him to the database
    if not user:
        username = email.split('@')[0]
        user = User(email=resp['email'], username=resp['email'].split('@')[0])
        db.session.add(user)
        db.session.add(Usernames(username=username, email=email))
        db.session.commit()
    else:
        username = user.username
    # Save the user's info in the session
    session['logged_in'] = True
    session['email']     = email
    session['username']  = username

    return redirect( session.pop('redirect_to', url_for(POST_LOGIN_REDIRECT)) )





@auth_bp.route('/logout/')
@login_required()
def page_logout():
    session.clear()
    return redirect(url_for(POST_LOGOUT_REDIRECT))
    # return f'Successfully logged out. You may now return to the <a href="{url_for("root.page_index")}">homepage</a>'





class ChangeUsernameAPI(Resource):
    @login_required(json=True)
    def post(self):
        # Extract data
        new_username = request.get_json().get('new_username')
        if not new_username: return {'message': 'New username not provided', 'status': 'error'}, 400

        # Check if the username is a valid email address
        if check_email(new_username): return {'message': 'Username cannot be an email address', 'status': 'error'}, 400
        # Check if the username is already taken
        if Usernames.query.get(new_username): return {'message': 'Username already taken', 'status': 'error'}, 400
        # Check if the username is the same as the current one
        if session['username'] == new_username: return {'message': 'Please provide a username different from the current one', 'status': 'error'}, 400
        
        # Update the username
        user          = db.session.get(User, session['email'])
        old_username  = user.username
        user.username = new_username
        # Update the username in the Usernames table
        Usernames.query.get(old_username).username = new_username
        db.session.commit()
        
        # Update the session
        session['username'] = new_username
        
        return {'status': 'success'}








