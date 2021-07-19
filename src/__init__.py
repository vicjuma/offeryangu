from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_mail import Mail
from flask_msearch import Search
from flask_cors import CORS

db = SQLAlchemy()
loginmanager = LoginManager()
loginmanager.login_message_category = "warning"
loginmanager.login_view = "src.views.products.home"
migrate = Migrate()
moment = Moment()
mail = Mail()
search = Search()


def create_app(config_file='config.Config'):
    app = Flask(__name__)
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config.from_object(config_file)
    from src.views.users import user
    from src.errors import errors
    from src.views.products import product
    db.init_app(app)
    search.init_app(app)
    migrate.init_app(app, db=db, render_as_batch=True)
    moment.init_app(app)
    loginmanager.init_app(app)
    mail.init_app(app)
    app.register_blueprint(user, url_prefix='/users')
    app.register_blueprint(product, url_prefix='/')
    # app.register_blueprint(auth, url_prefix='/authenticate')
    app.register_blueprint(errors, url_prefix='/error')
    return app
