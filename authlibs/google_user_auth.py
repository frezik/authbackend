# vim:tabstop=2:shiftwidth=2:expandtab
from flask import Blueprint, redirect, url_for, session, flash, g
from flask_dance.contrib.google import make_google_blueprint, google

from flask_dance.consumer.storage.sqla import SQLAlchemyStorage, OAuthConsumerMixin

from flask_login import current_user, login_user, logout_user
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc import NoResultFound
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError
from .db_models import db, Member, OAuth, AnonymousMember, Role, UserRoles, AccessByMember
from flask_login import LoginManager
from flask_user import UserManager
from .accesslib import quickSubscriptionCheck

# Set-up Python module logging
import logging
from authlibs.init import GLOBAL_LOGGER_LEVEL
logger = logging.getLogger(__name__)
logger.setLevel(GLOBAL_LOGGER_LEVEL)
import os
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE']='Yes'
os.environ['OAUTHLIB_INSECURE_TRANSPORT']='Yes'

""" 
TODO FIX BUG

You can (and probably should) set OAUTHLIB_RELAX_TOKEN_SCOPE when running in production.
"""
def our_login():
    # Do something like this but not this
    logger.error("OUR LOGIN (Unauthenticated?)")
    return redirect(url_for('login'))


def authinit(app):
    userauth = Blueprint('userauth', __name__)

    google_blueprint = make_google_blueprint(
        client_id=app.config['globalConfig'].Config.get("OAuth","GOOGLE_CLIENT_ID"),
        client_secret=app.config['globalConfig'].Config.get("OAuth","GOOGLE_CLIENT_SECRET"),
        scope=[#"https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email"
        ],
	# TEST - DOESNT WORK authorized_url="https://staging.makeitlabs.com/authit/google_login/google/authorized",
        offline=True
        )

    google_blueprint.backend = SQLAlchemyStorage(OAuth, db.session,
                                                 user=current_user,
                                                 user_required=True)

    user_manager = UserManager(app, db, Member)
    user_manager.USER_ENABLE_AUTH0 = True
    user_manager.unauthenticated_view = our_login
    login_manager=LoginManager()
    login_manager.login_view="google.login"
    login_manager.init_app(app)
    login_manager.anonymous_user=AnonymousMember

    @login_manager.user_loader
    def load_user(user_id):
        if not user_id.lower().endswith("@makeitlabs.com"): 
          logger.error("User {0} invalid for login".format(user_id))
          return None
        mid = user_id.split("@")[0]
        mr =  Member.query.filter(Member.member == mid).one_or_none()
        if not mr:
          logger.error("User {0} Found no member record".format(user_id))
        logger.debug("User {0} loaded".format(user_id))
        return mr
        #return Member.get(user_id)

    @userauth.route("/google_login")
    def google_login():
        if not google.authorized:
            logger.debug("Not google authorized")
            session['next_url'] = request.args.get('next')
            return redirect(url_for("google.login"))
        resp = google.get(SCOPE)
        assert resp.ok, resp.text
        return resp.text

    @oauth_authorized.connect_via(google_blueprint)
    def google_logged_in(blueprint, token):
        resp = google.get("/oauth2/v2/userinfo")
        #print "RESP",dir(resp)
        #print "HEADERS",resp.headers
        #print "REASON",resp.reason
        #print "TEXT",resp.text
        #print "NEXT",resp.next
        #print "LINKS",resp.links
        #print "URL",resp.url
        #print "IS_REDIRECT",resp.is_redirect
        if resp.ok:
            account_info_json = resp.json()
            email = account_info_json['email']
            member=email.split("@")[0]
            logger.debug("Google auth RESP for {0} {1}".format(email,member))
            if not email.endswith("@makeitlabs.com"):
                flash("Not a MakeIt Labs account - You must log in with your @makeitlabs.com email address",'warning')
                logger.error("Not a MakeIt Labs account "+str(email))
                return redirect(url_for('empty'))
            #query = Member.query.filter_by(Member.member.ilike(member))
            #if not query:
            query = Member.query.filter(Member.email.ilike(email))

            try:
                user = query.all()
                if len(user) > 1:
                        flash("Error - Multiple accounts with same email - please seek assistance",'warning')
                        logger.error("%s has multiple account (GUI Login)" % email)
                        return redirect(url_for('empty'))

                if len(user) ==0:
                        flash("Error - No account found - please seek assistance",'warning')
                        logger.error("No account matching %s for GUI login" % email)
                        return redirect(url_for('empty'))

                user = user[0]
                sub = quickSubscriptionCheck(member_id=user.id)
                #print "UserID %s SUB IS %s" % (user.id,sub)
                if sub == "Active" or sub == "Grace Period":
                  if (UserRoles.query.filter(UserRoles.member_id == user.id).count() >= 1):
                    login_user(user, remember=True)
                    flash("Welcome!")
                    return redirect(url_for('index'))
                  logintype= app.config['globalConfig'].Config.get('General','Logins')
                  if logintype == "resource":
                    if  (AccessByMember.query.filter(AccessByMember.member_id == user.id,AccessByMember.level >= AccessByMember.LEVEL_TRAINER).count() ==0):
                      flash("Only resource managers may log in")
                      logger.error("Only resource managers may log in "+str(email))
                    else:
                      login_user(user, remember=True)
                  else:
                    flash("Welcome!")
                    login_user(user, remember=True)
                    return redirect(url_for('index'))
                else:
                  flash("Login Denied - "+str(sub),'danger')
                  logger.error("Login Denied - "+str(email)+" is "+str(sub))
                return redirect(url_for('empty'))
            except NoResultFound:
                flash("Email adddress "+str(email)+" not found in member database","warning")
                logger.error("Email adddress "+str(email)+" not found in member database")
                return redirect(url_for('empty'))
        else:
          logger.error("Google auth RESP is NOT okay")


    @userauth.route('/google_logout')
    def google_logout():
        """Revokes token and empties session."""
        if google.authorized:
            try:
                google.get(
                    'https://accounts.google.com/o/oauth2/revoke',
                    params={
                        'token':
                        google.token['access_token']},
                )
            except InvalidClientIdError:  # token expiration
                del google.token
                flash("OAuth error: Invalid Client ID",'danger')
                redirect(url_for('main.index'))
        session.clear()
        logout_user()
        return redirect(url_for('main.index'))

    app.register_blueprint(google_blueprint, url_prefix="/google_login")
