from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash

from dotenv import load_dotenv
import os
from extensions import db, migrate
import models
# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and migration
# db.init_app(app)
# migrate.init_app(app, db)

# Import routes (after db initialization)

import routes

#Create tables and setup admin
with app.app_context():
    db.create_all()
    
    # Check if admin exists
    admin = models.User.query.filter_by(is_admin=True).first()
    if not admin:
        admin1 = models.User(username='bhavya', password=generate_password_hash('password'), is_admin=True)
        admin2 = models.User(username='garv', password=generate_password_hash('password'), is_admin=True)
        db.session.add(admin1)
        db.session.add(admin2)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)
    
