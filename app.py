from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'davyee.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Set the path for image uploads
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

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
                    description="Samsung, 300L", image_file="fridge.jpg")
        ]
        db.session.bulk_save_objects(sample_items)
        db.session.commit()

# --- ROUTES ---
@app.route('/')
def home():
    # Search Logic: Look for 'search' keyword in the URL
    search_query = request.args.get('search')
    if search_query:
        # Filter products by name or category based on search
        products = Product.query.filter(
            (Product.name.contains(search_query)) | 
            (Product.category.contains(search_query))
        ).all()
    else:
        products = Product.query.all()
    
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)