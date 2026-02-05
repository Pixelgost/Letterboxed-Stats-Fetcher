from http.server import BaseHTTPRequestHandler
import feedparser
import json
from urllib.parse import urlparse, parse_qs
from dateutil import parser

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        username = query.get('username', [None])[0]
        since_date_str = query.get('since', [None])[0]

        if not username:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Username is required")
            return

        # Parse the 'since' date provided by frontend (e.g., "2023-01-01")
        since_date = parser.parse(since_date_str) if since_date_str else None

        rss_url = f"https://letterboxd.com/{username}/rss/"
        feed = feedparser.parse(rss_url)
        
        filtered_history = []
        for entry in feed.entries:
            # Letterboxd dates are usually in entry.published
            entry_date = parser.parse(entry.published) if hasattr(entry, 'published') else None
            
            # Filter logic: Keep if no date was provided OR if entry is newer than 'since'
            if not since_date or (entry_date and entry_date.replace(tzinfo=None) >= since_date.replace(tzinfo=None)):
                # Convert the entry object to a plain dictionary to send everything
                filtered_history.append(dict(entry))

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') 
        self.end_headers()
        self.wfile.write(json.dumps(filtered_history).encode('utf-8'))