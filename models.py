from flask_sqlalchemy import SQLAlchemy
from app import app
from werkzeug.security import generate_password_hash
from datetime import datetime
from flask_migrate import Migrate


db=SQLAlchemy(app)
migrate = Migrate(app, db)


#models

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,nullable=False,unique=True)
    password=db.Column(db.String,nullable=False)
    is_admin=db.Column(db.Boolean,default=False)
    orders=db.relationship("Order",backref="user",lazy=True,cascade='all,delete-orphan')

class Product_type(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    product_name=db.Column(db.String,nullable=False,unique=True)
    product_price=db.Column(db.Float,nullable=False)
    product_dimension=db.Column(db.String,nullable=False)

    prods=db.relationship("Product",backref="product_type",lazy=True,cascade='all,delete-orphan')
    inventory = db.relationship('Inventory', backref='product_type',lazy=True,cascade='all,delete-orphan')

class Order(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.Date,nullable=False)
    total_cost=db.Column(db.Float,nullable=False)
    notes=db.Column(db.String(256))
    payment_made_by=db.Column(db.String,nullable=False)
    status=db.Column(db.String,default="order placed")
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)

    products=db.relationship("Product",backref="order",lazy=True,cascade='all,delete-orphan')
    cost=db.relationship("Cost",backref="order",uselist=False,lazy=True,cascade='all,delete-orphan')
    
class Product(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    sheet_type=db.Column(db.String,nullable=False)
    quantity=db.Column(db.Integer,default=1)
    price=db.Column(db.Float,nullable=False)
    total_price=db.Column(db.Float,nullable=False)
    
    order_id=db.Column(db.Integer,db.ForeignKey("order.id"),nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey("product_type.id"),nullable=False)

class Cost(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    raw_material_cost=db.Column(db.Float,nullable=False)
    weaving_cost=db.Column(db.Float,nullable=False)
    transport_cost=db.Column(db.Float,nullable=False)
    tailoring_cost=db.Column(db.Float,nullable=False)
    rajiben_profit=db.Column(db.Float,nullable=False)
    pratibatai_profit=db.Column(db.Float,nullable=False)
    travels=db.Column(db.Float,nullable=False)
    total_cost=db.Column(db.Float,nullable=False)
    order_id=db.Column(db.Integer,db.ForeignKey("order.id"),nullable=False)

    rajiben=db.relationship("Rajiben",uselist=False, backref="cost", lazy=True, cascade='all,delete-orphan')
    pratibatai=db.relationship("Pratibatai",uselist=False, backref="cost", lazy=True, cascade='all,delete-orphan')


class Rajiben(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    cumulative_cost=db.Column(db.Float,nullable=False)
    cumulative_profit=db.Column(db.Float,nullable=False)
    cost_id=db.Column(db.Integer,db.ForeignKey("cost.id"),nullable=False)

class Pratibatai(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    cumulative_cost=db.Column(db.Float,nullable=False)
    cumulative_profit=db.Column(db.Float,nullable=False)
    cost_id=db.Column(db.Integer,db.ForeignKey("cost.id"),nullable=False)

class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    date_received=db.Column(db.Date,nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    sheet_type = db.Column(db.String(100), nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    current_keeper = db.Column(db.String(50), nullable=False)
    
    # Relationships
    product_type_id = db.Column(db.Integer, db.ForeignKey('product_type.id'), nullable=True)

with app.app_context(): #only when flask server/ application is ready then create the tables
    db.create_all()
    admin=User.query.filter_by(is_admin=True).first()
    if not admin:
        admin1= User(username='bhavya',password=generate_password_hash('password'),is_admin=True)
        admin2= User(username='garv',password=generate_password_hash('password'),is_admin=True)
        db.session.add(admin1)
        db.session.add(admin2)
        db.session.commit()
