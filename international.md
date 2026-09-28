# International and multilingual (Norway-focused defaults)

## When it applies
Apply this whenever the site targets more than one language, or targets Norway while
written in English. Norwegian buyers search in Norwegian. An English-only site will not match
queries like "skreddersydd programvare" or "booking system for flyklubb".

## Rules
- **One URL per language version.** Use subfolders (`/no/`, `/en/`) or ccTLD/subdomains.
  Don't switch language on the same URL via cookies or JS.
- **Language codes**: `nb` (Bokmål), `nn` (Nynorsk), `no` (generic Norwegian), or regional
  forms like `nb-NO` and `en-GB`. Google accepts ISO 639-1 plus an optional ISO 3166-1
  region.
- **hreflang must be reciprocal and self-referencing.** Every version lists all versions,
  itself included, plus an `x-default`:
  ```html
  <link rel="alternate" hreflang="nb" href="https://example.no/" />
  <link rel="alternate" hreflang="en" href="https://example.no/en/" />
  <link rel="alternate" hreflang="x-default" href="https://example.no/" />
  ```
- Each language version has its **own canonical pointing to itself**, never to the other
  language.
- Set `<html lang>` to match the page language. Set `og:locale` to `nb_NO` or `en_GB` and add
  `og:locale:alternate` for the others.
- **Translate the metadata too**: title, description, alt text, and JSON-LD `description`
  and `name`.
- **Never auto-redirect by IP or Accept-Language.** Crawlers mostly come from US IPs and
  would never see the Norwegian version. Offer a visible language switcher instead.
- Put local signals in the visible content: Norwegian address, org number, NOK prices,
  +47 phone number.
- For machine-translated pages, have a native speaker review at least titles, H1s, and key
  pages. Unreviewed bulk machine translation can fall under scaled-content policy.

# Measurement, indexing, and verification tools

| Tool | What it's for |
|---|---|
| Google Search Console | Indexing, URL Inspection (rendered HTML), sitemaps, CWV, the **Generative AI performance report**, and the **generative AI features inclusion setting** (required for eligibility). |
| Bing Webmaster Tools | Indexing, sitemaps, **AI Performance** report (Copilot/partner citations, grounding queries; Intents/Topics/Citation Share added June 2026), IndexNow insights. |
| IndexNow | Instant URL change notification to Bing, Yandex, Seznam, Naver and others. Google does not support it. Most CMS/hosts have plugins, or POST to `https://api.indexnow.org/indexnow` with a key file hosted on the site. |
| PageSpeed Insights / CrUX | Field Core Web Vitals (LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at p75). |
| Rich Results Test, validator.schema.org | Structured data validation. |
| Server/CDN logs | Which bots actually hit which pages. Verify bot identity by reverse DNS or IP lists. |
| Manual prompts | Ask ChatGPT, Claude, Perplexity, Gemini, and Copilot the buyer's real questions monthly and log whether the brand is cited. Third-party "AI visibility" tools automate this; treat their scores as indicative. |
