from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# --- CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'davyee.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Ensure the upload folder exists
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# --- MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.String(20), default="Contact for Price")
    description = db.Column(db.String(200))
    image_file = db.Column(db.String(100), default='default.jpg')

# --- DATABASE INITIALIZATION ---
with app.app_context():
    db.create_all()
    if not Product.query.first():
        sample_items = [
            Product(name="55-inch Smart TV", category="Electronics", price="KSh 45,000", 
                    description="Excellent condition, UHD", image_file="tv.jpg"),
            Product(name="L-Shaped Sofa", category="Living Room", price="KSh 35,000", 
                    description="Grey fabric, 5-seater", image_file="sofa.jpg"),
            Product(name="6x6 King Size Bed", category="Bedroom", price="KSh 25,000", 
                    description="Hardwood frame", image_file="bed.jpg"),
            Product(name="Double Door Fridge", category="Kitchen", price="KSh 50,000", 
                    description="Samsung, 300L", image_file="fridge.jpg"),
            Product(name="Gas Cylinder", category="Kitchen", price="KSh 4,500", 
                    description="13kg Full with Burner", image_file="gas.jpg")
        ]
        db.session.bulk_save_objects(sample_items)
        db.session.commit()

# --- ROUTES ---

# Home Page
@app.route('/')
def home():
    search_query = request.args.get('search')
    if search_query:
        products = Product.query.filter(
            (Product.name.contains(search_query)) | 
            (Product.category.contains(search_query))
        ).all()
    else:
        products = Product.query.all()
    return render_template('index.html', products=products)

# Admin Page: Add Product
@app.route('/admin/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        description = request.form.get('description')
        
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = 'default.jpg'
            
        new_item = Product(name=name, category=category, price=price, 
                          description=description, image_file=filename)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('home'))
            
    return render_template('add_product.html')

# Admin Page: Delete Product
@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('home'))

# --- PORT FIX FOR RENDER ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
