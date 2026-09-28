# Content for AI citation (GEO/AEO), graded by evidence

Evidence levels: **[Official]** vendor documentation · **[Measured]** large-scale
study · **[Opinion]** common industry advice without strong data.

## How the engines retrieve
- **Google AI Overviews / AI Mode** use RAG over Google's own search index, plus
  "query fan-out": the model issues several related sub-queries and cites pages that answer
  them. A page must be indexed and eligible for a snippet, and the site must be included in
  generative AI features in Search Console. [Official]
- **ChatGPT search** uses its own OAI-SearchBot index plus third-party search. Its citations
  overlap heavily with Bing's top results (one analysis: 87% vs 56% for Google). [Measured]
- **Perplexity** runs a live search for every query, is very freshness-sensitive, and
  historically cited a lot of UGC (Reddit, YouTube). [Measured]
- **Copilot** grounds on Bing. [Official]
- The engines overlap little: roughly 11–12% domain overlap between ChatGPT and Perplexity in
  one analysis. Being visible in one doesn't mean being visible in another. [Measured]

## What correlates with being cited
1. **Being crawlable in raw HTML** by the retrieval bots. It's a precondition. [Official/Measured]
2. **Unique, non-commodity, first-hand content.** Google calls this the single biggest long-term
   factor. Examples: original data, real prices, specific local knowledge, case details,
   expert opinion. Generic "7 tips" content is commodity. [Official]
3. **Brand mentions across the web.** In Ahrefs' study of 75k brands, mentions correlated
   about 3× more strongly with AI visibility (~0.66) than backlinks (~0.22). YouTube mentions
   were the strongest single correlate for AI Overviews. [Measured, correlational]
4. **Freshness.** Across ~17M citations, AI-cited content was ~25.7% fresher than Google's
   organic top 10. Perplexity is especially recency-biased. [Measured]
5. **Clear structure.** Descriptive headings, a direct answer near the top of each section,
   concrete facts and numbers, tables for comparisons. Google frames this as writing for
   humans, which happens to be extractable. [Official + Opinion]
6. **Entity clarity.** State who you are, what you do, and where, in plain text on the
   page. Keep it consistent with directory listings (Google Business Profile, national
   registries, LinkedIn, industry directories). [Opinion, with some Official support via GBP]

Ranking top-10 in Google is no longer a strong predictor of AI Overview citation. One
early-2026 measurement found only ~38% of cited pages ranked top 10. [Measured]

## Page-writing checklist for the agent
- The first 1–2 sentences under the H1 say what the page is and who it's for, including the
  entity name and location if the business is local.
- One topic per page, with sections that each answer a question a buyer actually asks.
- Include specifics: prices (and currency), durations, capacities, requirements, locations,
  dates, and numbers.
- Show a visible "Last updated" date, and update it only when the content really changes.
- Add an author or owner with credentials on expertise-driven content.
- Internal links between related pages use descriptive anchors.
- The meta description and title match the page's real positioning (a common failure:
  metadata still describing an old offering).

## Don'ts
- Don't mass-generate near-duplicate pages for query variants (scaled content abuse
  policy). [Official]
- Don't chase inauthentic "mentions" (spammy directories, paid Reddit posts). [Official]
- Don't hide content in tabs or accordions that only load on click via JS. Content inside a
  collapsed but server-rendered `<details>` is fine.
- Don't rely on llms.txt, ai.txt, or "AI summary JSON" files for visibility. [Measured:
  Ahrefs found 97% of llms.txt files got zero requests across 137k domains in May 2026, and
  SE Ranking found no correlation with citations across ~300k domains.]

## Conversion context (for prioritisation)
AI-referred visitors are few, but studies report much higher conversion rates than organic
search. Treat the exact multipliers as vendor-reported. [Measured, but self-interested sources]
