import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import re

app = Flask(__name__)


def get_clean_film_url(entry):
    original_link = entry.link
    # Step 1: Remove the username segment
    # From: https://letterboxd.com/username/film/slug/
    # To:   https://letterboxd.com/film/slug/
    url = re.sub(r'letterboxd\.com\/[^\/]+\/film\/', 'letterboxd.com/film/', original_link)
    
    # Step 2: Remove trailing rewatch counter (e.g., /1/)
    # We look for a slash, followed by digits, followed by a trailing slash
    # The [a-z0-9-]+ ensures we are looking at a film slug first
    url = re.sub(r'(film\/[a-z0-9-]+\/)\d+\/?$', r'\1', url)
    
    return url

def get_movie_details(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200: return "Unknown", [], []
        print(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        dir_tag = soup.find('meta', attrs={'name': 'twitter:data1'})
        director = dir_tag['content'] if dir_tag else "Unknown"
        
        # 2. Genres (Pulling from the script tags or details)
        # Finding genres in the provided HTML: Thriller, Drama
        genres = [a.text for a in soup.select('a[href*="/genre/"]')]
        
        # 3. Top 3 Actors (Using the text-slug class found in your file)
        actors = [a.get_text() for a in soup.select('.cast-list a.text-slug')[:3]]
        
        return director, genres, actors
        
    except:
        return "Unknown", [], []

@app.route('/api/get-history')
def get_history():
    username = request.args.get('username')
    feed = feedparser.parse(f"https://letterboxd.com/{username}/rss/")
    
    results = []
    # Limit to 5 for speed/stability during testing
    for entry in feed.entries[:5]:
        film_url = get_clean_film_url(entry)
        print(film_url )
        director, genres, actors = get_movie_details(film_url)
        
        results.append({
            "title": entry.letterboxd_filmtitle,
            "rating": getattr(entry, 'letterboxd_memberrating', None),
            "director": director,
            "genres": genres,
            "actors": actors
        })
    
    return jsonify(results)