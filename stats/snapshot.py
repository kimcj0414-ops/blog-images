"""Save each blog's all-time pageview total once per US-Eastern day (the "midnight baseline").

The footer counter on every blog shows  Today = live total - this baseline.
The live total comes from each blog's public Blogger "Blog Stats" gadget, so no secrets are needed.
Runs hourly from .github/workflows/stats.yml; only writes when the New York date changes
or a blog is missing.
"""
import datetime
import json
import os
import re
import urllib.request
from zoneinfo import ZoneInfo

BLOGS = [
    "koreabeforethebell.blogspot.com",
    "betweenseoulanddc.blogspot.com",
    "subtitlesnotincluded.blogspot.com",
    "seoulspoonblog.blogspot.com",
    "debatesintheafterlife.blogspot.com",
    "korealifemanual.blogspot.com",
]
PATH = os.path.join(os.path.dirname(__file__), "baseline.json")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/json"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def total_for(host):
    html = get("https://" + host + "/")
    m = re.search(r"'statsUrl':\s*'([^']+)'", html)
    if not m:
        return None
    url = m.group(1).replace("\\x3d", "=").replace("\\x26", "&")
    if url.startswith("//"):
        url = "https:" + url
    return int(json.loads(get(url))["total"])


def main():
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    try:
        data = json.load(open(PATH))
    except Exception:
        data = {}
    if data.get("date") != today:
        data = {"date": today, "timezone": "America/New_York", "totals": {}}
    changed = False
    for host in BLOGS:
        if host in data["totals"]:
            continue
        try:
            t = total_for(host)
        except Exception as e:
            print("skip", host, e)
            continue
        if t is not None:
            data["totals"][host] = t
            changed = True
            print(host, t)
    if changed or not os.path.exists(PATH):
        json.dump(data, open(PATH, "w"), indent=1)
        print("saved", PATH)


if __name__ == "__main__":
    main()
