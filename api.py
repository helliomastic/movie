# routes.py

from flask import render_template, request
from app import app
import requests

# Load your TMDB API key securely from environment variables or config file
TMDB_API_KEY = 'd13ffdf8612413fdf3d97ca7c527606b'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    movie_name = request.form['movie_name']
    tmdb_url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}'
    
    try:
        response = requests.get(tmdb_url)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
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

        return render_template('index.html', recommendations=recommendations, poster_urls=poster_urls)
    
    except requests.exceptions.RequestException as e:
        error_message = "Error fetching data from TMDB API. Please try again later."
        return render_template('index.html', error=error_message)
    
    
