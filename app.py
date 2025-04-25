from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from models.user import db

app = Flask(__name__, static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///indyfit.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
# db.init_app(app)  # Uncomment when ready to use the database

@app.route('/')
def home():
    return render_template('index.html', title='IndyFit - Fitness for Indianapolis Parks')

@app.route('/about')
def about():
    return render_template('index.html', title='About IndyFit')

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()  # Uncomment when ready to create database tables
    app.run(host='0.0.0.0', port=5000, debug=True)