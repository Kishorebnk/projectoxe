from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# from flask_mysqldb import MySQL
import os
import mysql.connector
app = Flask(__name__)
mydb = mysql.connector.connect(host="localhost",port=3306,  user="root", password="nanda@12",db='oxecure')
app.secret_key = "ba6354d1687d0d64876ee550b71bc947"
# Default Admin Credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password@123"

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Products Page - Fetch products from DB
@app.route('/products')
def products():
    cur = mydb.cursor()
    cur = mydb.cursor(dictionary=True)
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    print(products)
    return render_template('products.html', products=products)

# Admin Login Page
@app.route('/admin')
def admin():
    return render_template('admin.html')

# Admin Login Logic
@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin'] = True
        return redirect(url_for('add_products'))
    else:
        return "Invalid Credentials! <a href='/admin'>Try Again</a>"

# Add Products Page (Only for Admin)
@app.route('/add_products')
def add_products():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    
    cur = mydb.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    return render_template('addproducts.html', products=products)

# Add Product to Database
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'admin' not in session:
        return redirect(url_for('admin'))

    generic_name= request.form['generic_name']
    doses_form = request.form['doses_form']
    strength= request.form['strength']
   

    cur = mydb.cursor()
    cur.execute("INSERT INTO products (generic_name,doses_form,strength) VALUES (%s, %s, %s)", (generic_name,doses_form,strength))
    mydb.commit()
    cur.close()

    return redirect(url_for('add_products'))

# Edit Product
@app.route('/edit_product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    data = request.json
    generic_name = data.get("generic_name")
    doses_form = data.get("doses_form")
    strength = data.get("strength")
    try:
        cur=mydb.cursor()
        cur.execute("""
            UPDATE products 
            SET generic_name=%s, doses_form=%s, strength=%s 
            WHERE id=%s
        """, (generic_name, doses_form, strength, product_id))
        mydb.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("Error updating product:", str(e))
        return jsonify({"success": False, "error": str(e)})

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        cur=mydb.cursor()
        cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
        mydb.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("Error deleting product:", str(e))
        return jsonify({"success": False, "error": str(e)})

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
