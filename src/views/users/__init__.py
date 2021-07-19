from flask import Blueprint, render_template, \
    request, flash, abort, current_app
from flask.helpers import url_for
from werkzeug.utils import redirect
from src.models import User
from src import db
from src.forms import SignupForm, LoginForm
import datetime
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import phonenumbers
from src.utils import adminsonly, validate_profile_image
import smtplib
# from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer


def confirm_token(token, exptime=84600):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    id = serializer.loads(token, salt=current_app.secret_key, max_age=exptime)
    user = User.query.filter_by(id=id).first()
    return user.email


def set_upmsg(recepient, sender: str, url):
    msg = MIMEMultipart('alternative')

    html_cont = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Document</title>
        </head>
        <body>
            <div>
                <p>To reset the password, visit the following \
                    link <a href="{url}">Reset password.</a> \
                        If this request did not come from your end, \
                            ignore this \
                            message and no changes will happen to your \
                                previous password</p>
            </div>
        </body>
    """

    msg['subject'] = "Passord reset form"
    msg['from'] = sender
    msg['to'] = recepient

    cont = MIMEText(html_cont, 'html')
    msg.attach(cont)

    # add the confs as environment variables
    client = smtplib.SMTP(
        current_app.config[
            'MAIL_SERVER'], current_app.config['MAIL_PORT'])
    client.starttls()
    client.login(
        current_app.config[
            'MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
    client.send_message(msg)
    client.quit()


def send_mail_reset_email(user):
    token = user.get_reset_password_token()
    redirect_url = url_for(
        'src.views.users.change_password', _external=True, token=token)
    set_upmsg(recepient=user.email, sender=current_app.config[
        'MAIL_USERNAME'], url=redirect_url)


def send_confirmation_email(recepient, sender: str, url):
    msg = MIMEMultipart('alternative')

    html_cont = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Confirmation for your offer yangu account</title>
        </head>
        <body>
            <div>
                <p>Thank you for creating an account with offer yangu you can \
                    <a href="{url}">click this link to confirm your \
                        account</a></p>
            </div>
        </body>
    """

    msg['subject'] = "Confirmation to your offer yangu account"
    msg['from'] = sender
    msg['to'] = recepient

    cont = MIMEText(html_cont, 'html')
    msg.attach(cont)

    # add the confs as environment variables
    client = smtplib.SMTP(current_app.config[
        'MAIL_SERVER'], current_app.config['MAIL_PORT'])
    client.starttls()
    client.login(current_app.config[
        'MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
    client.send_message(msg)
    client.quit()


user = Blueprint(
    __name__, 'user', template_folder='../templates/',
    static_folder='../static/')


@user.route('/delete/user/<int:id>', methods=['POST'])
@login_required
@adminsonly()
def deleteuser(id):
    client = User.query.filter_by(id=id).first_or_404()
    db.session.delete(client)
    db.session.commit()
    flash('user successfully deleted', 'danger')
    return redirect(url_for('src.views.products.account'))


@user.route("/register", methods=["POST"])
def register():
    signup_form = SignupForm()
    if current_user.is_authenticated:
        return redirect(url_for("src.views.products.home"))
    if request.method == "POST":
        if signup_form.validate_on_submit():
            name = signup_form.username.data
            email = signup_form.email.data
            password = signup_form.password.data
            form_phone = signup_form.phone.data
            phone = phonenumbers.parse(form_phone, "KE")
            inter_national_f = phonenumbers.format_number(
                phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            phone = inter_national_f
            user_email = User.query.filter_by(email=email).first()
            user_phone = User.query.filter_by(phone=phone).first()
            if user_email:
                flash(
                    "You already have an accout please login to your account or \
                        the email entered is already taken",
                    "primary",
                )
                return redirect(url_for("src.views.products.home"))
            if user_phone:
                flash(
                    "A user with that phone already exists", "primary"
                )
                return redirect(url_for("src.views.products.home"))
            user = User(
                name=name,
                email=email,
                password=generate_password_hash(password, method="sha256"),
                phone=phone
            )
            db.session.add(user)
            db.session.commit()
            flash(
                f"Account for {signup_form.username.data} created \
                    successfully", "success")
            # token = user.get_reset_password_token()
            # confirm_url = url_for(
            #     'src.views.users.confirm_email', token=token, _external=True)
            # send_confirmation_email(
            #     user.email, current_app.config['MAIL_USERNAME'],
            #     url=confirm_url)
            # flash('A confirmation email has been sent via email.', 'success')
            return redirect(url_for("src.views.products.home"))
        if signup_form.errors != {}:
            for err_msg in signup_form.errors.values():
                flash(err_msg[0], "danger")
    return redirect(url_for("src.views.products.home"))


@user.route("/login", methods=["POST"])
def login():
    log_form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("src.views.products.home"))
    if request.method == "POST":
        if log_form.validate_on_submit():
            email = log_form.email.data
            password = log_form.password.data
            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    nxt = request.args.get("next")
                    login_user(user, remember=request.form.get('remember'))
                    flash("You have logged in successfully", "success")
                    if nxt:
                        return redirect(nxt)
                    return redirect(url_for("src.views.products.home"))
                else:
                    flash(
                        "wrong password ensure that you enter the correct \
                            credentials fields are case sensitive",
                        "danger",
                    )
                    return redirect(url_for("src.views.products.home"))
            flash(
                "the user associated with this email does not exist please create \
                    an accout before login",
                "danger",
            )
            return redirect(url_for("src.views.products.home"))
        if log_form.errors != {}:
            for err_msg in log_form.errors.values():
                flash(err_msg[0], "danger")
    return redirect(url_for("src.views.products.home"))


@user.route("/reset/password", methods=["POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for("src.views.products.home"))
    data = request.form.get("request")
    user = User.query.filter_by(email=data).first()
    if user:
        send_mail_reset_email(user)
    flash(
        "A confirmation email has been sent to your email with instructions on \
            how to reset your password, if not in the inbox section, kindly check the spam",
        "success")
    return redirect(url_for("src.views.products.home"))


@user.route("/reset/password/<token>", methods=["GET", "POST"])
def change_password(token):
    signup_form = SignupForm()
    log_form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("src.views.products.home"))
    else:
        if request.method == "POST":
            password = request.form.get("reset")
            user = confirm_token(token)
            client = User.query.filter_by(email=user).first()
            if client:
                try:
                    client.password = generate_password_hash(
                        password, method="sha256")
                    db.session.commit()
                    flash("you have successfully updated your \
                        password", "success")
                    return redirect(url_for("src.views.products.home"))
                except client.error:
                    flash("password reset failed please contact \
                        the admin", "danger")
                    return redirect(url_for("src.views.products.home"))
        return render_template(
            'reset_password.html', sign_form=signup_form,
            log_form=log_form)


@user.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have logged out now.', "info")
    return redirect(url_for("src.views.products.home"))


# PATCH /users
@user.route('/update/user/info/<name>/<int:id>', methods=['POST'])
@login_required
def updateuser(name, id):
    newname = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    client = User.query.filter_by(id=id).first_or_404()
    profile_image = request.files['profile']
    if client:
        if name and name == client.name:
            if current_user.name == client.name:
                client.name = newname
                client.email = email
                client.phone = phone
                if profile_image:
                    profile_pic = validate_profile_image(profile_image)
                    client.user_img = profile_pic
                db.session.commit()
                return redirect(url_for('src.views.products.account'))
            else:
                db.session.rollback()
    db.session.rollback()
    abort(404)


@user.route('/privacy')
def privacy():
    signup_form = SignupForm()
    log_form = LoginForm()
    return render_template(
        'privacy.html', sign_form=signup_form, log_form=log_form)


@user.route('/terms')
def terms():
    signup_form = SignupForm()
    log_form = LoginForm()
    return render_template(
        'terms.html', sign_form=signup_form, log_form=log_form)


@user.route('/about')
def about():
    signup_form = SignupForm()
    log_form = LoginForm()
    return render_template(
        'about.html', sign_form=signup_form, log_form=log_form)


@user.route('/buyers')
def buyers():
    signup_form = SignupForm()
    log_form = LoginForm()
    return render_template(
        'buyers.html', sign_form=signup_form, log_form=log_form)


@user.route('/safety')
def safety():
    signup_form = SignupForm()
    log_form = LoginForm()
    return render_template(
        'safety.html', sign_form=signup_form, log_form=log_form)


@user.route('/sellers')
def sellers():
    signup_form = SignupForm()
    log_form = LoginForm()
    return render_template(
        'sellers.html', sign_form=signup_form, log_form=log_form)


@user.route('/confirm/<token>')
def confirm_email(token):
    client = confirm_token(token)
    user = User.query.filter_by(email=client).first_or_404()
    if user.confirmed:
        flash(
            'Account successfully confirmed you can now \
                login to your account', 'success')
        return redirect(url_for('src.views.products.home'))
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
        login_user(user)
        return redirect(url_for('src.views.products.home'))
