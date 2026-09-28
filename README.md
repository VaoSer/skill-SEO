# seo-ai-visibility

An [Agent Skill](https://agentskills.io) that teaches AI coding agents (Claude Code, GitHub Copilot, Codex, Cursor and others) to build and audit websites that **Google, Bing and AI search engines (ChatGPT, Claude, Perplexity, Copilot, Gemini) can actually read, index and cite.**

The core problem it solves: most AI crawlers do not execute JavaScript. A client-side-rendered React/Vite SPA looks like an empty page to them. This skill makes the agent check what crawlers really receive, fix rendering (static, prerendered or SSR), set up crawler access, metadata and structured data, and skip the "GEO hacks" that the evidence says don't work (such as llms.txt).

**Evidence last verified: 2026-09-28.** Every recommendation is labelled Official (vendor docs), Measured (large-scale study) or Opinion. Sources are listed in [`references/sources.md`](references/sources.md). The field changes quickly, so check the date.

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | The 9-step workflow the agent follows, including a post-publish sitemap and indexing routine |
| `references/rendering.md` | SSR / SSG / prerender vs CSR, recipes for React Router v7, Astro, Vite, and the multi-tenant "static pages + embedded app" pattern |
| `references/crawlers-robots.md` | AI bot table (training vs search vs user-fetch), robots.txt template, Cloudflare/CDN gotchas, sitemaps |
| `references/structured-data.md` | JSON-LD status in 2026 (FAQ/HowTo rich results retired) and templates |
| `references/content-geo.md` | What correlates with AI citations, graded by evidence |
| `references/international.md` | hreflang/multilingual (Norway-focused defaults) and measurement tools |
| `scripts/audit_raw_html.py` | Standard-library Python audit: fetches pages without JS as AI crawlers do and flags SPA shells, robots/CDN blocks, and missing title/H1/canonical/JSON-LD |

## Install

Clone straight into your skills folder, then update later with `git pull`.

**Personal (all projects), Claude Code and VS Code Copilot:**
```bash
git clone https://github.com/<you>/seo-ai-visibility.git ~/.claude/skills/seo-ai-visibility
```

**Single project:**
```bash
git clone https://github.com/VaoSer/skill-SEO.git .claude/skills/seo-ai-visibility
# or .github/skills/ or .agents/skills/, depending on your agent
```

Reload your editor. In Claude Code you can invoke it with `/seo-ai-visibility`, or just ask for an SEO audit.

## Use the audit script on its own

```bash
python3 scripts/audit_raw_html.py https://example.com/ https://example.com/pricing
python3 scripts/audit_raw_html.py --json https://example.com/   # machine-readable
```
Exit code `1` means at least one blocker was found, so it can be used as a post-deploy CI check.

## Disclaimer

This is guidance, not a ranking guarantee. Neither Google nor any AI provider guarantees indexing or citation. Only audit sites you own or have permission to test.

## License

MIT. Built by [Signal Workflows](https://signalworkflows.com).
