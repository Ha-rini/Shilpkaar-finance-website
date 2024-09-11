from flask import Flask,render_template,request,jsonify, redirect, session, url_for,flash
from flask_restful import Api, Resource,reqparse,abort
from models import db, User, Order, Product, Cost, Rajiben, Pratibatai
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import math
from collections import Counter, defaultdict
from sqlalchemy import or_,and_

from werkzeug.utils import secure_filename

from app import app


def check_admin(func):
    @wraps(func) #to avoid the server throwing an error for not having unique functions;   func-placeholder for the function passed (eg. profile(), login(), etc.)
    def wrapper(*args, **kwargs): #pack and unpacking of : args- positional arguments ; kwargs- keyword arguments
        if 'username' not in session:
            flash("You need to login first",category="danger")
            return redirect(url_for('login'))
        user=User.query.filter_by(username=session['username']).first()
        if not user:
            session.pop('username')
            return redirect(url_for('login'))
        if not user.is_admin:
            flash("You are not authorized to visit this page",category="danger")
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapper



@app.route('/')
def re():
    return redirect(url_for('login'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form.get('log_email')
        password=request.form.get('password')
        user=User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password,password):
            print("Incorrect credentials")
            return redirect(url_for('login'))
        session['username']=username
        return redirect(url_for('dashboard'))
    return render_template("index.html")


# Route to the home/dashboard page
@app.route('/dashboard')
@check_admin
def dashboard():
    orders=Order.query.all()
    return render_template('dashboard.html',orders=orders)


# Sample product cost data from the image
product_costs = {
    'Tote Bag': {
        'price': 700,
        'raw_material': 50,
        'weaving': 150,
        'transport': 40,
        'tailoring': 170,
        'travels': 100,
    },
    'Pouch': {
        'price': 450,
        'raw_material': 25,
        'weaving': 75,
        'transport': 40,
        'tailoring': 110,
        'travels': 100,
    },
    'Sling': {
        'price': 600,
        'raw_material': 25,
        'weaving': 75,
        'transport': 40,
        'tailoring': 220,
        'travels': 100,
    },
    'Laptop': {
        'price': 550,
        'raw_material': 25,
        'weaving': 75,
        'transport': 40,
        'tailoring': 170,
        'travels': 100,
    }
}

@app.route('/new_order', methods=['GET', 'POST'])
@check_admin
def new_order():
    if request.method == 'POST':
        product_type = request.form.get('product_type')
        quantity = int(request.form.get('quantity'))
        sheet_type = request.form.get('sheet_type')
        notes = request.form.get('notes')

        # Get the product details
        product = product_costs.get(product_type)
        if not product:
            return redirect(url_for('new_order'))  # If invalid product, redirect

        # Calculate costs and profits for Rajiben and Pratibha Tai
        raw_material_cost = product['raw_material'] * quantity
        weaving_cost = product['weaving'] * quantity
        transport_cost = product['transport'] * quantity
        tailoring_cost = product['tailoring'] * quantity
        travels_cost = product['travels'] * quantity
        total_price = product['price'] * quantity

        # Rajiben's profit: 35% of (raw material + weaving + transport)
        rajiben_profit = math.ceil(0.35 * (raw_material_cost + weaving_cost + transport_cost))

        # Pratibha Tai's profit: 35% of tailoring cost
        pratibatai_profit = math.ceil(0.35 * tailoring_cost)

        # Total cost
        total_cost = (raw_material_cost + weaving_cost + transport_cost + tailoring_cost + travels_cost)

        # Initialize the session storage if not present
        if 'order_data' not in session:
            session['order_data'] = {
                'items': [],
                'total_cost': 0,
                'cost': {
                    'raw_material_cost': 0,
                    'weaving_cost': 0,
                    'transport_cost': 0,
                    'tailoring_cost': 0,
                    'rajiben_profit': 0,
                    'pratibatai_profit': 0
                }
            }

        # Append the current product to the session's 'items'
        session['order_data']['items'].append({
            'product_type': product_type,
            'quantity': quantity,
            'sheet_type': sheet_type,
            'price': product['price'],
            'total_price': total_price
        })

        # Update the session data for the overall costs
        session['order_data']['total_cost'] += total_cost
        session['order_data']['cost']['raw_material_cost'] += raw_material_cost
        session['order_data']['cost']['weaving_cost'] += weaving_cost
        session['order_data']['cost']['transport_cost'] += transport_cost
        session['order_data']['cost']['tailoring_cost'] += tailoring_cost
        session['order_data']['cost']['rajiben_profit'] += rajiben_profit
        session['order_data']['cost']['pratibatai_profit'] += pratibatai_profit

        return redirect(url_for('confirm_order'))
    
    return render_template('new_order.html')

@app.route('/confirm_order', methods=['GET', 'POST'])
@check_admin
def confirm_order():
    if request.method == 'POST':
        order_data = session.get('order_data', {})

        if not order_data or not order_data['items']:
            return redirect(url_for('new_order'))  # Ensure there's valid order data

        # Create and save the order in the database
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            return redirect(url_for('login'))  # Ensure user exists

        # Create the order
        new_order = Order(
            date=datetime.utcnow(),
            total_cost=order_data['total_cost'],
            notes=order_data['notes'],
            user_id=user.id
        )
        db.session.add(new_order)
        db.session.commit()

        # Add each product to the database
        for item in order_data['items']:
            product = Product(
                product_type=item['product_type'],
                sheet_type=item['sheet_type'],
                quantity=item['quantity'],
                price=item['price'],
                total_price=item['total_price'],
                order_id=new_order.id
            )
            db.session.add(product)

        # Add cost details
        cost = Cost(
            raw_material_cost=order_data['cost']['raw_material_cost'],
            weaving_cost=order_data['cost']['weaving_cost'],
            transport_cost=order_data['cost']['transport_cost'],
            tailoring_cost=order_data['cost']['tailoring_cost'],
            rajiben_profit=order_data['cost']['rajiben_profit'],
            pratibatai_profit=order_data['cost']['pratibatai_profit'],
            total_cost=order_data['total_cost'],
            order_id=new_order.id
        )
        db.session.add(cost)

        # Update Rajiben and Pratibha Tai's cumulative profits
        rajiben = Rajiben.query.first()
        pratibatai = Pratibatai.query.first()

        rajiben.cumulative_profit += order_data['cost']['rajiben_profit']
        pratibatai.cumulative_profit += order_data['cost']['pratibatai_profit']

        db.session.add(rajiben)
        db.session.add(pratibatai)

        db.session.commit()

        # Clear the session after successful save
        session.pop('order_data', None)

        return redirect(url_for('dashboard'))

    order_data = session.get('order_data', {})
    return render_template('confirm_order.html', order=order_data)



@app.route('/overall_financials')
@check_admin
def overall_financials():
    orders = Order.query.all()
    return render_template('overall_financials.html', orders=orders)

@app.route('/rajiben')
def rajiben():
    orders = Order.query.all()
    rajiben_financials = Rajiben.query.all()
    return render_template('rajiben.html', orders=orders, rajiben_financials=rajiben_financials)

@app.route('/pratiba')
def pratiba():
    orders = Order.query.all()
    pratibatai_financials = Pratibatai.query.all()
    return render_template('pratibatai.html', orders=orders, pratibatai_financials=pratibatai_financials)



# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear the session
    flash('You have been logged out.', category='info')
    return redirect(url_for('login'))
