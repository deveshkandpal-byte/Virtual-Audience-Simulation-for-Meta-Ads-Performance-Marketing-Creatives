# Contributing

Thank you for considering a contribution.

## Before making changes

1. Open an issue describing the problem or proposed improvement.
2. Keep changes focused and document any new configuration.
3. Never include API keys, client data, or other secrets in commits.

## Local setup

Use Python 3.11 or newer.

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests before submitting:

```bat
python -m pytest -q
```

## Product guardrails

- Mark missing input as `Not provided`; never invent product facts, discounts, testimonials, guarantees, or outcomes.
- Label model-generated audience reactions as simulated hypotheses, not real audience research.
- Do not present CTR, conversion rate, or ROAS as validated predictions without a documented and evaluated model.
- Keep multi-creative comparisons transparent; completeness alone does not establish a performance winner.
- Update README documentation and tests when behavior changes.
