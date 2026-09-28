# Structured data (JSON-LD), status as of Sept 2026

## Principles
- Use JSON-LD in a `<script type="application/ld+json">` that is **in the server-returned
  HTML**.
- Mark up only content that is visible on the page. Hidden or contradictory markup violates
  Google's structured data policies.
- Structured data is **not required** for Google's AI features, and there is no special
  "AI schema". It helps with rich-result eligibility and entity understanding. Microsoft has
  said schema helps its systems interpret pages.
- Validate with Google's Rich Results Test and validator.schema.org.
- Markup that Google no longer uses is harmless: "does not cause problems for Search, but
  also has no visible effects".

## What still produces Google rich results (selected)
Article, Breadcrumb, Event, Local business, Organization (knowledge panel and logo), Product
(product snippet and merchant listing), Review snippet (for eligible types), Software app,
Course list, Video, Recipe, Job posting, Profile page, Discussion forum, Q&A (user-generated
Q&A pages, not a site's own FAQ), Vacation rental, and Image metadata.

## Retired or no SERP effect
- **FAQPage**: rich results were retired in Google Search on **7 May 2026**. Search Console
  reporting and Rich Results Test support were removed in June 2026, and API support ends
  August 2026. The markup is still valid schema.org. Keep it if it describes a visible,
  useful FAQ; don't add it expecting a Google SERP feature. Visible Q&A sections are still
  useful for users and for AI answer extraction.
- **HowTo**: no rich result on any surface.
- Phased out in 2025–2026: Book actions (partly restored), Course info, Claim review,
  Estimated salary, Learning video, Special announcement, Vehicle listing, Practice problems,
  Dataset (now Dataset Search only), Nutrition facts, Nearby offers, and others. Check
  Google's "Documentation updates" page before adding niche types.

## Templates

### Organization / business (home or about page)
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.no/#org",
  "name": "Example AS",
  "url": "https://example.no/",
  "logo": "https://example.no/logo.png",
  "description": "One sentence that matches the positioning on the page.",
  "foundingDate": "2024",
  "founder": {"@type": "Person", "name": "Founder Name"},
  "address": {"@type": "PostalAddress", "addressLocality": "Oslo", "addressCountry": "NO"},
  "identifier": {"@type": "PropertyValue", "propertyID": "NO-orgnr", "value": "123456789"},
  "email": "post@example.no",
  "sameAs": [
    "https://www.linkedin.com/company/example",
    "https://www.proff.no/...",
    "https://github.com/example"
  ]
}
```
Use `ProfessionalService`, `LocalBusiness`, or a specific subtype (e.g.
`SportsActivityLocation`, `Locksmith`) when there is a physical location or service area.
Add `geo`, `openingHoursSpecification`, `areaServed`, and `priceRange`.

### Service with price (e.g. a bookable experience)
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Guided kayak tour — Bergen",
  "description": "…visible description…",
  "image": "https://example.no/img/tandem.jpg",
  "brand": {"@id": "https://example.no/#org"},
  "offers": {
    "@type": "Offer",
    "price": "2500",
    "priceCurrency": "NOK",
    "availability": "https://schema.org/InStock",
    "url": "https://example.no/tandem/"
  }
}
```
(`Service` is semantically closer but gets no rich result. `Product` with `Offer` is widely
used for bookable experiences. Mark up only prices that are shown on the page.)

### BreadcrumbList
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.no/"},
    {"@type": "ListItem", "position": 2, "name": "Tandem", "item": "https://example.no/tandem/"}
  ]
}
```

### SoftwareApplication (SaaS product page)
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Product",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": {"@type": "Offer", "price": "990", "priceCurrency": "NOK"},
  "publisher": {"@id": "https://example.no/#org"}
}
```

### Article / blog post
Include `headline`, `datePublished`, `dateModified` (real dates), `author` (a Person with a
`url` to a bio page), and `image`. Freshness and authorship matter for AI citation, and
visible dates should match the markup.

## Connect entities with @id
Give the Organization an `@id` and reference it from Product, Article, and similar markup.
That builds one coherent entity graph instead of disconnected blobs.
