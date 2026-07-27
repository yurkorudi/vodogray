import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "QwErTy15243")
    ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin").strip()
    ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123").strip()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = "uk"
    BABEL_SUPPORTED_LOCALES = ["uk", "en"]
    BABEL_TRANSLATION_DIRECTORIES = "translations"
