import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import re
from datetime import datetime
import time

app = Flask(__name__)

movie_cache = {}

def get_movie_details(url):
    if url in movie_cache:
        return movie_cache[url]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    try:
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code != 200:
            return {"director": "Unknown", "genres": [], "actors": []}
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Twitter metadata is a clever way to get the director quickly!
        dir_tag = soup.find('meta', attrs={'name': 'twitter:data1'})
        director = dir_tag['content'] if dir_tag else "Unknown"
        
        genres = []
        # Attempt to find genres in the JavaScript ramp tags found in your HTML
        script_tag = soup.find('script', string=re.compile(r'window\.ramp\.custom_tags'))
        if script_tag:
            # Extract tags like 'thriller', 'drama' from the script block
            matches = re.findall(r"'(.*?)'", script_tag.string)
            # Filter out non-genre strings like film IDs or 'intl_true'
            genres = [m for m in matches if m and not m.endswith('G') and m != 'intl_true']
        
        # Fallback: search for links containing /genre/ in the URL
        if not genres:
            genres = list(set([a.text.strip() for a in soup.find_all('a', href=re.compile(r'/genre/'))]))
        actors = [a.get_text() for a in soup.select('.cast-list a.text-slug')[:3]]
        
        data = {"director": director, "genres": genres, "actors": actors}
        movie_cache[url] = data
        return data
    except Exception:
        return {"director": "Unknown", "genres": [], "actors": []}

@app.route('/api/get-history')
def get_history():
    username = request.args.get('username')
    since_param = request.args.get('since')
    
    if not username:
        return jsonify({"error": "Username required"}), 400

    try:
        rss_url = f"https://letterboxd.com/{username}/rss/"
        response = requests.get(rss_url, timeout=5)
        feed = feedparser.parse(response.text.strip())
    except Exception as e:
        return jsonify({"error": f"Failed to fetch feed: {str(e)}"}), 500
    
    since_date = None
    if since_param:
        try:
            since_date = datetime.strptime(since_param, '%Y-%m-%d')
        except ValueError:
            pass

    results = []
    
    # FIX: Added [:10] to the slice
    for entry in feed.entries:
        try:
            pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        except:
            pub_date = datetime.now()

        if since_date and pub_date < since_date:
            continue

        # Clean Title Logic
        title = getattr(entry, 'letterboxd_filmtitle', entry.title)
        print(title)
        title = re.sub(r', \d{4} - ★+.*$', '', title).replace('Watched by ', '').strip()
        
        if not title or title.lower() == "unknown":
            continue

        # URL Cleaning
        film_url = re.sub(r'letterboxd\.com\/[^\/]+\/film\/', 'letterboxd.com/film/', entry.link)
        film_url = re.sub(r'(film\/[a-z0-9-]+\/)\d+\/?$', r'\1', film_url)
        
        details = get_movie_details(film_url)
        
        results.append({
            "title": title,
            "user": username,
            "rating": getattr(entry, 'letterboxd_memberrating', None),
            "date": pub_date.strftime('%Y-%m-%d'),
            "director": details['director'],
            "genres": details['genres'],
            "actors": details['actors']
        })
    print(results)
    return jsonify(results)
