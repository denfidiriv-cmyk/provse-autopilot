"""Один раз на твоєму комп'ютері: отримати refresh token для кожного каналу.

1. У Google Cloud Console створи OAuth client типу «Desktop app» і скопіюй Client ID і Client secret.
2. Запусти:  python tools/youtube_auth.py <CLIENT_ID> <CLIENT_SECRET>
3. Відкриється браузер. Увійди в Google і ОБЕРИ ПОТРІБНИЙ КАНАЛ (бренд-акаунт), дозволь доступ.
4. Скрипт надрукує refresh token. Збережи його в GitHub секрет YT_TOKEN_<КАНАЛ>, напр. YT_TOKEN_EKONOMIKA.
Повтори для кожного з 7 каналів.
"""
import json, sys, urllib.parse, urllib.request, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

cid, secret = sys.argv[1], sys.argv[2]
PORT = 8765; REDIRECT = f"http://127.0.0.1:{PORT}/"
scope = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"
url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(
    {"client_id": cid, "redirect_uri": REDIRECT, "response_type": "code", "scope": scope, "access_type": "offline", "prompt": "consent select_account"})
code = {}

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code["c"] = q.get("code", [""])[0]
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
        self.wfile.write("Готово, можна закрити вкладку.".encode())
    def log_message(self, *a): pass

print("Відкриваю браузер...\n", url); webbrowser.open(url)
srv = HTTPServer(("127.0.0.1", PORT), H)
while not code.get("c"):
    srv.handle_request()
data = urllib.parse.urlencode({"code": code["c"], "client_id": cid, "client_secret": secret, "redirect_uri": REDIRECT, "grant_type": "authorization_code"}).encode()
tok = json.loads(urllib.request.urlopen("https://oauth2.googleapis.com/token", data=data).read())
at = tok["access_token"]
me = json.loads(urllib.request.urlopen(urllib.request.Request("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true", headers={"Authorization": "Bearer " + at})).read())
name = me["items"][0]["snippet"]["title"] if me.get("items") else "?"
print(f"\nКанал: {name}\nREFRESH TOKEN (поклади в секрет YT_TOKEN_<КАНАЛ>):\n{tok.get('refresh_token')}")
