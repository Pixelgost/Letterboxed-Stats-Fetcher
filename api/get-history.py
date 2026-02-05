import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

def get_movie_details(url):
    try:
        # Strict timeout of 2 seconds per movie to avoid 500 error
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=2)
        if response.status_code != 200:
            return "Unknown", [], []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Director
        director_tag = soup.find('span', {'class': 'directorlist'})
        director = director_tag.get_text(strip=True) if director_tag else "Unknown"
        
        # Genres - Updated selector to be more robust
        genre_links = soup.select('a[href*="/genre/"]')
        genres = list(set([g.get_text(strip=True) for g in genre_links])) if genre_links else []
        
        # Actors
        actor_links = soup.select('.cast-list .cast-list-link')[:3]
        actors = [a.get_text(strip=True) for a in actor_links] if actor_links else []
        
        return director, genres, actors
    except Exception:
        return "Unknown", [], []

@app.route('/api/get-history')
def get_history():
    try:
        username = request.args.get('username')
        since_date = request.args.get('since', '')
        
        feed_url = f"https://letterboxd.com/{username}/rss/"
        feed = feedparser.parse(feed_url)
        
        if not feed.entries:
            return jsonify([])

        results = []
        # LIMIT to 5 entries initially to test if it bypasses the 500 error
        # Scraping is slow; 5 entries = ~5-7 seconds
        for entry in feed.entries[:5]:
            watch_date = getattr(entry, 'letterboxd_watched_date', '')
            if since_date and watch_date and watch_date < since_date:
                continue

            # This is the slow part
            director, genres, actors = get_movie_details(entry.link)

            results.append({
                "title": getattr(entry, 'letterboxd_filmtitle', 'Unknown'),
                "rating": getattr(entry, 'letterboxd_memberrating', None),
                "date": watch_date,
                "director": director,
                "genres": genres,
                "actors": actors
            })
        
        return jsonify(results)
        
    except Exception as e:
        # This catches the error and returns it as JSON so your JS doesn't crash
        return jsonify({"error": str(e)}), 500