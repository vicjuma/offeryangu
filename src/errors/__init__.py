from flask import Blueprint, render_template
from src.forms import SearchForm, SignupForm, LoginForm

errors = Blueprint(__name__, 'errors', template_folder='../templates/')


@errors.app_errorhandler(404)
def not_found(error):
    search_form = SearchForm()
    signup_form = SignupForm()
    login_form = LoginForm()
    return render_template(
        "errors/404.html", search_form=search_form,
        sign_form=signup_form, log_form=login_form), 404


@errors.app_errorhandler(403)
def forbidden(error):
    signup_form = SignupForm()
    login_form = LoginForm()
    return render_template(
        "errors/403.html", sign_form=signup_form,
        log_form=login_form), 403


@errors.app_errorhandler(500)
def internal_server(error):
    signup_form = SignupForm()
    login_form = LoginForm()
    return render_template(
        "errors/500.html", sign_form=signup_form,
        log_form=login_form), 500
