# Crawlers, robots.txt, and CDN bot controls

## Bot categories (2026)

The big change since 2024 is that each vendor now runs **separate bots for training, search
indexing, and user-triggered fetches**. Each has its own robots.txt token. Blocking one does
not block the others.

| Token | Vendor | Purpose | Allow for AI search visibility? |
|---|---|---|---|
| Googlebot | Google | Search index. Also feeds AI Overviews and AI Mode. | **Yes, required** |
| Bingbot | Microsoft | Bing index. Feeds Copilot and is heavily used by ChatGPT search. | **Yes** |
| OAI-SearchBot | OpenAI | ChatGPT search index. Blocking it removes the site from cited ChatGPT answers. | **Yes** |
| ChatGPT-User | OpenAI | Live fetch when a user asks ChatGPT to read a URL. OpenAI says robots.txt may not apply the same way. | **Yes** |
| GPTBot | OpenAI | Model training | Business decision |
| Claude-SearchBot | Anthropic | Claude search indexing | **Yes** |
| Claude-User | Anthropic | Live, user-initiated fetch | **Yes** |
| ClaudeBot | Anthropic | Model training | Business decision |
| PerplexityBot | Perplexity | Perplexity search index | **Yes** |
| Perplexity-User | Perplexity | Live user fetch | **Yes** |
| Google-Extended | Google | A robots **token**, not a separate crawler. It controls use of content for Gemini training and grounding. It does **not** affect Search or AI Overviews. | Business decision |
| Applebot / Applebot-Extended | Apple | Search / training | Allow Applebot; the Extended token is a decision |
| Amazonbot, Amzn-SearchBot | Amazon | Training / search (Alexa, Rufus) | Decision / Yes |
| Meta-ExternalAgent, meta-externalfetcher | Meta | Training / live fetch | Decision |
| DuckAssistBot, MistralAI-User | DuckDuckGo, Mistral | Live AI answers | Yes |
| CCBot | Common Crawl | Open dataset used by many LLMs | Decision |
| Bytespider | ByteDance | Training (historically aggressive) | Usually block |

Training bots influence what *future* models know about the brand. For a small or unknown
brand, allowing them is often net-positive because the models learn you exist. For a
publisher that sells content, blocking them is common. It is the user's call. Ask if it's
unclear, and default to allow for small B2B or service businesses that want to be known.

## robots.txt template (visibility-first)

```txt
# robots.txt — visibility-first policy (verified 2026-09)

User-agent: *
Allow: /
Disallow: /app/
Disallow: /admin/
Disallow: /api/

# Search & live-answer bots: explicitly allowed
User-agent: Googlebot
User-agent: Bingbot
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: DuckAssistBot
Allow: /
Disallow: /app/
Disallow: /admin/
Disallow: /api/

# Training bots: allowed by default. To opt out, change "Allow: /" to "Disallow: /".
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: CCBot
Allow: /
Disallow: /app/
Disallow: /admin/
Disallow: /api/

Sitemap: https://example.com/sitemap.xml
```

Notes:
- A bot follows only the **most specific** group that matches it and ignores the `*`
  group. That's why the Disallow lines are repeated in each group.
- Grouping several `User-agent:` lines over one rule set is valid (RFC 9309).
- robots.txt controls crawling, not indexing. Use `<meta name="robots" content="noindex">`
  or an `X-Robots-Tag` header to keep crawlable pages out of the index. Don't combine
  noindex with a robots.txt Disallow on the same URL, because the bot then can't see the
  noindex.
- **Never paste a borrowed "block all AI bots" list without reading it.** Some circulating
  lists include `Googlebot` or `Bingbot`.
- Staging environments: use `noindex` plus auth. Make sure the staging `Disallow: /` never
  ships to production. Add a deploy check for it.

## CDN / WAF layer (often the real blocker)

robots.txt is advisory. CDNs can block bots before they ever reach it:

- **Cloudflare**: new domains have blocked known AI crawlers by default since 1 July 2025.
  Since 1 July 2026 the controls are split into Search / Agent / Training on every plan.
  From **15 Sep 2026**, newly onboarded domains get Training and Agent blocked by default on
  pages with ads, and existing customers also saw default changes. Cloudflare evaluates
  multi-purpose crawlers (Googlebot, Bingbot, Applebot) under both policies, so blocking
  "Training" can end up blocking them too. **Always check Security → Bots / AI Crawl
  Control settings and test with real bot user-agents.**
- Other CDNs behave differently (some hard-block, some challenge, some pass through). If the
  audit script returns 403, 429, or a challenge page for bot user-agents but 200 for a
  browser, the CDN is the problem.
- Rate limits and bot-fight modes can silently serve challenge pages to crawlers.

## Verifying real bots

User-agent strings are trivially spoofed. To act on log data, verify by reverse DNS or
against published IP ranges. Google, Bing, OpenAI, and Anthropic all publish verification
methods and IP lists.

## Sitemaps

- An XML sitemap at `/sitemap.xml`, or a sitemap index for more than 50k URLs.
- Include only canonical, indexable URLs that return 200. No redirects, no noindexed pages,
  no app routes.
- `<lastmod>` must reflect real content changes. Google ignores it if it's always "now".
- Reference it in robots.txt and submit it in both Google Search Console and Bing Webmaster
  Tools.
- For multilingual sites, sitemap hreflang annotations are an alternative to HTML `<link>`
  tags.
