import os

base = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base, 'app.sqlite')
    DEBUG = True
    # TESTING = True
    SECRET_KEY = 'd7bf7040ee06491787b18b62569a8e1a'
    RECAPTCHA_PUBLIC_KEY = "6LdqgWAbAAAAAMtOplh6Vlva1JAaUjxGtYCeo0k0"
    RECAPTCHA_PRIVATE_KEY = "6LdqgWAbAAAAAHvdOnMifvpXclNSPe_MMkSfaHcN"
    UPLOAD_FOLDER = './src/static/images/uploads/'
    PROFILE_PICS_FOLDER = './src/static/images/profile_pics/'
    ENV = 'development'
    ALLOWED_FILES = [
        ".jpeg", ".png", ".JPEG", ".jPEG", ".Png",
        ".PNG", ".webp", ".jpg", ".gif", ".Jpeg"]
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SQLALCHEMY_ECHO = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'info@offeryangu.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'offeryangu.ke'
    MAIL_USE_TLS = True
    MAIL_PORT = 587
    MAIL_SERVER = 'mail.offeryangu.com'
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = True


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base, 'test.db')
    ENV = 'testing'
