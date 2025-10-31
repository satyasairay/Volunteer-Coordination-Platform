# Sanitization Log — 2025-10-31

Actions
- Created checkpoint tag `v2025.10.31-m1.2-sanitize` before changes.
- templates/index.html:
  - Removed all non-ASCII characters (regex: `[^\x09\x0A\x0D\x20-\x7E]`).
  - Normalized nav brand to `Joyguru Bhadrak`.
  - Replaced zoom-out label with `-`.
  - Disabled reset button by removing its markup (kept CSS fallback `.zoom-btn-reset { display:none }`).
- Added CSS fallback to hide reset control.

Validation
- App endpoints unchanged; running smoke next.

Rollback
- Use tag `v2025.10.31-m1.2-sanitize` to revert fast if needed.
