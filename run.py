#!/usr/bin/env python3
"""LLMWiki local viewer server.

Port resolution, highest priority first:

    --port 8011            explicit flag
    WIKI_PORT=8011         environment
    .llmwiki-port          a file in the wiki root containing the number
    8001                   default

If the chosen port is taken the server still starts on the next free one, but
says so loudly. Silent drift is the bug this ordering exists to fix: several
wikis on one machine all defaulted to 8001, so whichever started first won it
and the rest landed on 8002, 8003 — with nothing in the URL to say which wiki
you were actually looking at.
"""
import argparse
import http.server
import os
import re
import socket
import socketserver
import sys
import threading
import time
import webbrowser

DEFAULT_PORT = 8001
PORT_FILE = '.llmwiki-port'


def port_is_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except socket.error:
            return False


def find_free_port(start_port):
    port = start_port
    while not port_is_free(port):
        port += 1
    return port


def preferred_port(wiki_root, cli_port):
    """Returns (port, source). The source is shown in the banner."""
    if cli_port:
        return cli_port, '--port'

    env = os.environ.get('WIKI_PORT', '').strip()
    if env:
        try:
            return int(env), 'WIKI_PORT'
        except ValueError:
            print(f"⚠️  Ignoring WIKI_PORT={env!r} — not a number.")

    path = os.path.join(wiki_root, PORT_FILE)
    if os.path.exists(path):
        try:
            with open(path, encoding='utf-8') as f:
                # Allow a trailing comment so the file can explain itself.
                raw = f.readline().split('#')[0].strip()
            return int(raw), PORT_FILE
        except (ValueError, OSError):
            print(f"⚠️  Ignoring {PORT_FILE} — no port number could be read from it.")

    return DEFAULT_PORT, 'default'


def wiki_name(wiki_root):
    """The <title> from index.html, so the banner names the wiki, not just its path."""
    try:
        with open(os.path.join(wiki_root, 'index.html'), encoding='utf-8') as f:
            match = re.search(r'<title>(.*?)</title>', f.read(), re.S | re.I)
        if match:
            return ' '.join(match.group(1).split())
    except OSError:
        pass
    return os.path.basename(wiki_root)


def main():
    parser = argparse.ArgumentParser(description='Serve this LLMWiki locally.')
    parser.add_argument('--port', type=int, help='Port to serve on.')
    parser.add_argument('--no-browser', action='store_true',
                        help='Do not open a browser window.')
    args = parser.parse_args()

    engine_dir = os.path.dirname(os.path.abspath(__file__))
    wiki_root = os.path.abspath(os.path.join(engine_dir, '..'))

    wanted, source = preferred_port(wiki_root, args.port)
    port = find_free_port(wanted)
    url = f"http://localhost:{port}"
    name = wiki_name(wiki_root)

    print("-" * 60)
    print("⚡ Starting LLMWiki Local Server...")
    print(f"📛 Wiki:      {name}")
    print(f"📂 Wiki Root: {wiki_root}")
    print(f"🌐 URL:       {url}")
    if port != wanted:
        print("-" * 60)
        print(f"⚠️  Port {wanted} (from {source}) is in use — most likely another")
        print(f"    wiki is serving it. Started on {port} instead.")
        print(f"    Pin this wiki's port with a {PORT_FILE} file or --port,")
        print("    otherwise the URL does not tell you which wiki you opened.")
    elif source == 'default':
        print("ℹ️  Using the default port. Running more than one wiki? Pin each")
        print(f"    to its own port with a {PORT_FILE} file.")
    print("-" * 60)

    os.chdir(wiki_root)

    if not args.no_browser:
        def open_browser():
            time.sleep(0.5)
            webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()

    class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
        """Serve fresh every time. The client is a single-page app that fetches
        the markdown at runtime, so any browser caching shows stale wiki content.
        Force no-store on every response so edits appear on a normal reload."""
        def end_headers(self):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            super().end_headers()

    handler = NoCacheHandler
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            sys.exit(0)


if __name__ == '__main__':
    main()
