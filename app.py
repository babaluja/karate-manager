import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "karate_club_secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# configure the database
# Per database mobile, usa SQLite in una posizione accessibile
db_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(db_folder, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(db_folder, 'karate_manager.db')}")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize the app with the extensions
db.init_app(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Rotta di login
login_manager.login_message = 'Accedi per visualizzare questa pagina'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models here so they are registered with SQLAlchemy
    from models import Athlete, Payment, Exam, User  # noqa: F401
    db.create_all()

# Import routes after db initialization to avoid circular imports
from routes import *  # noqa: F401, E402

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
