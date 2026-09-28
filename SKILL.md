---
name: seo-ai-visibility
description: Technical SEO and AI-search visibility (GEO/AEO) for public web pages — making sure Google, Bing, and AI crawlers (ChatGPT, Claude, Perplexity, Copilot, Gemini) can read, index, and cite a site. Use this skill whenever building, reviewing, or deploying any public-facing page, marketing site, landing page, docs site, or the public parts of a SaaS/booking app; whenever the user mentions SEO, rankings, Google, "AI search", being cited by ChatGPT/Claude/Perplexity, crawlers, robots.txt, sitemap, meta tags, JSON-LD/schema, llms.txt, SSR vs SPA, prerendering, hreflang, or Core Web Vitals; and before shipping any React/Vite/SPA front end that has pages meant to be found by search. Trigger even if the user only says "make the site findable" or "why doesn't the site show up".
---

# SEO + AI visibility for coding agents

Evidence last verified: 2026-09-28. The field moves fast; if a claim below matters for a
decision and is more than ~6 months old, re-check the primary source listed in
`references/sources.md` before relying on it.

## The one rule that matters most

**If the content is not in the raw HTML the server returns, most AI crawlers cannot see it.**

- GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot and similar fetch raw HTML
  and do not execute JavaScript. A Vercel/MERJ analysis of 500M+ GPTBot fetches found zero JS
  execution.
- Googlebot renders JS (queued, delayed, can fail). Bing renders JS only partially.
  ChatGPT search results align far more with Bing's index than Google's.
- So a client-side-rendered React SPA is: indexable-with-caveats in Google, weak in Bing,
  and a blank page to ChatGPT/Claude/Perplexity.

Everything else in this skill is secondary to getting this right.

## Workflow

Follow these steps in order. Don't skip to meta tags or schema while step 1 is failing.

### Step 1 — Verify what crawlers actually receive

Run the deterministic audit script against every important public URL:

```bash
python scripts/audit_raw_html.py https://example.com/ https://example.com/pricing
```

It fetches pages **without JavaScript** using crawler user-agents, and reports on:
visible word count, `<title>`, meta description, canonical, `<h1>`, `lang`, hreflang,
JSON-LD types, internal links, the robots.txt verdict per bot, and the sitemap. It flags an
"SPA shell" when the body has almost no text.

If you can't run Python, use the manual equivalent:
`curl -sA "GPTBot" URL | grep -iE "<h1|<title|application/ld\+json"`.

If step 1 shows an SPA shell, go to step 2. If it passes, go to step 3.

### Step 2 — Fix rendering (architecture decision)

Read `references/rendering.md` for recipes. Decision rule:

| Page type | Render strategy |
|---|---|
| Marketing, landing, pricing, about, blog, docs, FAQ, service pages | **Static (SSG) or prerendered HTML.** Best default. |
| Public pages with data that changes (listings, availability, per-tenant public pages) | **SSR**, or SSG plus a rebuild/revalidate on change. |
| Logged-in app (dashboards, booking flow internals, admin) | **CSR SPA is fine.** Put `noindex` on it and keep it out of the sitemap. |

Preferred pattern for SaaS: **split the public site from the app.** Serve the public pages
as static HTML (Astro, or React Router v7 `prerender`, or a Vite prerender plugin). Mount the
interactive app only where it's needed, either on `app.` or `/app`, or as an embedded widget
inside a static page. SEO content lives in the static HTML. The widget is progressive
enhancement on top of it.

Do not rely on "dynamic rendering" (serving bots a different prerendered version). Google
treats it as a workaround, not a recommendation, and it risks cloaking mismatches.

### Step 3 — Crawl access

Read `references/crawlers-robots.md`. Checklist:

- `robots.txt` exists at the root, returns 200, and has no blanket `Disallow: /` left over
  from staging.
- **Search/retrieval bots are allowed**: Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User,
  Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User. Blocking these removes the
  site from those AI answers.
- Allowing or blocking **training bots** (GPTBot, ClaudeBot, Google-Extended, CCBot, etc.) is a
  separate business decision. It does not affect current AI search citations.
- **CDN/WAF check.** Cloudflare can block AI bots before robots.txt is ever read. New
  domains have blocked AI crawlers by default since July 2025. Since 15 Sep 2026 the settings
  are split into Search / Agent / Training. Verify in the dashboard (AI Crawl Control) and
  with the audit script's status codes.
- A `Sitemap:` line in robots.txt, and a valid XML sitemap listing only canonical, indexable,
  200-status URLs with accurate `<lastmod>`.

### Step 4 — On-page technical basics (every indexable page)

- A unique `<title>` of about 50–60 characters, with the primary topic first and the brand last.
- A unique meta description of about 150–160 characters, written as a pitch that matches
  the actual positioning.
- A self-referencing `<link rel="canonical">` using the absolute https URL.
- Exactly one `<h1>` that matches the page's purpose, and a logical h2/h3 hierarchy.
- `<html lang="…">` set correctly. Use `nb` or `no` for Norwegian Bokmål and `en` for English.
- Semantic HTML (`main`, `nav`, `article`, `header`, `footer`), real `<a href>` links (not
  onClick navigation), and descriptive anchor text.
- Images have `alt` text, `width`/`height`, and use modern formats. Lazy-load below the fold
  only, never the LCP image.
- OpenGraph and Twitter tags with a 1200×630 image.
- Do not set `maximum-scale=1` or `user-scalable=no` in the viewport tag. Blocking zoom is an
  accessibility failure.
- Everything above must be present in the **raw HTML**, not injected client-side by
  react-helmet or similar in a CSR app.

### Step 5 — Structured data (JSON-LD)

Read `references/structured-data.md`. Short version:

- Put JSON-LD in the server-returned HTML. Mark up only what's visible on the page.
- Always add `Organization` (or `LocalBusiness` subtype) on the home/about page, with `name`,
  `url`, `logo`, `sameAs`, contact details, and address or org number where relevant.
- Add `BreadcrumbList`, and `Product`/`Offer`, `Event`, `Article`, `SoftwareApplication`,
  or `Course` where they genuinely fit.
- **FAQ rich results were retired in Google on 7 May 2026. HowTo rich results are gone.**
  FAQPage markup is still valid and harmless, but don't add it expecting a Google SERP
  feature. Visible Q&A content is still useful for users and AI extraction.
- Structured data is not required for Google's AI features and doesn't guarantee citation.
  It helps entity understanding and rich-result eligibility.

### Step 6 — Content that gets cited

Read `references/content-geo.md`. The core points:

- Google's official position (guide updated July 2026) is that optimizing for AI Overviews
  and AI Mode is still SEO. Unique, non-commodity, first-hand content beats "GEO hacks".
- Answer the real question early on the page. Use clear headings, include concrete facts,
  numbers, prices, and specifics, and name the entity (brand, place, service) explicitly.
- Keep pages fresh. Update them and show real "last updated" dates. AI-cited content skews
  measurably newer than the organic top 10.
- Off-site brand mentions correlate more strongly with AI visibility than backlinks do.
  Profiles, directories, partner and customer sites, and YouTube all count. This is marketing
  work, not code, but flag it to the user.
- Do not generate mass variant pages for fan-out queries. That falls under Google's scaled
  content abuse policy.

### Step 7 — International (if more than one language or market)

Read `references/international.md`. Use one URL per language, reciprocal `hreflang` links
including `x-default`, and translated metadata. Never auto-redirect by IP.

### Step 8 — Performance

Core Web Vitals "good" thresholds are unchanged as of Aug 2026: **LCP ≤ 2.5 s,
INP ≤ 200 ms, CLS ≤ 0.1**, measured at the 75th percentile of real users. Ignore claims that
LCP tightened to 2.0 s; Google's docs don't say that. CWV is a tie-breaker, not a primary
ranking lever. Static HTML usually passes by default.

### Step 9 — Measurement and indexing hand-off

Tell the user which of these to do. They require account access the agent usually lacks:

- **Google Search Console**: verify the site, submit the sitemap, and use URL Inspection →
  "View crawled page" to confirm the rendered HTML. Check the **Generative AI performance
  report**, and confirm the site is **included in generative AI features** (there is now a
  Search Console toggle for this, and it is required for eligibility).
- **Bing Webmaster Tools**: verify, submit the sitemap, and use the **AI Performance** report
  (Copilot citations and grounding queries). Bing matters disproportionately for ChatGPT.
- **IndexNow**: ping Bing and others on publish or update. Google does not use it.
- **Google Business Profile**, for any business with a physical or local service area.

#### After publishing or updating pages (repeat on every deploy)

1. **Regenerate the sitemap at build time.** New URLs get added, removed URLs are dropped,
   and `<lastmod>` is set to the real content-change date. Never stamp every URL with the
   deploy time, because Google stops trusting lastmod that is always "now".
2. **Google: submit the sitemap once, not on every deploy.** Submit it in Search Console →
   Sitemaps (or reference it in robots.txt). Google then refetches it on its own schedule,
   and an accurate lastmod is what gets changed pages recrawled. The old
   `google.com/ping?sitemap=` endpoint was retired in 2023, so don't implement it.
   - Optional automation: the Search Console API `sitemaps.submit` method, with a service
     account added as a user on the property. It's useful for multi-tenant setups with many
     properties.
   - For a few important new pages: URL Inspection → "Request indexing" (manual, daily quota).
   - **Do not use the Google Indexing API** for normal pages. It is only supported for
     JobPosting and BroadcastEvent pages.
3. **Bing and others: ping IndexNow** with the changed URLs on every deploy, e.g. POST to
   `https://api.indexnow.org/indexnow` with the key file hosted at the site root. Also submit
   the sitemap once in Bing Webmaster Tools (it can import from Search Console).
4. **Verify after deploy.** Run `scripts/audit_raw_html.py` on the new URLs. After a few days,
   check Search Console → Pages / Sitemaps for "Discovered – currently not indexed" or errors.

For multi-tenant platforms: each tenant domain needs its own Search Console property (a
domain property via DNS TXT is easiest), its own sitemap, and a robots.txt that points to it.
A sitemap can only list URLs on its own host unless cross-site submission is verified in
Search Console.

## Things NOT to spend time on

Evidence as of mid-2026:

- **llms.txt**: ignored by Google Search, not read in production by any major AI search
  engine, and 97% of published files got zero requests in Ahrefs' 137k-domain log study.
  Only add one if the site has developer docs consumed by coding assistants, and never as a
  visibility lever.
- **Chunking content into tiny pieces** or **rewriting in a special "AI style"**: Google says
  this is unnecessary.
- **`/.well-known/ai.txt`, `/ai/summary.json`** and similar invented files: no engine reads them.
- **Meta keywords tag**: ignored.
- **Chasing a Lighthouse 100**: once the field CWV thresholds pass, content and access matter
  far more.

## Output expectations

When auditing, report findings in this order:
1. Blockers: raw-HTML visibility, robots/CDN blocks, noindex on pages that should be indexed.
2. High impact: titles/descriptions, canonical, h1, sitemap, positioning mismatch.
3. Medium: structured data, hreflang, internal linking.
4. Low: CWV polish, OG images.

Label every recommendation with its evidence level: **Official** (Google, Bing, OpenAI or
Anthropic docs), **Measured** (large-scale study), or **Opinion** (industry consensus without
hard data). Don't present vendor "GEO score" claims as facts.

When implementing, verify with `scripts/audit_raw_html.py` after deploy, not just locally.
