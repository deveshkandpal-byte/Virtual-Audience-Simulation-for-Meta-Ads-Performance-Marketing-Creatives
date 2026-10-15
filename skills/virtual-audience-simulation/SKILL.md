---
name: virtual-audience-simulation
description: Review Meta Ads creative concepts and variants using the project's Master Prompt. Use when analyzing static image ads, video concepts/scripts, UGC-style ads, carousels, collection/catalog ads, testimonials/social proof, comparison/educational ads, promotional/conversion ads, storytelling/engagement ads, or industry-specific creatives. Produces cautious, structured feedback and actionable test plans; does not claim real audience testing or validated performance predictions.
---

# Virtual Audience Simulation for Meta Ads Creatives

## Purpose and boundaries

Use this skill to perform a structured pre-launch review of Meta/Facebook/Instagram ad creatives. It can guide a human or AI agent through the review process. It is not a real audience panel, does not access Meta Ads account data, and does not establish actual CTR, conversion rate, ROAS, or guaranteed outcomes.

Before analysis, read the repository's `docs/CREATIVE_TYPE_LIBRARY.md` for the complete creative-format, concept, and execution-style taxonomy.

## Workflow

1. Identify the product/service, market, campaign objective, target audience, funnel stage, offer, CTA, and destination. Mark missing facts as `Not provided`; ask only for essential missing information.
2. Identify all relevant formats/concepts from the creative-type library. Formats may be combined; do not force irrelevant types or assume one format always wins.
3. Review each supplied creative individually before comparison.
4. Assess heading/hook, primary copy, offer, CTA, visual execution (only when the image is actually visible/inspected), trust evidence, audience fit, and destination consistency.
5. Apply format-specific checks:
   - Static image: hierarchy, contrast, legibility, product visibility, composition, brand consistency.
   - Video: opening hook, pacing, subtitles, audio/voice-over, demonstration, closing CTA. If only text is supplied, call it a script/concept review; never imply rendered video or audio was inspected.
   - UGC/testimonial/social proof: natural delivery, relevance, authenticity, evidence, permissions; never invent real customers or results.
   - Carousel: first card, sequence, narrative continuity, swipe motivation, consistency, final CTA.
   - Collection/catalog: product/catalog relevance, imagery, personalization, catalog setup and shopping transition when known.
   - Comparison/education: clarity, fair comparisons, accuracy, usefulness, objection handling.
   - Promotion/conversion: offer value, verified urgency, trust, friction, CTA/objective alignment.
   - Storytelling/industry-specific: emotional relevance and actual product/service fit.
6. Model distinct audience hypotheses when useful (cold, problem-aware, solution-aware, product-aware, warm, high-intent). Clearly label them as hypotheses, not observed human reactions.
7. Provide strengths, weaknesses, component-specific modifications, launch-readiness label, and prioritized action plan.
8. For multiple creatives, report each individually first, then compare attention, click intent, conversion potential, funnel fit, and testing priorities without forcing a universal winner.
9. Suggest controlled live tests to validate the hypotheses. Change one meaningful variable at a time where practical.

## Metrics and claim integrity

- Prefer qualitative engagement/CTR/conversion assessments when there is no defensible quantitative basis.
- Do not invent precise benchmark data or present estimates as actual Meta Ads performance.
- Separate engagement from purchase intent.
- Never invent product features, prices, offers, discounts, deadlines, guarantees, testimonials, identities, customer outcomes, or credentials.
- Flag claims that require substantiation and platform-policy review.
- State assumptions and uncertainty explicitly.
- Use the Master Prompt's assessment labels: `Ready for controlled testing`, `Requires minor modifications`, `Requires major modifications`, `Not recommended in its current form`.

## Output schema

Return valid JSON for each creative using this structure:

```json
{
  "creative_type": "Primary format — concept",
  "components": {
    "heading": "string or Not provided",
    "ad_copy": "string or Not provided",
    "offer": "string or Not provided",
    "cta": "string or Not provided"
  },
  "simulated_performance": {
    "engagement_rate": "Qualitative assessment with uncertainty",
    "ctr": "Qualitative assessment with uncertainty",
    "conversion_rate": "Qualitative assessment with uncertainty"
  },
  "analysis": {
    "strengths": ["specific, evidence-based observation"],
    "weaknesses": ["specific limitation or risk"]
  },
  "recommended_modifications": [
    {
      "component": "heading | ad_copy | offer | cta | visual | hook | video_structure | carousel_sequence | trust_signals | audience_fit | landing_page",
      "suggestion": "specific action"
    }
  ],
  "overall_assessment": "One of the four approved assessment labels"
}
```

For multiple creatives, return an array of individual reports, followed by a separate comparative summary and prioritized action plan. Do not put Markdown comments or trailing commas inside JSON.

## Using the repository app

If this skill is installed in an agent that can execute shell commands and access a local clone, follow `README.md` to install dependencies and start the FastAPI app. The app is available at `http://127.0.0.1:8000`; its API schema is at `/docs`. If the agent cannot execute local tools or the app is not running, perform the review directly from this skill and the supplied creative details; do not pretend to have called the app or inspected files/media you cannot access.

## Reference

- Full taxonomy and detailed checks: `docs/CREATIVE_TYPE_LIBRARY.md`
- Local installation, API-provider configuration, testing, privacy, and deployment: `README.md`
- Security limitations: `SECURITY.md`
