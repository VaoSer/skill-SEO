# Rendering for crawlers: SSR, SSG, prerender vs CSR

## Contents
1. Who renders JavaScript
2. The four strategies
3. Recipes by stack
4. Pattern: static public pages + embedded app
5. Metadata and JSON-LD in SPAs
6. Verification

## 1. Who renders JavaScript (mid-2026)

| Consumer | Executes JS? | Notes |
|---|---|---|
| Googlebot (Search, AI Overviews, AI Mode) | Yes | Rendering is queued and delayed. It can fail on blocked resources, slow scripts, or errors. |
| Gemini (via Google infrastructure) | Yes | Inherits Google's rendering. |
| Bingbot (Bing, Copilot) | Partially | Unreliable for heavy SPAs. |
| GPTBot, OAI-SearchBot, ChatGPT-User | No | Raw HTML only. GPTBot sometimes downloads JS files but doesn't run them. |
| ClaudeBot, Claude-SearchBot, Claude-User | No | Raw HTML only. |
| PerplexityBot, Perplexity-User | No | Raw HTML only. |
| Meta, ByteDance, Apple-Extended, CCBot | No | Raw HTML only. |
| Social preview bots (Slack, LinkedIn, Facebook) | No | Use OG tags from raw HTML. |

Consequence: the raw HTML response is the only version every consumer sees. Design for it.

## 2. The four strategies

- **SSG / static prerender (build time).** HTML is generated at build and served as files.
  It is the fastest, the cheapest, and every crawler sees the full content. Use it for
  anything that changes less often than you deploy, or that can be rebuilt on change.
- **SSR (request time).** The server renders HTML per request and then hydrates. Use it for
  public pages with frequently changing or per-tenant data. It needs a Node or edge runtime.
- **ISR / revalidate (hybrid).** Static pages that regenerate on a timer or on demand
  (Next.js, Astro with adapters, Nuxt). A good fit for listings.
- **CSR (client-side SPA).** An empty shell plus JS. Acceptable only for logged-in or
  non-public UI. Mark it `noindex`.

Avoid **dynamic rendering** (user-agent sniffing to serve bots prerendered HTML). Google
documents it as a workaround, not a long-term solution. It adds infrastructure, and if the
bot and user versions diverge it risks being treated as cloaking.

## 3. Recipes by stack

### Vite + React SPA, minimal change (prerender known routes)
Options:
- **React Router v7 framework mode**: in `react-router.config.ts`, set
  `ssr: false, prerender: ["/", "/pricing", "/about", ...]`. This produces
  `build/client/<route>/index.html` with real content and hydrates afterwards. With
  `prerender: true` it includes all static (non-parameterised) routes. For dynamic routes,
  pass an async function that returns paths from a CMS or DB at build time. Route `loader`s
  run at build time for prerendered paths.
- **Vite prerender plugins** (e.g. `vite-plugin-seo-prerender`, `react-spa-prerender`), which
  render a route list after build using headless Chrome. Fine for a handful of marketing
  pages. Check that the output HTML actually contains the text.
- For **all** of these, confirm hydration doesn't wipe or duplicate content, and that
  `<head>` tags are part of the prerendered output.

### Marketing site as its own project (recommended for SaaS)
- **Astro**: static by default, ships zero JS unless asked, and lets you embed React
  "islands" (`client:load` / `client:visible`) for interactive parts. It is the best fit when
  most of the page is content and only a widget is interactive.
- **Next.js**: App Router with static generation or SSR. It suits a large, data-driven
  public surface.
- Plain hand-written HTML is completely valid for a small site. Crawlers don't care
  about the framework.

### Existing Express/Node backend serving a SPA
- Render the public routes server-side (templates or React `renderToString`) and keep `/app/*`
  as the SPA. At minimum, inject the per-route `<title>`, meta, canonical, JSON-LD, and a
  real text summary into the HTML shell on the server.

### Replit and other hosted builders
- They often scaffold Vite + React CSR by default. Tell the agent explicitly: "public pages
  must be prerendered or SSR; verify with curl that text is in the HTML." Check the
  deployment type too. Static deployments serve prerendered files; autoscale or reserved-VM
  deployments can run SSR.

## 4. Pattern: static public pages + embedded app (multi-tenant)

Used for booking platforms and similar SaaS where each tenant has a public presence:

```
tenant.example.no/                 ← static HTML (SSG): who, what, prices, FAQ, JSON-LD
tenant.example.no/tandem/          ← static HTML per service/product
tenant.example.no/book  (or widget) ← React app mounted into <div id="booking">
app.example.no/*                   ← logged-in app, noindex, excluded from sitemap
```

Rules:
- The static page carries all indexable content: prices, descriptions, location, FAQ, and
  contact details. The widget adds interactivity only.
- The widget's container holds meaningful fallback content (e.g. "Book a tandem flight — see
  prices above or call …") so the page reads correctly with JS off.
- If tenants use custom domains, canonical URLs must point to the tenant's public domain,
  not the platform subdomain. Keep one canonical per piece of content.
- Generate per-tenant sitemaps and robots.txt, or make sure a platform-level sitemap only
  lists canonical tenant URLs.
- Rebuild or revalidate a tenant's static pages when they change prices or content (webhook
  → build).

## 5. Metadata and JSON-LD in SPAs

- `react-helmet`-style runtime injection only helps Googlebot, after rendering. For
  everyone else the tags must be in the served HTML. Generate them at build (SSG) or on the
  server (SSR).
- JSON-LD injected client-side is unreliable for rich results even in Google. Emit it in
  the HTML.
- Titles and canonicals must be route-specific. A single shared `index.html` `<title>` for
  every route is a common SPA failure.

## 6. Verification

1. `python scripts/audit_raw_html.py <urls>` against **production**, after deploy.
2. `curl -sA "OAI-SearchBot" <url> | sed 's/<[^>]*>/ /g' | wc -w`. If the word count is near
   zero, the page is invisible to AI crawlers.
3. Google Search Console → URL Inspection → View crawled page, which shows the rendered HTML.
4. Disable JS in browser devtools and load the page. What you see is what AI crawlers get.
