# Sources (re-verify before relying on anything older than ~6 months)

Verified 2026-09-28.

## Official
- Google — Optimizing your website for generative AI features (updated 2026-07-10):
  https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
  Key points: AEO/GEO is "still SEO"; llms.txt is ignored by Google Search; no need to chunk
  or rewrite content for AI; structured data is not required for AI features; the site must
  be included in generative AI features in Search Console; use the Generative AI performance
  report.
- Google — AI features and your website:
  https://developers.google.com/search/docs/appearance/ai-features
- Google — JavaScript SEO basics:
  https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- Google — FAQPage structured data (retirement notice, 7 May 2026):
  https://developers.google.com/search/docs/appearance/structured-data/faqpage
- Google — Simplifying search results (June 2025 structured data phase-out):
  https://developers.google.com/search/blog/2025/06/simplifying-search-results
- Google blog — New controls for website owners (June 2026, gen-AI inclusion toggle):
  https://blog.google/products-and-platforms/products/search/new-controls-website-owners/
- Bing — AI Performance report help: https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c
- Bing blog — Intents/Topics/Citation Share/Compare (June 2026):
  https://blogs.bing.com/search/2026/6/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare/
- OpenAI crawler docs: https://platform.openai.com/docs/bots
- Anthropic crawler docs: https://support.anthropic.com/en/articles/9906653-claude-bot-and-crawling
- React Router pre-rendering: https://reactrouter.com/how-to/pre-rendering

## Measured studies
- Vercel/MERJ, "The rise of the AI crawler": no major AI crawler renders JS.
  https://vercel.com/blog/the-rise-of-the-ai-crawler
- Ahrefs, llms.txt study, 137k domains, May 2026: 97% of files received zero requests.
  https://ahrefs.com/blog/llmstxt-study/
- Ahrefs brand-mentions study (75k brands) and citation-freshness study (~17M citations),
  summarised in secondary sources, 2026.
- Seer Interactive: SearchGPT citations match Bing's top 10 far more than Google's.

## Watch list (things likely to change)
- Cloudflare AI crawler defaults (Search/Agent/Training split; 15 Sep 2026 changes).
- Whether any major AI engine starts honouring llms.txt (currently none).
- Further Google rich-result retirements (check Search Central "Documentation updates").
- Core Web Vitals thresholds (unchanged since INP replaced FID in March 2024).
