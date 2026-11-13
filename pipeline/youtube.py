"""Завантаження на YouTube через Data API v3 (resumable upload). Лише стандартна бібліотека.

Для кожного каналу потрібен власний refresh token (бренд-акаунти). Секрети в GitHub:
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_TOKEN_<KEY>  (наприклад YT_TOKEN_EKONOMIKA)
Токени отримує tools/youtube_auth.py один раз на комп'ютері власника.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


def access_token(channel: str) -> str:
    data = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                   "refresh_token": os.environ[f"YT_TOKEN_{channel.upper()}"], "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", data=data, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def upload(channel: str, mp4: Path, title: str, description: str, tags: list[str], privacy: str = "public") -> str:
    tok = access_token(channel)
    meta = {"snippet": {"title": title[:100], "description": description[:4900], "tags": tags[:15], "categoryId": "25",
                        "defaultLanguage": "uk", "defaultAudioLanguage": "uk"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False}}
    init = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                                  data=json.dumps(meta).encode(), method="POST",
                                  headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                                           "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(mp4.stat().st_size)})
    with urllib.request.urlopen(init, timeout=60) as r:
        loc = r.headers["Location"]
    put = urllib.request.Request(loc, data=mp4.read_bytes(), method="PUT", headers={"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4"})
    with urllib.request.urlopen(put, timeout=600) as r:
        vid = json.loads(r.read())["id"]
    return f"https://youtube.com/shorts/{vid}"


def _api(channel: str, method: str, url: str, body: dict | None = None) -> dict:
    tok = access_token(channel)
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, method=method,
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    return json.loads(raw) if raw else {}


def set_public(channel: str, video_id: str) -> None:
    _api(channel, "PUT", "https://www.googleapis.com/youtube/v3/videos?part=status",
         {"id": video_id, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}})


def delete(channel: str, video_id: str) -> None:
    _api(channel, "DELETE", f"https://www.googleapis.com/youtube/v3/videos?id={video_id}")
