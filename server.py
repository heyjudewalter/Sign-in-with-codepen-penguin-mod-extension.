# Update just the API part of your server.py
if self.path.startswith('/api/verify'):
    try:
        query_components = parse_qs(urlparse(self.path).query)
        pen_url = query_components.get('url', [''])[0]
        code = query_components.get('code', [''])[0]

        # 1. Verify the code exists in the Pen
        r = requests.get(pen_url, impersonate="chrome120")
        is_verified = code.lower() in r.text.lower()
        
        # 2. Get the username for the extension to use
        username = urlparse(pen_url).path.split('/')[1]
        
        # 3. Get the RSS feed (This is much more reliable for a list of pens)
        rss_url = f"https://codepen.io/{username}/public/feed/"
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Return the verification status AND the RSS link
        result = {
            "success": is_verified, 
            "username": username,
            "rss": rss_url
        }
        self.wfile.write(json.dumps(result).encode())
