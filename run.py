#!/usr/bin/env python3
import socket
import sys
import os
import webbrowser
import time
import http.server
import socketserver
import threading

def find_free_port(start_port=8001):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except socket.error:
                port += 1

def main():
    engine_dir = os.path.dirname(os.path.abspath(__file__))
    wiki_root = os.path.abspath(os.path.join(engine_dir, '..'))
    
    port = find_free_port(8001)
    url = f"http://localhost:{port}"
    
    print("-" * 50)
    print("⚡ Starting LLMWiki Local Server...")
    print(f"📂 Wiki Root: {wiki_root}")
    print(f"🌐 URL:       {url}")
    print("-" * 50)
    
    # Change working dir to wiki root to serve it
    os.chdir(wiki_root)
    
    def open_browser():
        time.sleep(0.5)
        webbrowser.open(url)
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run python HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            sys.exit(0)

if __name__ == '__main__':
    main()
