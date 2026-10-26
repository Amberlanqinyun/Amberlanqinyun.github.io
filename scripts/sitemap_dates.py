#!/usr/bin/env python3
"""Keeps sitemap.xml's <lastmod> true for the hand-built English pages.

Blog guides and the glossary are dated by build_blog.py from each guide's
"modified" field, and i18n.py copies every English date to its /zh/ twin.
Everything else (home, About, services, sprints, work, tools) had no source
of truth, so its dates went stale. This sets each of those to the last day
its file, or its Chinese twin, changed in git (today if it has uncommitted
edits). Run before i18n.py:
  python3 scripts/sitemap_dates.py && python3 scripts/i18n.py
"""
import datetime as dt
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.flowai.co.nz"
TODAY = dt.date.today().isoformat()


def file_of(path):
    p = path.lstrip("/")
    return ROOT / (p + "index.html" if p.endswith("/") or not p else p + ".html")


def changed(f):
    if not f.exists():
        return None
    rel = str(f.relative_to(ROOT))
    if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=ROOT).returncode:
        return TODAY
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out or None


def main():
    sm = ROOT / "sitemap.xml"
    text = sm.read_text()
    n = 0

    def fix(m):
        nonlocal n
        loc, old = m.group(1), m.group(2)
        path = loc[len(SITE):]
        if path.startswith(("/blog/", "/glossary/", "/zh/")):
            return m.group(0)
        dates = [d for d in (changed(file_of(path)), changed(file_of("/zh" + path))) if d]
        new = max(dates) if dates else old
        if new != old:
            n += 1
        return f"<loc>{loc}</loc><lastmod>{new}</lastmod>"

    text = re.sub(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", fix, text)
    sm.write_text(text)
    print(f"sitemap: {n} English page dates updated")


if __name__ == "__main__":
    main()
