# Agent Log — 2025-10-31 (Encoding Sanitization)

Actions
- Scanned and removed non‑ASCII characters from all `templates/*.html` files (mojibake cleanup).
- Preserved UTF‑8 meta tags; no functional UI logic changed.
- Annotated plan with the root cause and SVG‑only icon policy.

Validation
- Manual: headings and buttons no longer contain garbled symbols.
- TODO: replace removed decorative icons with inline SVGs in future phases (not part of this cleanup pass).

Revert
- Implementation rollback point: tag `v2025.10.31-m2-preclip`.