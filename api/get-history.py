import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS # You might need: pip install flask-cors

app = Flask(__name__)
CORS(app) # This prevents the "CORS Error" when running locally

def get_movie_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    try:
        print(f"Scraping: {url}")
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Get Director (Selector updated)
        director_tag = soup.select_one('span.directorlist a')
        director = director_tag.get_text(strip=True) if director_tag else "Unknown Director"
        
        # 2. Get Genres (Selector updated)
        genre_tags = soup.select('div#tab-details a[href*="/genre/"]')
        genres = [g.get_text(strip=True) for g in genre_tags] if genre_tags else ["Unknown Genre"]
        
        # 3. Get Actors
        actor_tags = soup.select('div.cast-list a.cast-list-link')[:3]
        actors = [a.get_text(strip=True) for a in actor_tags] if actor_tags else ["Unknown Cast"]
        
        return director, list(set(genres)), actors
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return "Error", [], []

@app.route('/api/get-history')
def get_history():
    username = request.args.get('username')
    print(f"--- Fetching for user: {username} ---")
    
    feed_url = f"https://letterboxd.com/{username}/rss/"
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        print("No entries found in RSS feed. Is the username correct?")
        return jsonify([])

    results = []
    # Test with just the first 3 movies to see if data populates
    for entry in feed.entries[:3]:
        print(f"Found movie: {entry.get('letterboxd_filmtitle', 'Unknown')}")
        
        director, genres, actors = get_movie_details(entry.link)

        results.append({
            "title": entry.get('letterboxd_filmtitle', 'Unknown'),
            "rating": entry.get('letterboxd_memberrating', None),
            "director": director,
            "genres": genres,
            "actors": actors
        })
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)