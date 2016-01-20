__author__ = 'Alimohammad'
from flask import redirect, url_for, request, render_template, abort
from flask_login import login_user, login_required, current_user, logout_user
from flask import current_app

from data_model import User
from forms import LoginForm, ForgotPasswordForm, ChangePassowrdForm, recaptcha_check

from flask import Blueprint

import mail_handler

common_views = Blueprint('common_views', __name__, template_folder='templates')

@common_views.route('/', methods=["GET", "POST"])
def index():
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST' and form.validate():
        user = User.get(email=form.email.data)
        if user is not None:
            if user.authenticate(form.password.data):
                if login_user(user, remember=True):
                    current_app.logger.debug(url_for("user_views.devices_view"))
                    return redirect(request.args.get("next") or url_for("user_views.devices_view"))
            else:
                error = "Email and password do not match!"
        else:
            error = "A user with this email does not exist!"
    return render_template("index.html", form=form, error=error)

@common_views.route('/about/', methods=["GET", "POST"])
def about():
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST' and form.validate():
        user = User.get(email=form.email.data)
        if user is not None:
            if user.authenticate(form.password.data):
                if login_user(user, remember=True):
                    return redirect(request.args.get("next") or url_for("user_views.devices_view"))
            else:
                error = "Email and password do not match!"
        else:
            error = "A user with this email does not exist!"
    return render_template("about.html", form=form, error=error)

@common_views.route('/participate/', methods=["GET", "POST"])
def participate():
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST' and form.validate():
        user = User.get(email=form.email.data)
        if user is not None:
            if user.authenticate(form.password.data):
                if login_user(user, remember=True):
                    return redirect(request.args.get("next") or url_for("user_views.devices_view"))
            else:
                error = "Email and password do not match!"
        else:
            error = "A user with this email does not exist!"
    return render_template("participate.html", form=form, error=error)

@common_views.route('/forgotpassword/', methods=["GET", "POST"])
def forgot_password():
    forgot_form = ForgotPasswordForm(request.form)
    error = None
    if request.method == 'POST':
        if forgot_form.validate() and recaptcha_check(request.form["g-recaptcha-response"]):
            user = User.get(email=forgot_form.email.data)
            if user is not None:
                if user.forgot_password():
                    link = url_for("common_views.change_password", user_id=user.user_id, secret=user.forgot_secret, _external=True)
                    current_app.logger.info(link)
                    mail = mail_handler.Mail(user.email, link)
                    mail.send()
                    return redirect(url_for("common_views.index"))
            else:
                error = "A user with this email does not exist!"
        else:
            error = "Please enter email address and prove you are not a robot!"
    return render_template("forgot.html", forgot_form=forgot_form, error=error)

@common_views.route('/changepassword/<user_id>/<secret>', methods=["GET", "POST"])
def change_password(user_id, secret):
    if not User.validate_reset_secret(user_id, secret):
        abort(403)
    change_pass_form = ChangePassowrdForm(request.form)
    error = None
    if request.method == 'POST' and change_pass_form.validate():
        User.change_password(user_id, change_pass_form.password.data)
        return redirect(url_for("common_views.index"))
    return render_template("change_pass.html", change_form=change_pass_form, error=error)

@common_views.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("common_views.index"))
