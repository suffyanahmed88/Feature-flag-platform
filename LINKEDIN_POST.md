# LinkedIn post

I just built **Flagship**, a standalone feature flag management platform designed around a simple idea: ship with confidence without turning a release into a major infrastructure project.

It includes a polished Next.js dashboard, FastAPI backend, JWT auth, hashed environment API keys, deterministic percentage rollouts, attribute targeting, audit history, and a lightweight Python SDK.

The evaluation engine is deliberately independent of the API layer, making the core release logic easy to test and extend. A user will always receive the same rollout result for a given flag — a small detail that matters enormously in production.

Stack: Next.js, TypeScript, Tailwind, FastAPI, SQLAlchemy, PostgreSQL, Alembic, and httpx.

I kept it intentionally focused: no Docker, queues, Redis, or microservices — just a local-first, understandable MVP with a real API and persistence model.

Source: https://github.com/suffyanahmed88/Feature-flag-platform

#FullStackDevelopment #Python #FastAPI #NextJS #SaaS #FeatureFlags #OpenSource
