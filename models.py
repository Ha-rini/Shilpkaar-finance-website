from flask_sqlalchemy import SQLAlchemy
from extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime

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

class Order(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.Date,nullable=False)
    total_cost=db.Column(db.Float,nullable=False)
    notes=db.Column(db.String(256))
    status=db.Column(db.String,default="order placed")
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"))

    items=db.relationship("Product",backref="order",lazy=True,cascade='all,delete-orphan')

class Product(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    product_type = db.Column(db.Integer, db.ForeignKey("product_type.id"))
    sheet_type=db.Column(db.String,nullable=False)
    quantity=db.Column(db.Integer,default=1)
    price=db.Column(db.Float,nullable=False)
    total_price=db.Column(db.Float,nullable=False)
    order_id=db.Column(db.Integer,db.ForeignKey("order.id"))

class Cost(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    raw_material_cost=db.Column(db.Float,nullable=False)
    weaving_cost=db.Column(db.Float,nullable=False)
    transport_cost=db.Column(db.Float,nullable=False)
    tailoring_cost=db.Column(db.Float,nullable=False)
    rajiben_profit=db.Column(db.Float,nullable=False)
    pratibatai_profit=db.Column(db.Float,nullable=False)
    total_cost=db.Column(db.Float,nullable=False)
    order_id=db.Column(db.Integer,db.ForeignKey("order.id"))

    rajiben=db.relationship("Rajiben", backref="cost", lazy=True, cascade='all,delete-orphan')
    pratibatai=db.relationship("Pratibatai", backref="cost", lazy=True, cascade='all,delete-orphan')


class Rajiben(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    cumulative_cost=db.Column(db.Float,nullable=False)
    cumulative_profit=db.Column(db.Float,nullable=False)
    order_id=db.Column(db.Integer,db.ForeignKey("order.id"))
    cost_id=db.Column(db.Integer,db.ForeignKey("cost.id"))

class Pratibatai(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    cumulative_cost=db.Column(db.Float,nullable=False)
    cumulative_profit=db.Column(db.Float,nullable=False)
    order_id=db.Column(db.Integer,db.ForeignKey("order.id"))
    cost_id=db.Column(db.Integer,db.ForeignKey("cost.id"))

# with app.app_context(): #only when flask server/ application is ready then create the tables
#     db.create_all()
#     admin=User.query.filter_by(is_admin=True).first()
#     if not admin:
#         admin1= User(username='bhavya',password=generate_password_hash('password'),is_admin=True)
#         admin2= User(username='garv',password=generate_password_hash('password'),is_admin=True)
#         db.session.add(admin1)
#         db.session.add(admin2)
#         db.session.commit()
