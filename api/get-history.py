import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

def get_movie_details(url):
    try:
        # We add a timeout so the scraper doesn't hang forever
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Letterboxd specific selectors
        director = soup.find('span', {'class': 'directorlist'})
        director_text = director.get_text(strip=True) if director else "Unknown"
        
        # Extract Genres from the 'tab-details' section
        genre_links = soup.select('a[href*="/genre/"]')
        genres = list(set([g.get_text(strip=True) for g in genre_links])) if genre_links else ["Unknown"]
        
        # Extract Actors
        actor_links = soup.select('.cast-list .cast-list-link')[:3]
        actors = [a.get_text(strip=True) for a in actor_links] if actor_links else ["Unknown"]
        
        return director_text, genres, actors
    except Exception as e:
        print(f"Scraping error for {url}: {e}")
        return "Unknown", ["Unknown"], ["Unknown"]

@app.route('/api/get-history')
def get_history():
    username = request.args.get('username')
    since_date = request.args.get('since')
    
    if not username:
        return jsonify({"error": "Username is required"}), 400

    feed_url = f"https://letterboxd.com/{username}/rss/"
    feed = feedparser.parse(feed_url)
    
    results = []
    # LIMITING TO 10 RECENT MOVIES to prevent timeout during scraping
    entries = feed.entries[:10] 

    for entry in entries:
        watch_date = getattr(entry, 'letterboxd_watched_date', None)
        if since_date and watch_date and watch_date < since_date:
            continue

        # Get the extra data
        director, genres, actors = get_movie_details(entry.link)

        results.append({
            "title": entry.letterboxd_filmtitle,
            "rating": getattr(entry, 'letterboxd_memberrating', None),
            "date": watch_date,
            "director": director,
            "genres": genres,
            "actors": actors
        })
        # Small sleep to be polite to Letterboxd servers
        time.sleep(0.1)
    
    return jsonify(results)