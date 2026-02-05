import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def get_clean_film_url(entry):
    original_link = entry.link
    # Remove username and rewatch counters to get the base film URL
    url = re.sub(r'letterboxd\.com\/[^\/]+\/film\/', 'letterboxd.com/film/', original_link)
    url = re.sub(r'(film\/[a-z0-9-]+\/)\d+\/?$', r'\1', url)
    return url

def get_movie_details(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return "Unknown", [], []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Director - Letterboxd uses 'twitter:data1' for director
        dir_tag = soup.find('meta', attrs={'name': 'twitter:data1'})
        director = dir_tag['content'] if dir_tag else "Unknown"
        
        # Genres - Using more specific selector
        genres = [a.text for a in soup.select('div.terms.genre-list a')]
        
        # Actors - Top 3
        actors = [a.get_text() for a in soup.select('.cast-list a.text-slug')[:3]]
        
        return director, genres, actors
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return "Unknown", [], []

@app.route('/api/get-history')
def get_history():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    feed = feedparser.parse(f"https://letterboxd.com/{username}/rss/")
    
    results = []
    # Fetching the 5 most recent entries
    for entry in feed.entries[:5]:
        film_url = get_clean_film_url(entry)
        director, genres, actors = get_movie_details(film_url)
        
        # Letterboxd RSS uses specific namespaces for these fields
        results.append({
            "title": getattr(entry, 'letterboxd_filmtitle', 'Unknown'),
            "rating": getattr(entry, 'letterboxd_memberrating', None),
            "link": film_url,
            "director": director,
            "genres": genres,
            "actors": actors
        })
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)