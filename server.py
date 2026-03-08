from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import re
from curl_cffi import requests
from urllib.parse import urlparse, parse_qs

class CodePenAuthHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/verify'):
            try:
                # 1. Parse URL and Code
                query_components = parse_qs(urlparse(self.path).query)
                pen_url = query_components.get('url', [''])[0]
                code = query_components.get('code', [''])[0]

                if not pen_url:
                    result = {"success": False, "error": "No URL provided"}
                else:
                    # 2. Verify the specific Pen
                    print(f"Verifying Pen: {pen_url}")
                    r = requests.get(pen_url, impersonate="chrome120")
                    is_verified = code.lower() in r.text.lower()
                    
                    pen_list = []
                    username = "Unknown"

                    if is_verified:
                        # 3. Get Username and RSS feed for Pens
                        username = urlparse(pen_url).path.split('/')[1]
                        rss_url = f"https://codepen.io/{username}/public/feed/"
                        rss_r = requests.get(rss_url, impersonate="chrome120")
                        
                        # Find all Pen links in the RSS feed
                        links = re.findall(r'<link>(https://codepen\.io/[^/]+/pen/[^<]+)</link>', rss_r.text)
                        
                        # Format list for the extension
                        for link in list(set(links)):
                            pen_list.append({"url": link, "id": link.split('/')[-1]})
                    
                    result = {"success": is_verified, "username": username, "pens": pen_list}

                # 4. Send the successful response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                print(f"Verified {username} - Found {len(pen_list)} pens.")

            except Exception as e:
                # THIS IS THE PART PYTHON WAS MISSING
                print(f"Error: {e}")
                self.send_response(200) # Still send 200 so the browser doesn't crash
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
        else:
            # Handle serving the index.html file
            super().do_GET()

print("🚀 SERVER REPAIRED & RUNNING: http://localhost:8080")
HTTPServer(('localhost', 8080), CodePenAuthHandler).serve_forever()
