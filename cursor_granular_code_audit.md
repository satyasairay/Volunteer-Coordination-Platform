### MASTER CODE AUDIT PROMPT (Incremental Version)

You are performing a **full production readiness, documentation, and SDLC compliance audit** of this repository.

You will work in **phases**, each focused on a manageable subset of the project (e.g., one folder or one group of files). After each phase, you’ll produce a **granular report** and wait for the next batch.

---

## WORKFLOW (FOR AI TO FOLLOW)

**PHASE 1 — INITIAL CONTEXTING**
- Read `package.json`, `README.md`, `docs/`, and top‑level folders.
- Identify architecture, stack, and general structure.
- Request additional folders/files if needed before analysis.

**PHASE 2 — FOLDER‑LEVEL ANALYSIS**
For each major folder (e.g., `/src`, `/api`, `/components`, `/services`, `/db`, `/docs`, `/tests`):
- Analyze 3–5 files at a time.
- Perform a **line‑by‑line review**.
- For each issue or weakness, include:
  1. **File path and line number(s)**
  2. **Issue description** (precise, short)
  3. **Impact level** (BLOCKER / HIGH / MEDIUM / LOW)
  4. **Recommendation** — exactly how to fix or improve it.

**PHASE 3 — RECONSOLIDATION**
- After finishing all folders, produce a unified report combining all identified issues.
- Generate a ranked action list for remediation.

---

## ADDITIONAL SDLC DOCUMENTATION REVIEW

Perform an audit of **missing or incomplete documentation** expected in a standard Software Development Life Cycle (SDLC):

1. **Requirements Documentation**
   - Check if there is a clear statement of project scope, functional/nonfunctional requirements.
   - Recommend how to write or structure missing docs.

2. **Design Documentation**
   - Assess whether architectural diagrams, data models, or sequence flows exist.
   - Recommend artifacts if missing (e.g., UML, ERD, API design doc).

3. **Implementation Documentation**
   - Verify inline code comments, API docstrings, README clarity.
   - Identify where code lacks explanation.

4. **Testing Documentation**
   - Check for test coverage reports, test plans, or `tests/` folder.
   - Recommend test types missing (unit, integration, end‑to‑end).

5. **Deployment & Maintenance Docs**
   - Check for CI/CD instructions, environment setup guides, rollback/recovery notes.
   - Recommend DevOps and maintenance documentation improvements.

6. **User & API Documentation**
   - Review `/docs`, `/swagger`, or `/openapi` if available.
   - Recommend a structure for user‑facing or API documentation if missing.

7. **Governance & Versioning**
   - Check if changelogs, version tags, and contribution guidelines exist.
   - Recommend practices for governance and release management.

---

## OUTPUT STRUCTURE (PER PHASE)

### 1. EXECUTIVE SUMMARY
- Short narrative of what was reviewed.
- Overall repo health (grade A–F).

### 2. FILE‑BY‑FILE FINDINGS
For every file reviewed:
```
File: src/routes/userController.js
Line 45–52 → Hardcoded JWT secret. [BLOCKER]
Recommendation: Move secret to environment variable and use process.env.SECRET_KEY.

Line 73 → Missing error handling for DB call. [HIGH]
Recommendation: Wrap in try/catch, log error via centralized logger.
```

### 3. STRUCTURAL & CROSS‑CUTTING ISSUES
Summarize recurring patterns (e.g., repeated auth code, inconsistent error handling) and recommend global fixes.

### 4. SDLC DOCUMENTATION GAPS
List missing documentation artifacts and provide specific recommendations for each category (Requirements, Design, Testing, etc.).

### 5. PRIORITIZED ACTION PLAN
Summarize all recommendations by priority:
- BLOCKER: Must fix immediately.
- HIGH: Fix before launch.
- MEDIUM: Fix within next sprint.
- LOW: Optional polish.

---

## EXECUTION INSTRUCTIONS

1. Perform **incremental analysis**, no more than 3–5 files at once.
2. Always output line‑by‑line findings with exact recommendations.
3. After each phase, confirm with me before moving to the next folder.
4. Final output: a consolidated audit report across all code and SDLC documentation.

---

## DELIVERABLE FORMAT
- Markdown document with headings per phase and section.
- All recommendations actionable, specific, and technically sound.
- No generic comments like “improve readability” — specify exactly *how*.

---

### TL;DR
**Goal:** Produce an enterprise‑grade, line‑by‑line audit + SDLC documentation review + prioritized remediation roadmap.

**Constraints:**
- Process repo incrementally (3–5 files per step).
- Each issue must include a recommendation.
- Include SDLC documentation review and improvement plan.

