from collections import namedtuple
from flask import Blueprint, render_template, abort, request, flash, redirect, url_for, current_app, session
from flask_login import login_user, logout_user, login_required, current_user, UserMixin

# # OAuth providers
# from web.model.oauth.base import OAuthSignIn
#
# shared = get_shared(current_app)
#
# dal = shared.get('dal')
# m_cache = shared.get('mcache')
# dbi = DBInterface(dal, cache=m_cache)
#
# authentication = Blueprint('auth', __name__)
# _authenticated_user = shared.get('users')
#
UserInfo = namedtuple('UserInfo', ['name', 'email', 'id'])


class User(UserMixin):
    """
    User object after login
    """

    def __init__(self, email, info=None):
        self.email = email
        if not info:
            info = {}
        self.fname = info.get('fname')
        self.lname = info.get('lname')

    def _set_info(self, info):
        self.info = info.get('meta', {}) if info else {}

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def get_fname(self):
        return self.fname

    def get_lname(self):
        return self.lname

    def get_name(self, formatted=False):
        """Return first and last name of user"""
        if formatted:
            return "{0} {1}".format(self.get_fname().capitalize(),
                                    self.get_lname().capitalize())
        return self.get_fname(), self.get_lname()

    def get_email(self):
        """Get Email of the user"""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __repr__(self):
        return "%r" % self.get_id()

    def __str__(self):
        return '%s,%s,%s' % (self.email, self.get_fname(), self.get_lname())


@authentication.record
def init(setup_state):
    azure_client_id = '4cd8bc66-beb8-47a0-85a4-962044fcdceb'
    azure_pass = 'NyaK1D8nwi7pxnC8Rcb1ouj'

    github_client_id = 'aa148ba2f4486a716b24'
    github_secret = '04cc12cdbd43c97f121f1835fd944b19ae2e4c36'


@authentication.route('/login', methods=['GET', 'POST'])
def login():
    header = 'User Login'
    if request.method == 'POST':
        username = request.form.get('uname')
        passwd = request.form.get('pword')
        # result = dbi.create_new_user(dict(fname='User', lname='Name', email=username, authenticator='lblrsm'))
        # flash("Result of insert operation: {0}".format(result))
        user_info = dbi.get_user_info(username)
        # pdb.set_trace()
        if user_info is None:
            flash("Error:Sorry, No Such user exist!")
            return redirect(url_for('auth.login'))

        if not validate(username, passwd, user_info, current_app.config['DEBUG']):
            flash("Error:Invalid Username/Password")
            return redirect(url_for('auth.login'))

        user = User(username, info={'lname': user_info.get('lname'), 'fname': user_info.get('fname')})
        login_user(user)

        if user_info.get('deleted', False):  # User existed but deleted the profile,
            flash('Info:User profile was deleted, please re-create the profile')
            return redirect(url_for('profile.view'))

        flash("Info:Login Successful!")
        return redirect(request.args.get('next') or url_for('profile.view'))

    if current_user.is_authenticated:
        flash("Info:You are already logged in as {0}".format(current_user.get_id()))
        return redirect(url_for('profile.view'))
    return render_template('authenticate/login.html', content_header=header)


@authentication.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        pass

    return render_template('authenticate/signup.html')


@authentication.route('/logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    # _user = user_session_management(user.get_id(), None, action='del')
    flash('Info:Logged out successfully')
    # print(_authenticated_user.keys())
    logout_user()
    return redirect(url_for('home'))


@authentication.route('/authorize/<string:provider>')
def oauth_authorize(provider):
    # TODO: Check if provider is configured!
    if not current_user.is_anonymous:
        return redirect(url_for('.login'))

    oauth = OAuthSignIn.get_provider(provider_name=provider)
    return oauth.authorize()


@authentication.route('/callback/<string:provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('.login'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, name, email, full_info = oauth.callback()

    if email is None:
        flash('Error:Authentication failed/User declined the request/email address is not available')
        flash('Warn:Try to login with provider which provides email address!')
        return redirect(url_for('.login'))

    # pdb.set_trace()
    user_info = dbi.get_from_cache_or_db(email) or {}
    # pdb.set_trace()
    session['%s_authenticator' % email] = provider
    user = User(email, info={'fname': user_info.get('fname'), 'lname': user_info.get('lname')})

    old_authenticator = user_info.get('authenticator')

    if user_info and old_authenticator and old_authenticator != provider:
        flash('Error:User "%s" already exist, originally signed in with %s' % (email, user_info.get('authenticator')))
        return redirect(url_for('.login'))

    if not user_info:  # this is a new user update the count
        dbi.update_stats(user_cnt=1)

    login_user(user, remember=False)

    if not user_info:
        fname, lname = '', ''
        if name and isinstance(name, (list, tuple)):
            fname, lname = name

        url = url_for('profile.update') + "?f=%s&l=%s" % (fname, lname)   # Redirect to create page
    else:
        url = url_for('profile.view')

    session[email] = full_info
    return redirect(request.args.get('next') or url)

