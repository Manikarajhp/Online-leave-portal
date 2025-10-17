from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os
import secrets
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from flask_login import LoginManager

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
# Prefer SESSION_SECRET, fall back to SECRET_KEY env var for compatibility
secret = os.environ.get("SESSION_SECRET") or os.environ.get("SECRET_KEY")
if not secret:
    # Generate an ephemeral secret for development so sessions work.
    # WARNING: this is not suitable for production because it changes on each
    # startup and will invalidate existing sessions. Set SESSION_SECRET in
    # your environment for a persistent secret.
    secret = secrets.token_urlsafe(32)
    logging.warning(
        "SESSION_SECRET not set; generated ephemeral secret key. Set SESSION_SECRET for persistent sessions."
    )
app.secret_key = secret
app.config['SECRET_KEY'] = secret
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
# Use DATABASE_URL from environment if provided, otherwise fall back to an
# instance-local SQLite database so the app can run in development without
# requiring an external DB.
db_uri = os.environ.get("DATABASE_URL")
if not db_uri:
    # Ensure the instance folder exists and use a file-based SQLite DB there.
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception:
        # In rare cases instance_path may be invalid; fall back to relative path
        os.makedirs(os.path.join(os.getcwd(), 'instance'), exist_ok=True)
        app.instance_path = os.path.join(os.getcwd(), 'instance')
    db_uri = f"sqlite:///{os.path.join(app.instance_path, 'app.db')}"
    logging.warning("DATABASE_URL not set; defaulting to SQLite DB at %s", db_uri)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

db = SQLAlchemy(app, model_class=Base)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    import models
    db.create_all()
    logging.info("Database tables created")
