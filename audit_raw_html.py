#!/usr/bin/env python3
"""
audit_raw_html.py: see a page the way non-JS crawlers (GPTBot, ClaudeBot, PerplexityBot,
OAI-SearchBot, etc.) see it. Python stdlib only.

Usage:
    python audit_raw_html.py https://example.com/ [https://example.com/pricing ...]
    python audit_raw_html.py --json https://example.com/

Exit code: 0 = no FAIL, 1 = at least one FAIL, 2 = usage/network error.
"""
import json
import re
import sys
import urllib.error
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

UAS = {
    "browser": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
    "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "OAI-SearchBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot",
    "ClaudeBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "PerplexityBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
}

ROBOTS_BOTS = [
    # (token, category)
    ("Googlebot", "search"), ("Bingbot", "search"),
    ("OAI-SearchBot", "ai-search"), ("ChatGPT-User", "ai-user"),
    ("Claude-SearchBot", "ai-search"), ("Claude-User", "ai-user"),
    ("PerplexityBot", "ai-search"), ("Perplexity-User", "ai-user"),
    ("GPTBot", "training"), ("ClaudeBot", "training"),
    ("Google-Extended", "training"), ("CCBot", "training"),
]

SPA_ROOT_IDS = {"root", "app", "__next", "__nuxt", "svelte", "q-app"}
MIN_WORDS_OK = 150  # below this the page is likely a shell or thin


def fetch(url, ua, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(3_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
            return r.status, r.geturl(), dict(r.headers), body
    except urllib.error.HTTPError as e:
        try:
            body = e.read(200_000).decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, url, dict(e.headers or {}), body
    except Exception as e:  # network error
        return None, url, {}, str(e)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.meta = {}
        self.links = []
        self.canonical = None
        self.hreflang = []
        self.lang = None
        self.h1 = []
        self._in_h1 = False
        self._h1_buf = ""
        self.jsonld_raw = []
        self._in_jsonld = False
        self._jsonld_buf = ""
        self._skip = 0  # inside script/style/noscript/template
        self.text_parts = []
        self.anchors = []
        self.root_ids = []
        self.scripts = 0
        self.img_no_alt = 0

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "link":
            rel = a.get("rel", "").lower()
            if "canonical" in rel:
                self.canonical = a.get("href")
            if "alternate" in rel and a.get("hreflang"):
                self.hreflang.append((a.get("hreflang"), a.get("href")))
        elif tag == "h1":
            self._in_h1 = True
            self._h1_buf = ""
        elif tag == "script":
            self.scripts += 1
            if "ld+json" in a.get("type", "").lower():
                self._in_jsonld = True
                self._jsonld_buf = ""
            else:
                self._skip += 1
        elif tag in ("style", "noscript", "template", "svg"):
            self._skip += 1
        elif tag == "a" and a.get("href"):
            self.anchors.append(a["href"])
        elif tag == "div" and a.get("id", "").lower() in SPA_ROOT_IDS:
            self.root_ids.append(a["id"])
        elif tag == "img" and "alt" not in a:
            self.img_no_alt += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
            self.h1.append(self._h1_buf.strip())
        elif tag == "script":
            if self._in_jsonld:
                self.jsonld_raw.append(self._jsonld_buf)
                self._in_jsonld = False
            elif self._skip:
                self._skip -= 1
        elif tag in ("style", "noscript", "template", "svg") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_jsonld:
            self._jsonld_buf += data
            return
        if self._in_title:
            self.title += data
            return
        if self._skip:
            return
        if self._in_h1:
            self._h1_buf += data
        self.text_parts.append(data)


def jsonld_types(raw_blocks):
    types, errors = [], 0

    def walk(node):
        if isinstance(node, dict):
            t = node.get("@type")
            if t:
                types.extend(t if isinstance(t, list) else [t])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for raw in raw_blocks:
        try:
            walk(json.loads(raw))
        except Exception:
            errors += 1
    return types, errors


def audit_url(url):
    findings = []  # (level, message)

    def add(level, msg):
        findings.append((level, msg))

    status, final, headers, html = fetch(url, UAS["OAI-SearchBot"])
    if status is None:
        return {"url": url, "error": html, "findings": [("FAIL", f"Network error: {html}")]}

    # Compare status across UAs (CDN/WAF blocking detection)
    ua_status = {"OAI-SearchBot": status}
    for name in ("browser", "Googlebot", "ClaudeBot", "PerplexityBot"):
        s, _, _, _ = fetch(url, UAS[name])
        ua_status[name] = s
    blocked = [k for k, v in ua_status.items() if k != "browser" and v != ua_status["browser"]]
    if blocked:
        add("FAIL", f"Different HTTP status per user-agent {ua_status}. CDN/WAF likely blocking: {', '.join(blocked)}")
    if status != 200:
        add("FAIL", f"HTTP {status} for AI crawler UA")

    xrt = headers.get("X-Robots-Tag") or headers.get("x-robots-tag")
    if xrt and "noindex" in xrt.lower():
        add("FAIL", f"X-Robots-Tag header: {xrt}")

    p = PageParser()
    try:
        p.feed(html)
    except Exception as e:
        add("WARN", f"HTML parse issue: {e}")

    text = re.sub(r"\s+", " ", " ".join(p.text_parts)).strip()
    words = len(text.split())
    if words < 50:
        add("FAIL", f"Only {words} visible words in raw HTML. Page is invisible to non-JS AI crawlers"
            + (f" (SPA root div: #{p.root_ids[0]})" if p.root_ids else ""))
    elif words < MIN_WORDS_OK:
        add("WARN", f"Thin raw HTML: {words} visible words")
    else:
        add("PASS", f"{words} visible words in raw HTML")

    title = p.title.strip()
    if not title:
        add("FAIL", "Missing <title>")
    else:
        lvl = "PASS" if 15 <= len(title) <= 65 else "WARN"
        add(lvl, f"Title ({len(title)} chars): {title}")

    desc = p.meta.get("description", "")
    if not desc:
        add("FAIL", "Missing meta description")
    else:
        lvl = "PASS" if 70 <= len(desc) <= 160 else "WARN"
        add(lvl, f"Meta description ({len(desc)} chars){' will be truncated' if len(desc) > 160 else ''}")

    robots_meta = p.meta.get("robots", "")
    if "noindex" in robots_meta.lower():
        add("FAIL", f"meta robots: {robots_meta}")

    if not p.canonical:
        add("WARN", "No canonical link")
    else:
        cabs = urljoin(final, p.canonical)
        same = urlparse(cabs)._replace(fragment="").geturl().rstrip("/") == urlparse(final)._replace(fragment="", query="").geturl().rstrip("/")
        add("PASS" if same else "WARN", f"Canonical: {cabs}{'' if same else ' (differs from fetched URL, check intent)'}")

    h1s = [h for h in p.h1 if h]
    if not h1s:
        add("FAIL", "No <h1> in raw HTML")
    elif len(h1s) > 1:
        add("WARN", f"{len(h1s)} <h1> tags: {h1s[:3]}")
    else:
        add("PASS", f"H1: {h1s[0][:100]}")

    add("PASS" if p.lang else "WARN", f"<html lang>: {p.lang or 'missing'}")

    if p.hreflang:
        codes = [c for c, _ in p.hreflang]
        add("PASS" if "x-default" in codes else "WARN", f"hreflang: {codes}")

    types, errs = jsonld_types(p.jsonld_raw)
    if errs:
        add("FAIL", f"{errs} JSON-LD block(s) failed to parse")
    if types:
        add("PASS", f"JSON-LD types: {sorted(set(types))}")
        if "FAQPage" in types:
            add("INFO", "FAQPage present: valid, but Google retired FAQ rich results on 2026-05-07")
        if "HowTo" in types:
            add("INFO", "HowTo present: no Google rich result on any surface")
    else:
        add("WARN", "No JSON-LD in raw HTML")

    host = urlparse(final).netloc
    internal = {urljoin(final, h).split("#")[0] for h in p.anchors
                if urlparse(urljoin(final, h)).netloc == host}
    add("PASS" if len(internal) >= 3 else "WARN", f"{len(internal)} internal <a href> links in raw HTML")

    for key in ("og:title", "og:description", "og:image"):
        if key not in p.meta:
            add("WARN", f"Missing {key}")
    vp = p.meta.get("viewport", "")
    if "maximum-scale=1" in vp.replace(" ", "") or "user-scalable=no" in vp.replace(" ", ""):
        add("WARN", f"Viewport blocks zoom (accessibility): {vp}")
    if p.img_no_alt:
        add("WARN", f"{p.img_no_alt} <img> without alt attribute")

    return {"url": url, "final_url": final, "status_by_ua": ua_status, "words": words,
            "findings": findings}


def audit_site(origin):
    findings = []
    robots_url = urljoin(origin, "/robots.txt")
    status, _, _, body = fetch(robots_url, UAS["browser"])
    sitemaps = []
    if status != 200:
        findings.append(("WARN", f"robots.txt returned {status}: every bot is allowed by default, but there is no Sitemap line"))
    else:
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(body.splitlines())
        home = urljoin(origin, "/")
        for token, cat in ROBOTS_BOTS:
            ok = rp.can_fetch(token, home)
            if not ok and cat in ("search", "ai-search", "ai-user"):
                findings.append(("FAIL", f"robots.txt blocks {token} ({cat}) from /"))
            elif not ok:
                findings.append(("INFO", f"robots.txt blocks {token} ({cat}): training opt-out, doesn't affect AI search"))
            else:
                findings.append(("PASS", f"robots.txt allows {token} ({cat})"))
        sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", body)
        if not rp.can_fetch("SomeUnlistedBot", home):
            findings.append(("WARN", "robots.txt blocks all unlisted bots from / (User-agent: * Disallow: /). Leftover staging block?"))
    if not sitemaps:
        sitemaps = [urljoin(origin, "/sitemap.xml")]
    for sm in sitemaps[:3]:
        s, _, _, sbody = fetch(sm, UAS["browser"])
        if s == 200 and ("<urlset" in sbody or "<sitemapindex" in sbody):
            n = sbody.count("<loc>")
            findings.append(("PASS", f"Sitemap {sm}: {n} <loc> entries"))
        else:
            findings.append(("WARN", f"Sitemap {sm} missing or invalid (HTTP {s})"))
    llms_s, _, _, _ = fetch(urljoin(origin, "/llms.txt"), UAS["browser"])
    findings.append(("INFO", f"llms.txt: {'present' if llms_s == 200 else 'absent'} (no measurable effect on AI search as of 2026)"))
    return {"origin": origin, "findings": findings}


def main(argv):
    as_json = "--json" in argv
    urls = [a for a in argv if not a.startswith("--")]
    if not urls:
        print(__doc__)
        return 2
    origins = sorted({f"{urlparse(u).scheme}://{urlparse(u).netloc}" for u in urls})
    site_reports = [audit_site(o) for o in origins]
    page_reports = [audit_url(u) for u in urls]

    any_fail = any(l == "FAIL" for r in site_reports + page_reports for l, _ in r["findings"])
    if as_json:
        print(json.dumps({"site": site_reports, "pages": page_reports}, indent=2, ensure_ascii=False))
    else:
        icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌", "INFO": "ℹ️ "}
        for r in site_reports:
            print(f"\n## Site: {r['origin']}")
            for l, m in r["findings"]:
                print(f"{icon[l]} {m}")
        for r in page_reports:
            print(f"\n## Page: {r['url']}")
            for l, m in sorted(r["findings"], key=lambda x: ["FAIL", "WARN", "INFO", "PASS"].index(x[0])):
                print(f"{icon[l]} {m}")
        print("\nResult:", "FAIL: fix blockers first" if any_fail else "No blockers found")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
