#!/usr/bin/env python3
"""Tell IndexNow engines (Bing, which feeds Copilot and others; Yandex; Seznam; Naver)
that guide URLs changed. Run AFTER the change is live on www.flowai.co.nz.

  python3 scripts/indexnow.py            # every /blog/ and /glossary/ URL in sitemap.xml
  python3 scripts/indexnow.py URL [URL]  # just these
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "www.flowai.co.nz"
KEY = "552735e68fb8926010d7314520b183c9"

urls = sys.argv[1:] or [u for u in re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text())
                        if "/blog/" in u or "/glossary/" in u or "/llms" in u]
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req, timeout=20) as r:
    print(r.status, f"submitted {len(urls)} URLs")
