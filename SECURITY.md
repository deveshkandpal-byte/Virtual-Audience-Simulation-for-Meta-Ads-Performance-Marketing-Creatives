# Security Policy

## Reporting a vulnerability

Please do not publish API keys, credentials, private campaign data, or details of an exploitable vulnerability in a public issue.

Until a private security contact is configured for this project, avoid submitting sensitive proof-of-concept material. You may open a public issue describing the general concern without secrets, or contact the repository owner through their GitHub profile.

## Safe-use notes

- Never commit `.env` files, provider API keys, or access tokens.
- Do not deploy the development server directly to the public internet without authentication, rate limits, and production hardening.
- Treat campaign creatives and ad account information as commercially sensitive.
- Uploaded image content may be sent to a configured external AI provider.
- The application is an early MVP and has not undergone an independent security audit.
