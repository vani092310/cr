from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import pickle
import numpy as np

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

# Home page
@app.route('/')
def home():
    return render_template('gaya.html')

@app.route('/abstract')
def abstract():
    return render_template('abstract.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect(url_for('user_home'))
        else:
            return render_template('login.html', error='Invalid user')

    return render_template('login.html')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

# Home page after login
@app.route('/user_home')
def user_home():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            return render_template('main.html', user=user)
        else:
            flash('User not found. Please log in again.')
            return redirect(url_for('login'))
    else:
        flash('Session expired. Please log in again.')
        return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/index')
def index():
    return render_template('index.html')

# Load the models and scalers
model = pickle.load(open('RandomForest_model.pkl', 'rb'))
sc = pickle.load(open('standscaler.pkl', 'rb'))
mx = pickle.load(open('minmaxscaler.pkl', 'rb'))

@app.route('/recommend', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            N = float(request.form['Nitrogen'])
            P = float(request.form['Phosporus'])
            K = float(request.form['Potassium'])
            temp = float(request.form['Temperature'])
            humidity = float(request.form['Humidity'])
            ph = float(request.form['pH'])
            rainfall = float(request.form['Rainfall'])

            feature_list = [N, P, K, temp, humidity, ph, rainfall]
            single_pred = np.array(feature_list).reshape(1, -1)
            mx_features = mx.transform(single_pred)
            sc_mx_features = sc.transform(mx_features)

            prediction = model.predict(sc_mx_features)

            crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                         8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                         14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                         19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}

            if prediction[0] in crop_dict:
                crop = crop_dict[prediction[0]]
                result = "{} is the best crop to be cultivated right there".format(crop)
            else:
                result = "Sorry, we could not determine the best crop to be cultivated with the provided data."

            return render_template('cropresult.html', result=result)
        except ValueError:
            flash("Please enter valid numerical values for all fields.")
            return render_template('index.html')
        except Exception as e:
            flash(f"An error occurred while making the prediction. Please try again. Error: {e}")
            return render_template('index.html')
    else:
        return render_template('index.html')
@app.route('/conclusion')
def conclusion():
    return render_template('con.html')  # Replace 'conclusion.html' with your actual conclusion page template


if __name__ == "__main__":
    app.run(debug=True)
