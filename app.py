from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100))
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# TMDB API Key
TMDB_API_KEY = 'd13ffdf8612413fdf3d97ca7c527606b'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/details')
def details():
    return render_template('movie-details.html')

@app.route('/recommd')
def recommd():
    return render_template('recom.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = user.email
            flash('Please login', 'success')
            return redirect('/')
        else:
            error = 'Invalid email or password'
            flash(error, 'error')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
    
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = 'Email address already exists'
            flash(error, 'error')
            return render_template('register.html')
        
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect('/login')
        
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        email = session['email']
        user = User.query.filter_by(email=email).first()
        return render_template('dashboard.html', user=user)
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'success')
    return redirect('/login')

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    movie_name = request.form['movie_name']
    tmdb_url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}'
    
    try:
        response = requests.get(tmdb_url)
        response.raise_for_status()
        data = response.json()

        recommendations = []
        poster_urls = []
        if 'results' in data:
            for movie in data['results']:
                recommendations.append(movie['title'])
                if 'poster_path' in movie:
                    poster_urls.append(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}")
                else:
                    poster_urls.append(None)

        return render_template('recom.html', recommendations=recommendations, poster_urls=poster_urls)
    
    except requests.exceptions.RequestException as e:
        error_message = "Error fetching data from TMDB API. Please try again later."
        return render_template('recom.html', error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
