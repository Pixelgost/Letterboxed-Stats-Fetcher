import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def get_clean_film_url(entry):
    """
    Converts 'https://letterboxd.com/username/film/title/' 
    to 'https://letterboxd.com/film/title/'
    """
    original_link = entry.link
    # Regex to remove the username part of the path
    # Matches letterboxd.com/ [any-username] /film/
    clean_url = re.sub(r'letterboxd\.com\/[^\/]+\/film\/', 'letterboxd.com/film/', original_link)
    return clean_url

def get_movie_details(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200: return "Unknown", [], []
        print(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Director - specific meta/span check
        dir_tag = soup.select_one('meta[name="twitter:data1"]') 
        # Letterboxd often puts the director in a twitter meta tag 'data1'
        director = dir_tag['content'] if dir_tag else "Unknown"
        
        if director == "Unknown":
            # Fallback to standard selector
            dir_link = soup.select_one('span.directorlist a')
            director = dir_link.get_text() if dir_link else "Unknown"

        # 2. Genres
        genre_links = soup.select('div#tab-details a[href*="/genre/"]')
        genres = list(set([g.get_text(strip=True) for g in genre_links]))
        
        # 3. Actors
        actor_links = soup.select('.cast-list a.cast-list-link')[:3]
        actors = [a.get_text(strip=True) for a in actor_links]
        
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