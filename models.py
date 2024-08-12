from flask_sqlalchemy import SQLAlchemy
from app import app
from werkzeug.security import generate_password_hash
from datetime import datetime
from flask_migrate import Migrate

db=SQLAlchemy(app)
migrate = Migrate(app, db)

#models

