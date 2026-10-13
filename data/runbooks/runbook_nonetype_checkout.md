# Incident Runbook: INC-102 — NoneType AttributeError in Cart Checkout

## Symptom:
FastAPI endpoint crashes with `AttributeError: 'NoneType' object has no attribute 'customer_id'` or unhandled 500 Internal Server Error during cart processing.

## Root Cause:
Checkout service assumed `cart.user` is guaranteed to be hydrated from session cookies. When anonymous or expired guest sessions trigger checkout, `cart.user` is `None`.

## Remediation Steps:
1. Introduce defensive guard clause:
   ```python
   if not cart or not cart.user:
       raise ValueError("Invalid checkout session: cart user cannot be None")
   ```
2. Enforce strict Pydantic model validation on incoming checkout payloads.
3. Synthesize regression test verifying anonymous guest cart gracefully raises 400 Bad Request rather than crashing with 500.
