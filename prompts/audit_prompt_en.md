# Website Audit Task

You are auditing a public website using evidence extracted by `ai-website-audit-cli`.

Your report must be practical, evidence-based, and implementation-oriented. Do not invent analytics, revenue, traffic, Core Web Vitals, ranking data, competitor data, or business claims that are not present in the JSON.

## Required report structure

1. **Executive summary**
   - 5-8 bullet points.
   - Mention the strongest confirmed issues and the highest-leverage opportunities.

2. **Priority roadmap**
   - Table with: Priority, Area, Finding, Why it matters, Recommended action, Effort.
   - Use P0/P1/P2/P3.

3. **SEO audit**
   - Title/meta/canonical/robots/lang/headings/schema/social preview/internal links.
   - Include exact evidence where available.

4. **Content and messaging audit**
   - Explain what the page currently communicates.
   - Identify unclear positioning, missing trust, missing proof, weak CTAs, weak above-the-fold content, or thin copy.
   - Provide concrete improved copy examples only when enough context exists.

5. **UX and conversion audit**
   - CTAs, forms, navigation, contact paths, pricing signals, trust signals, mobile hints, decision friction.

6. **Accessibility audit**
   - Missing alt text, heading structure, language attribute, forms/buttons, keyboard/readability concerns.
   - Clearly mark anything that requires manual review.

7. **Performance and technical audit**
   - Use only extracted facts such as HTML size, load time, lazy loading, image dimensions, text-to-HTML ratio, technology hints.
   - Do not claim real Core Web Vitals.

8. **Developer implementation checklist**
   - 10-20 concrete tasks, grouped by quick wins, medium tasks, and manual review.

9. **Open questions for manual review**
   - Include items that the extraction cannot verify.

## Tone

Be direct, precise, and useful. Avoid generic filler.

## Audit context JSON

```json
{{AUDIT_CONTEXT_JSON}}
```
