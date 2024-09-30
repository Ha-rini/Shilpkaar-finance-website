from flask import Flask, json,render_template,request,jsonify, redirect, session, url_for,flash
from app import app
from flask_restful import Api, Resource,reqparse,abort
from models import db, User, Order, Product, Cost, Rajiben, Pratibatai,Product_type,Inventory
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from collections import Counter, defaultdict
from sqlalchemy import or_,and_
import math



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
    return render_template("index.html")


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form.get('log_email')
        password=request.form.get('password')
        user=User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password,password):
            
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

cost_details = {
    "Tote Bag": {
        "Raw Material": 50,
        "Weaving": 150,
        "Rajiben Profit": 70,
        "Transport to Mumbai": 40,
        "Tailoring Cost": 170,
        "Pratibha Tai Profit": 60,
        "Travels": 100,
        "Total Cost": 640,
        "Price of Product": 700
    },
    "Pouch": {
        "Raw Material": 25,
        "Weaving": 75,
        "Rajiben Profit": 35,
        "Transport to Mumbai": 40,
        "Tailoring Cost": 110,
        "Pratibha Tai Profit": 39,
        "Travels": 100,
        "Total Cost": 424,
        "Price of Product": 450
    },
    "Sling Bag": {
        "Raw Material": 25,
        "Weaving": 75,
        "Rajiben Profit": 35,
        "Transport to Mumbai": 40,
        "Tailoring Cost": 220,
        "Pratibha Tai Profit": 77,
        "Travels": 100,
        "Total Cost": 572,
        "Price of Product": 600
    },
    "Laptop Sleeve": {
        "Raw Material": 25,
        "Weaving": 75,
        "Rajiben Profit": 35,
        "Transport to Mumbai": 40,
        "Tailoring Cost": 140,
        "Pratibha Tai Profit": 105,
        "Travels": 100,
        "Total Cost": 520,
        "Price of Product": 550
    }
}

@app.route('/new_order',methods=['GET','POST'])
@check_admin
def new_order():
    if request.method == 'POST':
        items_json = request.form.get('items_json')
        items = []
        if items_json:
            items = json.loads(items_json)
         
        notes = request.form.get('notes')
        payment_made_by = request.form.get('payment_made_by')
        
        # Calculate and handle costs here
        raw_material_cost=0
        weaving_cost=0
        transport_cost=0
        rajiben_profit=0
        rajiben_total=0

        tailoring_cost=0
        pratibatai_profit=0
        pratibatai_total=0

        travels_cost=0

        total_cost = 0
        for item in items:
            # Cost calculation logic
            qty = int(item['quantity'])
            raw_material_cost+=int(cost_details[item["productType"]]["Raw Material"]*qty)
            weaving_cost+=int(cost_details[item["productType"]]["Weaving"]*qty)
            transport_cost+=int(cost_details[item["productType"]]["Transport to Mumbai"])
            rajiben_profit+=int(cost_details[item["productType"]]["Rajiben Profit"]*qty)
            rajiben_total+=int(raw_material_cost+weaving_cost+transport_cost+rajiben_profit)

            tailoring_cost+=int(cost_details[item["productType"]]["Tailoring Cost"]*qty)
            pratibatai_profit+=int(cost_details[item["productType"]]["Pratibha Tai Profit"]*qty)
            pratibatai_total+= tailoring_cost + pratibatai_profit

            total_cost += int(cost_details[item["productType"]]["Price of Product"]*qty)

        travels_cost= int(cost_details[item["productType"]]["Travels"])

        user = User.query.filter_by(username=session['username']).first()
        order = Order(user_id=user.id, date=datetime.now(), notes=notes, payment_made_by=payment_made_by, total_cost=total_cost)
        db.session.add(order)
        db.session.commit() 

        # Create and commit Product objects for each item in the order
        for item in items:
            product_type = Product_type.query.filter_by(product_name=item['productType']).first()
            product = Product(order_id=order.id, product_id=product_type.id, quantity=item['quantity'],
                              price=product_type.product_price, sheet_type=item['sheetType'],
                              total_price=int(item['quantity']) * product_type.product_price)
            db.session.add(product)

        # Generate and commit cost details
        cost = Cost(raw_material_cost=raw_material_cost, weaving_cost=weaving_cost, transport_cost=transport_cost,
                    tailoring_cost=tailoring_cost, rajiben_profit=rajiben_profit, pratibatai_profit=pratibatai_profit,
                    travels=travels_cost, total_cost=total_cost,order_id=order.id)
        db.session.add(cost)

        # Rajiben and Pratibatai cost records
        rajiben = Rajiben(cumulative_cost=rajiben_total, cumulative_profit=rajiben_profit, cost=cost)
        pratibatai = Pratibatai(cumulative_cost=pratibatai_total, cumulative_profit=pratibatai_profit, cost=cost)
        db.session.add(rajiben)
        db.session.add(pratibatai)

        # Commit everything at the end
        db.session.commit()

        session['items'] = items
        session['notes'] = notes
        session['total_cost'] = total_cost
        session['rajiben_total'] = rajiben_total
        session['rajiben_profit'] = rajiben_profit
        session['pratibatai_total'] = pratibatai_total
        session['pratibatai_profit'] = pratibatai_profit
        session['travels_cost'] = travels_cost
        session['cost'] = {
                            'raw_material_cost': cost.raw_material_cost,
                            'weaving_cost': cost.weaving_cost,
                            'transport_cost': cost.transport_cost,
                            'tailoring_cost': cost.tailoring_cost,
                            'rajiben_profit': cost.rajiben_profit,
                            'pratibatai_profit': cost.pratibatai_profit,
                            'travels': cost.travels,
                            'total_cost': cost.total_cost,
                        }
        return redirect(url_for('confirm_order'))
    return render_template('new_order.html')

@app.route('/confirm_order')
@check_admin
def confirm_order():
    # Fetch the necessary data from the session
    items = session.get('items', [])
    notes = session.get('notes', "")
    total_cost = session.get('total_cost', 0)
    rajiben_total = session.get('rajiben_total', 0)
    rajiben_profit = session.get('rajiben_profit', 0)
    pratibatai_total = session.get('pratibatai_total', 0)
    pratibatai_profit = session.get('pratibatai_profit', 0)
    travels_cost = session.get('travels_cost', 0)
    cost = session.get('cost', {})# Travel cost

     # Clear session after fetching data
    session.pop('items', None)
    session.pop('notes', None)
    session.pop('total_cost', None)
    session.pop('rajiben_total', None)
    session.pop('rajiben_profit', None)
    session.pop('pratibatai_total', None)
    session.pop('pratibatai_profit', None)
    session.pop('travels_cost', None)
    session.pop('cost', None)

    # Render the 'confirm_order.html' template and pass all relevant data
    return render_template('confirm_order.html', 
                           items=items,  # List of items and their details
                           notes=notes,  # Notes from the user
                           total_cost=total_cost,  # Total cost for the entire order
                           rajiben_total=rajiben_total,  # Rajiben's cumulative cost
                           rajiben_profit=rajiben_profit,  # Rajiben's profit
                           pratibatai_total=pratibatai_total,  # Pratibatai's cumulative cost
                           pratibatai_profit=pratibatai_profit,  # Pratibatai's profit
                           travels_cost=travels_cost,  # Travel cost
                           cost=cost  # Cost object
                          )

@app.route('/cancel_order')
def cancel_order():
    # Clear session on order cancellation
    session.pop('items', None)
    session.pop('notes', None)
    session.pop('total_cost', None)
    session.pop('rajiben_total', None)
    session.pop('rajiben_profit', None)
    session.pop('pratibatai_total', None)
    session.pop('pratibatai_profit', None)
    session.pop('travels_cost', None)
    session.pop('cost', None)

    return redirect(url_for('dashboard'))  # Redirect to a dashboard or home page

@app.route('/delete_order/<int:order_id>', methods=['POST'])
@check_admin
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    try:
        # Delete the order and all its associated products
        db.session.delete(order)
        db.session.commit()
        flash(f"Order {order_id} has been deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()  # Rollback if there's any error
        flash(f"Error occurred while deleting order {order_id}: {str(e)}", "danger")

    return redirect(url_for('dashboard'))  # Redirect to dashboard after deletion

@app.route('/order/<int:order_id>', methods=['GET'])
@check_admin
def view_order(order_id):
    # Fetch the specific order based on order_id
    order = Order.query.get_or_404(order_id)

    # Fetch associated products for the order
    products = Product.query.filter_by(order_id=order.id).all()
    items = [{
        'productType': prod.product_type.product_name,
        'quantity': prod.quantity,
        'dimensions': prod.product_type.product_dimension,
        'sheetType': prod.sheet_type
    } for prod in products]

    # Fetch associated cost details for the order
    cost = Cost.query.filter_by(order_id=order.id).first()

    # Rajiben and Pratiba Tai's financial details
    rajiben = Rajiben.query.filter_by(cost_id=cost.id).first()
    pratibatai = Pratibatai.query.filter_by(cost_id=cost.id).first()

    # Pass order details to the confirm_order.html template
    return render_template('confirm_order.html', 
                           items=items,  # List of products in the order
                           notes=order.notes,  # Notes from the user
                           total_cost=order.total_cost,  # Total cost for the entire order
                           rajiben_total=rajiben.cumulative_cost if rajiben else 0,  # Rajiben's cumulative cost
                           rajiben_profit=rajiben.cumulative_profit if rajiben else 0,  # Rajiben's profit
                           pratibatai_total=pratibatai.cumulative_cost if pratibatai else 0,  # Pratibatai's cumulative cost
                           pratibatai_profit=pratibatai.cumulative_profit if pratibatai else 0,  # Pratibatai's profit
                           travels_cost=cost.travels if cost else 0,  # Travel cost
                           cost=cost  # Cost object
                          )

@app.route('/overall_financials')
@check_admin
def overall_financials():
    orders = Order.query.all()
    return render_template('overall_financials.html', orders=orders)

from flask import render_template, request, redirect, url_for, flash
from sqlalchemy.orm.exc import NoResultFound

from flask import render_template, request, redirect, url_for, flash

@app.route('/edit_financials/<int:order_id>', methods=['GET', 'POST'])
def edit_financials(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        # Get new values from the form
        rajiben_amt_paid = float(request.form['rajiben_amt_paid'])
        pratibatai_amt_paid = float(request.form['pratibatai_amt_paid'])

        # Update Rajiben's cumulative cost and profit
        if order.cost.rajiben:
            rajiben = order.cost.rajiben
            rajiben.cumulative_cost = rajiben_amt_paid
            rajiben.cumulative_profit = rajiben_amt_paid - (order.cost.raw_material_cost + order.cost.weaving_cost + order.cost.transport_cost + order.cost.rajiben_profit)
        else:
            # Create a new entry if not already present
            rajiben = Rajiben(
                cumulative_cost=rajiben_amt_paid,
                cumulative_profit=rajiben_amt_paid - (order.cost.raw_material_cost + order.cost.weaving_cost + order.cost.transport_cost + order.cost.rajiben_profit),
                cost_id=order.cost.id
            )
            db.session.add(rajiben)

        # Update Pratiba Tai's cumulative cost and profit
        if order.cost.pratibatai:
            pratibatai = order.cost.pratibatai
            pratibatai.cumulative_cost = pratibatai_amt_paid
            pratibatai.cumulative_profit = pratibatai_amt_paid - (order.cost.tailoring_cost + order.cost.pratibatai_profit)
        else:
            # Create a new entry if not already present
            pratibatai = Pratibatai(
                cumulative_cost=pratibatai_amt_paid,
                cumulative_profit=pratibatai_amt_paid - (order.cost.tailoring_cost + order.cost.pratibatai_profit),
                cost_id=order.cost.id
            )
            db.session.add(pratibatai)

        # Commit the changes to the database
        db.session.commit()
        
        return redirect(url_for('overall_financials'))

    # Render the edit financials form, passing the order object
    return render_template('edit_financials.html', order=order)



@app.route('/rajiben')
def rajiben():
    rajiben_orders = Rajiben.query.all()  # or filter based on the requirement
    return render_template('rajiben.html', rajiben_orders=rajiben_orders)

@app.route('/pratiba')
def pratiba():
    pratibatai_orders = Pratibatai.query.all()  # or filter based on the requirement
    return render_template('pratibatai.html', pratibatai_orders=pratibatai_orders)

@app.route('/inventory')
@check_admin
def inventory():
    inventories=Inventory.query.all()
    return render_template('inventory.html',inventories=inventories)

@app.route('/new_inventory', methods=['GET', 'POST'])
@check_admin
def new_inventory():
    if request.method == 'POST':
        product_type = request.form.get('product_type')
        sheet_type = request.form.get('sheet_type')
        additional_option = request.form.get('additional_option')
        quantity_in_stock = request.form.get('quantity_in_stock', type=int)
        date_received = request.form.get('date_received')
        current_keeper = request.form.get('current_keeper')

        product = Product_type.query.filter_by(product_name=product_type).first()
        
        # Convert date from string to datetime object
        date_received_obj = datetime.strptime(date_received, '%Y-%m-%d')

        # If "Other (please specify)" is selected, use the additional option
        if sheet_type == 'Other (please specify)' and additional_option:
            sheet_type = additional_option
        
        # Create a new Inventory entry
        new_inventory_item = Inventory(
            product_name=product.product_name,  # Optional, if you want to keep this field
            sheet_type=sheet_type,  
            quantity_in_stock=quantity_in_stock,
            date_received=date_received_obj,
            current_keeper=current_keeper,
            product_type_id=product.id
        )

        # Add to the database
        db.session.add(new_inventory_item)
        db.session.commit()

        # Redirect to the inventory page after successfully adding the item
        return redirect(url_for('inventory'))  # Change 'inventory' to the correct endpoint name if necessary
    
    return render_template('new_inventory.html')


# Route to handle cancelling inventory input
@app.route('/cancel_inventory', methods=['GET'])
@check_admin
def cancel_inventory():
    return redirect(url_for('inventory'))

@app.route('/edit_inventory/<int:inventory_id>', methods=['GET', 'POST'])
@check_admin
def edit_inventory(inventory_id):
    inventory_item = Inventory.query.get(inventory_id)

    if request.method == 'POST':
        # Get updated values from the form
        product_type = request.form.get('product_type')
        sheet_type=request.form.get('sheet_type')
        quantity_in_stock = request.form.get('quantity_in_stock')
        date_received = request.form.get('date_received')
        current_keeper = request.form.get('current_keeper')
        
        product=Product_type.query.filter_by(product_name=product_type).first()
        # Update the inventory item
        inventory_item.product_name = product_type
        inventory_item.sheet_type=sheet_type
        inventory_item.quantity_in_stock = quantity_in_stock
        inventory_item.date_received = datetime.strptime(date_received, '%Y-%m-%d')
        inventory_item.current_keeper = current_keeper
        inventory_item.product_type_id=product.id

        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('inventory'))

    # Render the edit form with existing inventory item values
    return render_template('edit_inventory.html', inventory=inventory_item)

@app.route('/delete_inventory/<int:inventory_id>', methods=['POST'])
@check_admin
def delete_inventory(inventory_id):
    # Find the inventory item by ID
    inventory_item = Inventory.query.get(inventory_id)

    if inventory_item:
        db.session.delete(inventory_item)  # Delete the item from the database
        db.session.commit()  # Commit the changes

    return redirect(url_for('inventory'))  # Redirect to the inventory dashboard


# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear the session
    flash('You have been logged out.', category='info')
    return redirect(url_for('login'))
