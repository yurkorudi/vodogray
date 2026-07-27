from flask import current_app, request, session
from flask_babel import Babel


babel = Babel()


def normalize_locale(locale):
    supported = current_app.config["BABEL_SUPPORTED_LOCALES"]
    if locale in supported:
        return locale
    return current_app.config["BABEL_DEFAULT_LOCALE"]


def get_locale():
    supported = current_app.config["BABEL_SUPPORTED_LOCALES"]

    if request.args.get("lang") in supported:
        return request.args["lang"]

    if session.get("lang") in supported:
        return session["lang"]

    return request.accept_languages.best_match(supported) or current_app.config["BABEL_DEFAULT_LOCALE"]
