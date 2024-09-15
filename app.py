from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Import configuration
import config

# Import database models
import models

# Import routes
import routes
