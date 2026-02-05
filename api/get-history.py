import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import re
from datetime import datetime
import time
from collections import Counter

app = Flask(__name__)

# Simple in-memory cache
# Format: { 'film_url': {'director': '...', 'genres': [...], 'actors': [...] } }
movie_cache = {}

def get_clean_film_url(entry):
    original_link = entry.link
    # Remove username/review segments and rewatch counters
    url = re.sub(r'letterboxd\.com\/[^\/]+\/film\/', 'letterboxd.com/film/', original_link)
    url = re.sub(r'(film\/[a-z0-9-]+\/)\d+\/?$', r'\1', url)
    return url

def get_movie_details(url):
    # Check cache first
    if url in movie_cache:
        return movie_cache[url]['director'], movie_cache[url]['genres'], movie_cache[url]['actors']

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return "Unknown", [], []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Director
        dir_tag = soup.find('meta', attrs={'name': 'twitter:data1'})
        director = dir_tag['content'] if dir_tag else "Unknown"
        
        # 2. Genres
        genres = [a.text for a in soup.select('div.terms.genre-list a')]
        
        # 3. Actors (Top 3)
        actors = [a.get_text() for a in soup.select('.cast-list a.text-slug')[:3]]
        
        # Save to cache
        movie_cache[url] = {
            'director': director,
            'genres': genres,
            'actors': actors
        }
        
        return director, genres, actors
    except Exception as e:
        print(f"Scraping error for {url}: {e}")
        return "Unknown", [], []

from collections import Counter

@app.route('/api/get-history')
def get_history():
    username = request.args.get('username')
    since_param = request.args.get('since')
    
    try:
        raw_rss = requests.get(f"https://letterboxd.com/{username}/rss/").text.strip()
        feed = feedparser.parse(raw_rss)
    except:
        return jsonify({"error": "Failed to fetch feed"}), 500
    
    since_date = datetime.strptime(since_param, '%Y-%m-%d') if since_param else None
    results = []
    
    for entry in feed.entries:
        pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        if since_date and pub_date < since_date:
            continue

        # Get Title and Filter Unknowns
        title = getattr(entry, 'letterboxd_filmtitle', entry.title)
        title = re.sub(r', \d{4} - ★+.*$', '', title).replace('Watched by ', '').strip()
        
        if not title or title.lower() == "unknown":
            continue

        film_url = get_clean_film_url(entry)
        director, genres, actors = get_movie_details(film_url)
        
        results.append({
            "title": title,
            "rating": getattr(entry, 'letterboxd_memberrating', None),
            "director": director,
            "genres": genres,
            "actors": actors
        })
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)