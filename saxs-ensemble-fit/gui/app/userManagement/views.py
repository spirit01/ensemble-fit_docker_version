from flask import render_template, redirect, request, url_for
from .. import db
from app.userManagement import userMngmt
from app.forms import RegistrationForm
from app.bussinesLogic import DirectoryAndFileWriter, DirectoryAndFileReader
from app.models import User
from app.email import send_email


@userMngmt.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    r_form = RegistrationForm(request.form)
    user_details = get_user_details()

    if r_form.validate_on_submit():
        # user_details = DirectoryAndFileReader.get_user_details()
        user = User(username=r_form.username.data, email=r_form.email.data, eppn=user_details[0], role_id=2)
        db.session.add(user)
        db.session.commit()
        DirectoryAndFileWriter.create_user_directory(get_user_id(user_details[0]))
        # send_email(user.email, 'Confirm Your Account', 'mail/confirm', user=user, token=token)
        return redirect(url_for('userManagement.unconfirmed'))

    return render_template('sign_up.html', r_form=r_form, username=user_details[1], email=user_details[2])


@userMngmt.route('/unconfirmed')
def unconfirmed():
    user_details = get_user_details()
    if is_user_registered(user_details[0]) and is_user_confirmed(user_details[0]):
        return redirect('/home')

    return render_template('unconfirmed.html', username=get_user_username(user_details[0]))


def get_user_details():
    result = [request.environ["HTTP_EPPN"], request.environ["HTTP_CN"].decode("unicode_escape"), request.environ["HTTP_MAIL"].decode("unicode_escape")]
    return result


def is_user_registered(eppn):
    user = User.query.filter_by(eppn=eppn).first()
    return user is not None


def is_user_confirmed(eppn):
    user = User.query.filter_by(eppn=eppn).first()
    return user is not None and user.confirmed


def get_user_id(eppn):
    return User.query.filter_by(eppn=eppn).first().id


def get_user_username(eppn):
    return User.query.filter_by(eppn=eppn).first().username



