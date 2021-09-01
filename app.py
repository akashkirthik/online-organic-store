from flask import render_template, url_for, Flask, request, flash, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('password')
app.config['MYSQL_DB'] = os.getenv('dbName')
app.config["SECRET_KEY"] = os.getenv('secretKey')
mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('home.html')


# Directs to Farmer Sign-in

@app.route('/farmerLogin', methods=["GET", "POST"])
def farmerLogin():
    if request.method == "POST":
        print(request.form.get('email'), request.form.get('password'))

        email, password = request.form.get('email'), request.form.get('password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM farmer WHERE email_id = % s', (email,))
        account = cursor.fetchone()
        if account and check_password_hash(account['password'], password):
            session['farmer_id'] = account['farmer_id']
            cursor.close()
            return redirect('/stock', loggedIn=True)
        else:
            flash('Wrong credentials !')
            cursor.close()
            return render_template('farmerlogin.html')
    else:
        cursor.close()
        return render_template('farmerlogin.html')


# Directs to Buyer Sign-in

@app.route('/customerLogin', methods=["GET", "POST"])
def customerLogin():
    if request.method == "POST":
        print(request.form.get('email'), request.form.get('password'))

        email, password = request.form.get('email'), request.form.get('password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM buyer WHERE email_id = % s', (email,))
        account = cursor.fetchone()
        cursor.close()
        if account and check_password_hash(account['password'], password):
            session['buyer_id'] = account['buyer_id']
            return redirect('/shop')
        else:
            flash('Wrong credentials !')
            return render_template('custlogin.html')
    else:

        return render_template('custlogin.html')


# Directs to Farmer Sign-up

@app.route('/farmerSignUp', methods=["GET", "POST"])
def farmerSignUp():
    if request.method == "POST":
        email, password, name, age, contact, gender, experience, landarea, door, street, locality, city, pincode = request.form.get(
            "email"), request.form.get("password"), request.form.get("name"), request.form.get("age"), request.form.get(
            "contact"), request.form.get(
            "gender"), request.form.get("experience"), request.form.get("landarea"), request.form.get(
            "door"), request.form.get(
            "street"), request.form.get("locality"), request.form.get("city"), request.form.get("pincode")

        hashedPWD = generate_password_hash(password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM farmer WHERE email_id = % s', (email,))
        account = cursor.fetchone()

        if account:

            flash('User email already taken !')

        else:

            cursor.execute(
                'INSERT INTO farmer VALUES ( null, % s, % s, % s , % s, % s, % s, % s, % s, % s, % s, % s, % s, % s )',
                (name, age, gender, contact, email, experience, landarea, door, street, locality, city, pincode,
                 hashedPWD))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('farmerLogin'))

    return render_template('farm.html')


# Directs to Buyer Sign-up

@app.route('/customerSignUp', methods=["GET", "POST"])
def customerSignUp():
    if request.method == "POST":
        email, password, name, age, contact, gender, experience, landarea, door, street, locality, city, pincode = request.form.get(
            "email"), request.form.get("password"), request.form.get("name"), request.form.get("age"), request.form.get(
            "contact"), request.form.get(
            "gender"), request.form.get("experience"), request.form.get("landarea"), request.form.get(
            "door"), request.form.get(
            "street"), request.form.get("locality"), request.form.get("city"), request.form.get("pincode")

        hashedPWD = generate_password_hash(password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM buyer WHERE email_id = % s', (email,))
        account = cursor.fetchone()
        if account:

            flash('User email already taken !')

        else:

            cursor.execute(
                'INSERT INTO buyer VALUES ( null, % s, % s, % s , % s,  % s, % s, % s, % s, % s, % s, % s )',
                (name, age, gender, contact, email, door, street, locality, city, pincode,
                 hashedPWD))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('customerLogin'))

    return render_template('cust.html')


# Directs to Contact

@app.route('/contact', methods=["GET", "POST"])
def contact():
    return render_template('contact.html')


# directs farmer to stocks page. LOGIN REQUIRED

@app.route('/stock', methods=["GET", "POST"])
def stocks():
    if "farmer_id" not in session:
        return redirect('/farmerLogin')
    farmer_id = session['farmer_id']
    return_data = []
    to_fetch = []
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select stock_id from stock where farmer_id=%s', (farmer_id,))
    stocks = cursor.fetchall()

    for i in stocks:
        to_fetch.append(i['stock_id'])
    for i in to_fetch:
        cursor.execute('select name,available_quantity from holds where stock_id=%s', (i,))
        y = cursor.fetchone()

        if y:
            return_data.append({'name': y['name'], 'available_quantity': y['available_quantity'], 'stock_id': i})
    cursor.close()
    print(return_data)
    return_data = None if return_data == [] else return_data
    return render_template('stock.html', f_id=farmer_id, ret_data=return_data)


@app.route('/addStock', methods=["POST"])
def addStock():
    if "farmer_id" not in session:
        return redirect('/farmerLogin')
    farmer_id = session['farmer_id']
    print(farmer_id)
    # print(request.form.get('capacity'),request.form.get('description'),request.form.get('door'),request.form.get('street'),request.form.get('locality'),request.form.get('city'),request.form.get('pincode'))
    capacity, product, door, street, locality, city, pincode = request.form.get('capacity'), request.form.get(
        'product'), request.form.get('door'), request.form.get('street'), request.form.get(
        'locality'), request.form.get('city'), request.form.get('pincode')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(
        'INSERT INTO stock VALUES ( null, % s, % s, % s , % s,  % s, % s, % s )',
        (capacity, door, street, locality, city, pincode, farmer_id))
    cursor.execute('select max(stock_id) from stock where farmer_id=%s ', (farmer_id,))
    s_id = cursor.fetchone()
    s_id = s_id['max(stock_id)']
    cursor.execute('select product_id from product where name=%s', (product,))
    p_id = cursor.fetchone()
    p_id = p_id['product_id']
    cursor.execute(
        'INSERT INTO holds VALUES (  % s, % s, % s , % s )',
        (s_id, p_id, product, 0))
    mysql.connection.commit()
    cursor.close()
    flash('Added Successfully')
    return redirect('/stock'.format(farmer_id))


@app.route('/updateStock', methods=["POST"])
def updateStock():
    if "farmer_id" not in session:
        return redirect('/farmerLogin')
    farmer_id = session['farmer_id']
    print(farmer_id, request.form.get('uStockID'), request.form.get('quantity'), request.form.get('product'))
    uStockID, quantity, product = request.form.get('uStockID'), request.form.get('quantity'), request.form.get(
        'product')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT count(available_quantity) from holds where stock_id= %s and name=%s', (uStockID, product))
    q = cursor.fetchone()

    c = q['count(available_quantity)']
    if c == 0:
        cursor.execute('SELECT product_id from product where name= %s', (product,))
        w = cursor.fetchone()
        prod_id = w['product_id']
        cursor.execute('insert into holds values (%s,%s,%s,%s)', (uStockID, prod_id, product, quantity))
        flash('initialized stock values')
    else:
        cursor.execute('update holds set available_quantity=%s where name=%s and stock_id=%s',
                       (quantity, product, uStockID))
        flash('updated stock values')
    mysql.connection.commit()
    cursor.close()
    return redirect('/stock'.format(farmer_id))


@app.route('/shop', methods=["GET", "POST"])
def loggedShop():
    if "buyer_id" not in session:
        return redirect('/customerLogin')
    buyer_id = session['buyer_id']
    return render_template('shop.html', b_id=buyer_id)


@app.route('/<int:product_id>/buy', methods=["GET", "POST"])
def buyProduct(product_id):
    if 'buyer_id' not in session:
        return redirect('/customerLogin')

    buyer_id = session['buyer_id']
    session['product_id'] = product_id
    print(buyer_id, product_id)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT h.name,h.available_quantity, s.city,p.price,s.stock_id,p.product_id from holds h, stock s , product p where h.product_id= %s and h.stock_id=s.stock_id and h.product_id=p.product_id ',
        (product_id,))
    res = cursor.fetchall()
    cursor.close()
    if len(res) == 0:
        flash('Out of stock ')
    return render_template('buy.html', ret_data=res)


@app.route('/<int:stock_id>/cart', methods=["GET", "POST"])
def addToCart(stock_id):
    if 'buyer_id' not in session:
        return redirect('/customerLogin')
    if 'product_id' not in session:
        return redirect('/shop')
    buyer_id, product_id, stock_id = session['buyer_id'], session['product_id'], stock_id
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select cart_id from assign where buyer_id=%s', (buyer_id,))
    res = cursor.fetchone()
    if res is None:
        # assign cart to a user
        cursor.execute('insert into assign values(null,%s )', (buyer_id,))
        mysql.connection.commit()
    cursor.execute('select a.cart_id,p.name,p.price from assign a, product p  where a.buyer_id=%s and p.product_id=%s',
                   (buyer_id, product_id,))
    res = cursor.fetchone()
    cursor.execute('select * from cart where stock_id=%s and buyer_id=%s', (stock_id, buyer_id,))
    tmp = cursor.fetchone()
    if tmp is None:
        cursor.execute('insert into cart values (%s,%s,%s,%s,%s,%s,%s)',
                       (res['cart_id'], buyer_id, product_id, res['name'], stock_id, 0, 0))
        mysql.connection.commit()
    cursor.execute('select * from cart where stock_id=%s and buyer_id=%s', (stock_id, buyer_id,))
    tmp = cursor.fetchone()
    print(tmp)
    cursor.execute(
        'select c.name,c.quantity,c.price,c.cart_id,c.stock_id,c.buyer_id,p.price as unitPrice from cart c, product p where c.cart_id=%s and c.product_id=p.product_id',
        (tmp['cart_id'],))
    result = cursor.fetchall()
    print(result)
    cursor.execute(
        'select sum(price) as total from cart where cart_id=%s',
        (tmp['cart_id'],))
    total = cursor.fetchone()['total']
    print(total)
    cursor.close()
    return render_template('cart.html', cart_item=result, total=total)


@app.route('/<int:stock_id>/add')
def addItem(stock_id):
    if 'buyer_id' not in session:
        return redirect('/customerLogin')
    buyer_id = session['buyer_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select * from cart where stock_id=%s and buyer_id=%s', (stock_id, buyer_id,))
    tmp = cursor.fetchone()
    print(tmp)
    if tmp is not None:
        cursor.execute(
            'select c.name,c.quantity,c.price,c.cart_id,c.stock_id,c.buyer_id,p.price as unitPrice from cart c, product p where c.cart_id=%s and c.stock_id=%s and p.product_id=c.product_id',
            (tmp['cart_id'], stock_id,))
        res = cursor.fetchone()
        newQuantity, newPrice = 1 + res['quantity'], res['price'] + res['unitPrice']
        cursor.execute('update cart set quantity=%s, price=%s where cart_id=(%s) and stock_id=%s',
                       (newQuantity, newPrice, tmp['cart_id'], stock_id,))
        mysql.connection.commit()
    cursor.execute(
        'select c.name,c.quantity,c.price,c.cart_id,c.stock_id,c.buyer_id,p.price as unitPrice from cart c, product p where c.cart_id=%s and c.product_id=p.product_id',
        (tmp['cart_id'],))
    result = cursor.fetchall()
    print(result)
    cursor.execute(
        'select sum(price) as total from cart where cart_id=%s',
        (tmp['cart_id'],))
    total = cursor.fetchone()['total']
    print(total)
    cursor.close()
    return render_template('cart.html', cart_item=result, total=total)


@app.route('/<int:stock_id>/remove')
def removeItem(stock_id):
    if 'buyer_id' not in session:
        return redirect('/customerLogin')
    buyer_id = session['buyer_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select * from cart where stock_id=%s and buyer_id=%s', (stock_id, buyer_id,))
    tmp = cursor.fetchone()
    print(tmp)
    if tmp is not None:
        cursor.execute(
            'select c.name,c.quantity,c.price,c.cart_id,c.stock_id,c.buyer_id,p.price as unitPrice from cart c, product p where c.cart_id=%s and c.stock_id=%s and p.product_id=c.product_id',
            (tmp['cart_id'], stock_id,))
        res = cursor.fetchone()
        newQuantity, newPrice = -1 + res['quantity'], res['price'] - res['unitPrice']
        if newQuantity >= 0:
            cursor.execute('update cart set quantity=%s, price=%s where cart_id=(%s) and stock_id=%s',
                           (newQuantity, newPrice, tmp['cart_id'], stock_id,))
        else:
            cursor.execute('delete from cart where cart_id=%s and stock_id=%s', (tmp['cart_id'], stock_id,))

        mysql.connection.commit()
    cursor.execute(
        'select c.name,c.quantity,c.price,c.cart_id,c.stock_id,c.buyer_id,p.price as unitPrice from cart c, product p where c.cart_id=%s and c.product_id=p.product_id',
        (tmp['cart_id'],))
    result = cursor.fetchall()
    print(result)
    cursor.execute(
        'select sum(price) as total from cart where cart_id=%s',
        (tmp['cart_id'],))
    total = cursor.fetchone()['total']
    print(total)
    cursor.close()
    return render_template('cart.html', cart_item=result, total=total)


@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    if 'buyer_id' not in session:
        return redirect('/customerLogin')
    buyer_id = session['buyer_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'select sum(c.price) as amount from cart c, assign a where c.buyer_id=%s  and c.buyer_id=a.buyer_id and a.cart_id=c.cart_id',
        (buyer_id,))
    amount = cursor.fetchone()['amount']
    cursor.close()
    return render_template('payment.html', amount=amount)


@app.route('/pay', methods=["POST"])
def pay():
    if 'buyer_id' not in session:
        return redirect('/customerLogin')
    buyer_id = session['buyer_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select sum(price),stock_id as amount,cart_id from cart where buyer_id=%s', (buyer_id,))
    result = cursor.fetchone()
    amount = result['amount']

    cart_id = result['cart_id']
    cursor.execute('insert into payment values(null,%s,%s,%s,%s)',
                   (buyer_id, cart_id, amount, request.form.get("paymentMethod")))
    cursor.execute('select stock_id,quantity from cart where buyer_id=%s', (buyer_id,))
    result = cursor.fetchall()
    cursor.execute('delete from cart where cart_id=%s', (cart_id,))
    for item in result:
        cursor.execute('select available_quantity from holds where stock_id=%s', (item['stock_id'],))
        available_quantity = cursor.fetchone()['available_quantity']
        if available_quantity < item['quantity']:
            flash('OUT OF STOCK')
            break
        newQuantity = available_quantity - item['quantity']
        cursor.execute('update holds set available_quantity=%s where stock_id=%s', (newQuantity, item['stock_id'],))
    else:
        mysql.connection.commit()
        flash('PAYMENT DONE')
    cursor.close()
    return redirect('/shop')


@app.route('/logout')
def logout():
    if 'buyer_id' in session:
        session.pop('buyer_id', None)
    if 'farmer_id' in session:
        session.pop('farmer_id', None)

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
