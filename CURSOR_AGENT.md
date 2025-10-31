# CURSOR AGENT - REMEDIATION PROMPTS
## Quick Start Prompts for Complete Remediation

**Purpose:** Copy-paste these prompts in new chat sessions to execute the full remediation plan efficiently.

**Prerequisites:** 
- Read `AUDIT_REMEDIATION.md` first for full context
- These prompts assume you've read the remediation plan

---

## PROMPT 1: PHASE 1 - SECURITY & CRITICAL FIXES
**Duration:** 1-2 weeks | **Priority:** BLOCKER

```
I need to execute Phase 1 (Security & Critical Fixes) from AUDIT_REMEDIATION.md.

First, read AUDIT_REMEDIATION.md and CODE_AUDIT_REPORT.md to understand the security vulnerabilities and critical issues.

Then implement all Phase 1 tasks:

WEEK 1: Security Hardening
- Day 1-2: Remove hardcoded credentials from auth.py (lines 7-9) and main.py (line 1628). Add environment variable validation. Implement rate limiting on authentication endpoints using slowapi.
- Day 3-4: Fix XSS vulnerabilities - replace all innerHTML usage (50+ instances) in templates with safe DOM methods or DOMPurify. Implement CSRF token system. Add CSP headers. Sanitize Quill editor output.
- Day 5: Fix bare except clauses in auth.py:34 and main.py. Standardize error handling with custom exception handlers. Add error handling to file I/O operations (main.py:27, 1203, 1216, 1265).

WEEK 2: Critical Bug Fixes & Infrastructure
- Day 6-7: Fix AttributeError in auth.py:127,135. Add input validation. Replace deprecated datetime.utcnow() with datetime.now(timezone.utc).
- Day 8-9: Implement structured logging. Add /health endpoint. Set up monitoring documentation.

Work systematically through each task. After each major task, provide a summary of what was done. If you encounter issues, document them clearly. Use the exact file paths and line numbers from the audit report.

Do NOT proceed to Phase 2 until Phase 1 completion criteria are met:
✅ All hardcoded credentials removed
✅ CSRF protection implemented  
✅ XSS vulnerabilities eliminated
✅ Rate limiting on authentication
✅ All critical bugs fixed
✅ Error handling standardized
✅ Logging infrastructure in place
✅ Health check endpoint working
```

---

## PROMPT 2: PHASE 2 - UI/UX STANDARDIZATION
**Duration:** 2-3 weeks | **Priority:** HIGH

```
I need to execute Phase 2 (UI/UX Standardization) from AUDIT_REMEDIATION.md.

First, read AUDIT_REMEDIATION.md Phase 2 section and CODE_AUDIT_REPORT.md Phase 6 (UI/UX Design Consistency Review) to understand all UI inconsistencies.

Then implement all Phase 2 tasks:

WEEK 1: Design System Foundation
- Day 1-2: Create SDLC design system infrastructure in static/css/:
  * theme.css (CSS variables for colors, spacing, typography)
  * components.css (buttons, cards, inputs, modals)
  * typography.css (font system)
  * utilities.css (common utilities)
  Create style guide document.
- Day 3-5: Unify color system - replace all hardcoded colors across templates with CSS variables. Update index.html, login.html, dashboard.html, register.html, admin.html, admin_users.html, admin_field_workers.html, profile.html.

WEEK 2: Component Standardization
- Day 6-7: Create unified navigation component. Standardize all navigation bars across templates. Consistent height (72px), hamburger placement, menu items.
- Day 8-9: Create button and form component systems. Replace all button implementations (custom CSS, Tailwind, inline styles). Standardize form inputs.
- Day 10: Create card component system. Replace all card implementations.

WEEK 3: Typography, Spacing & Polish
- Day 11-12: Implement typographic scale. Replace all font-family, font-size, font-weight inconsistencies.
- Day 13: Implement 8px spacing scale. Replace all inconsistent spacing.
- Day 14-15: Create modal component system. Standardize responsive design. Ensure mobile navigation consistency.

Work file by file. After updating each template, verify it works. Document any issues. Use the exact file paths and inconsistencies identified in the audit report.

Do NOT proceed to Phase 3 until Phase 2 completion criteria are met:
✅ Single design system implemented
✅ All colors unified
✅ Navigation standardized
✅ Buttons standardized
✅ Forms standardized
✅ Cards standardized
✅ Typography standardized
✅ Spacing standardized
✅ Modals standardized
✅ Responsive design consistent
```

---

## PROMPT 3: PHASE 3 - CODE QUALITY & TESTING
**Duration:** 2 weeks | **Priority:** HIGH

```
I need to execute Phase 3 (Code Quality & Testing) from AUDIT_REMEDIATION.md.

First, read AUDIT_REMEDIATION.md Phase 3 section and CODE_AUDIT_REPORT.md to understand code quality issues and testing requirements.

Then implement all Phase 3 tasks:

WEEK 1: Code Refactoring
- Day 1-3: Split main.py (3338 lines) into modular route files:
  * Create routes/ directory
  * Extract to routes/villages.py
  * Extract to routes/users.py
  * Extract to routes/field_workers.py
  * Extract to routes/admin.py
  * Extract to routes/auth.py
  * Extract to routes/public.py
  * Update main.py as router (should be <500 lines)
- Day 4-5: Extract utilities (utils/geojson_helpers.py, utils/village_sync.py, utils/helpers.py). Extract magic numbers to config.py. Improve global state management (move to app.state).

WEEK 2: Testing Infrastructure
- Day 6-7: Set up pytest framework. Create tests/ directory structure. Create test fixtures (conftest.py, fixtures/test_data.py).
- Day 8-10: Write comprehensive test suite:
  * Unit tests for auth functions, utilities, models (tests/unit/)
  * Integration tests for all API endpoints (tests/integration/)
  * Edge case tests
  * Target: 80%+ code coverage
- Day 11: Performance optimization - identify N+1 queries, add eager loading, implement caching strategy.

Work systematically. After each refactoring, verify application still works. After writing tests, run them and ensure they pass. Document test coverage.

Do NOT proceed to Phase 4 until Phase 3 completion criteria are met:
✅ Code modularized and organized
✅ Test suite implemented (80%+ coverage)
✅ Performance optimized
✅ Code quality improved
```

---

## PROMPT 4: PHASE 4 - DOCUMENTATION & DEPLOYMENT (PART 1: REORGANIZATION & DOCUMENTATION)
**Duration:** 3 days | **Priority:** MEDIUM

```
I need to execute Phase 4 Day 0-3 (Documentation Reorganization & Creation) from AUDIT_REMEDIATION.md.

First, read AUDIT_REMEDIATION.md Phase 4 section and DOCUMENTATION_REORGANIZATION_PLAN.md to understand the SDLC structure.

Then execute:

DAY 0: Documentation Reorganization (PREREQUISITE)
- Task 1: Create SDLC-compliant directory structure:
  * docs/01-requirements/
  * docs/02-design/
  * docs/03-implementation/
  * docs/04-testing/
  * docs/05-deployment/
  * docs/06-user-documentation/
  * docs/07-governance/
  * docs/08-audit/BUG_TRACKING/
  * docs/09-archive/
  * Create README.md in each directory explaining purpose
- Task 2: Move and reorganize ALL existing documentation files according to DOCUMENTATION_REORGANIZATION_PLAN.md:
  * User docs → docs/06-user-documentation/
  * Implementation history → docs/03-implementation/
  * Testing docs → docs/04-testing/
  * Audit docs → docs/08-audit/
  * Historical files → docs/09-archive/
  * etc. (see plan for complete mapping)
- Task 3: Update README.md and all cross-references to new paths.

DAY 1: Requirements & Design Documentation
- Create docs/01-requirements/REQUIREMENTS.md (functional/non-functional requirements, user stories, acceptance criteria)
- Create docs/02-design/DATABASE_SCHEMA.md (ERD)
- Create docs/02-design/API_DESIGN.md
- Create docs/02-design/ARCHITECTURE.md (extract from replit.md)
- Create docs/02-design/DATA_FLOW.md
- Create docs/02-design/UX_DESIGN_SYSTEM.md

DAY 2: Implementation & API Documentation
- Add docstrings to all public functions and classes in Python files
- Create docs/06-user-documentation/API_REFERENCE.md
- Verify FastAPI /docs endpoint works
- Create Postman collection

DAY 3: Testing & Deployment Documentation
- Create docs/04-testing/TEST_PLAN.md
- Create docs/04-testing/TEST_COVERAGE_REPORT.md
- Create docs/05-deployment/DEPLOYMENT_GUIDE.md
- Create docs/05-deployment/ENVIRONMENT_SETUP.md
- Create docs/05-deployment/ROLLBACK_PROCEDURES.md
- Create docs/05-deployment/MONITORING_SETUP.md

Work systematically. Verify all moved files are accessible. Ensure all new documentation is complete and accurate. Update any broken references.

Pause after Day 3 tasks complete. Wait for next prompt for CI/CD and Governance.
```

---

## PROMPT 5: PHASE 4 - DOCUMENTATION & DEPLOYMENT (PART 2: CI/CD & GOVERNANCE) + FINAL VALIDATION
**Duration:** 2 days | **Priority:** MEDIUM

```
I need to execute Phase 4 Day 4-5 (CI/CD & Governance) and perform final validation from AUDIT_REMEDIATION.md.

First, verify Phase 4 Day 0-3 is complete by checking the documentation structure exists and new docs are created.

Then execute:

DAY 4: CI/CD Pipeline Setup
- Create .github/workflows/ci.yml:
  * Automated testing on push/PR
  * Code quality checks (linting with ruff/flake8)
  * Test coverage reporting
- Create .github/workflows/deploy.yml:
  * Staging deployment
  * Production deployment (manual approval)
  * Rollback automation
- Test CI/CD workflows (at minimum verify syntax is correct)

DAY 5: Governance & Versioning
- Create docs/07-governance/CONTRIBUTING.md (contribution guidelines)
- Create docs/07-governance/SECURITY.md (security policy, vulnerability disclosure)
- Create docs/07-governance/CODE_OF_CONDUCT.md
- Create docs/07-governance/VERSIONING.md (versioning strategy)
- Create docs/07-governance/CHANGELOG.md (Keep a Changelog format)
- Tag current version in git (v5.2.0 or appropriate)

FINAL VALIDATION:
After completing Day 4-5, perform complete validation checklist from AUDIT_REMEDIATION.md:
- [ ] Security audit passed (all Phase 1 fixes verified)
- [ ] UI/UX review completed (all Phase 2 fixes verified)
- [ ] Code review completed (Phase 3 refactoring verified)
- [ ] Test coverage > 80% (run pytest with coverage)
- [ ] Performance benchmarks met
- [ ] Documentation complete and in SDLC structure
- [ ] CI/CD pipeline functional (verify workflow files are valid)
- [ ] All cross-references updated
- [ ] README.md updated with new documentation paths

Generate a completion report listing:
1. All tasks completed
2. Files modified/created
3. Any issues encountered
4. Recommendations for next steps

This completes the full remediation plan. Provide a summary of the remediation status.
```

---

## USAGE INSTRUCTIONS

### How to Use These Prompts

1. **Start Fresh Chat**
   - Open a new Cursor chat session
   - These prompts are self-contained

2. **Execute Sequentially**
   - Paste Prompt 1, wait for completion
   - Then paste Prompt 2, wait for completion
   - Continue through Prompt 5

3. **Between Prompts**
   - Review completion summary
   - Verify phase completion criteria
   - Fix any issues before proceeding

4. **If Issues Occur**
   - The prompts reference exact files and line numbers
   - Check AUDIT_REMEDIATION.md for detailed context
   - Check CODE_AUDIT_REPORT.md for specific issues

### Expected Workflow

```
New Chat → Paste Prompt 1 → Wait for Phase 1 Complete
        → Paste Prompt 2 → Wait for Phase 2 Complete  
        → Paste Prompt 3 → Wait for Phase 3 Complete
        → Paste Prompt 4 → Wait for Day 0-3 Complete
        → Paste Prompt 5 → Complete All Remediation
```

---

## QUICK REFERENCE: KEY FILES TO READ

Before starting any prompt, the AI should read:
- `AUDIT_REMEDIATION.md` - Complete remediation plan
- `CODE_AUDIT_REPORT.md` - Detailed audit findings
- `DOCUMENTATION_REORGANIZATION_PLAN.md` - (For Prompt 4 only)

These prompts instruct the AI to read these files first, so they're self-contained.

---

## NOTES FOR OPTIMAL EXECUTION

1. **Each prompt is comprehensive** - They contain all necessary context
2. **File paths are exact** - Use the exact paths from audit reports
3. **Completion criteria included** - Each phase has clear sign-off requirements
4. **Error handling** - Prompts instruct to document issues clearly
5. **Systematic approach** - Work file-by-file, verify after changes

---

**Last Updated:** November 2025  
**Total Prompts:** 5 (covering all 4 phases)  
**Estimated Total Duration:** 8 weeks
