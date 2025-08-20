# CLAUDE\_BASE.md

> **Purpose** — One‑stop guide that Claude Code must read for **every** repository so it can work autonomously yet safely.
> Copy or symlink this file into the repo root as `CLAUDE.md`.
> If other project‑specific guides exist, they may extend (not override) the rules defined here.

---

## TL;DR (Read me first)

* ✅ **Self‑drive**: create branches, write tests, open PRs without waiting for prompts.
* 📐 **Small diffs**: ≤ 200 changed LOC per commit/PR.
* 🧪 **Tests & CI**: run `pytest` and keep coverage ≥ 90 %. CI must be green before asking for review.
* ⛔ **Never** run destructive commands (`rm -rf`, force‑push) unless explicitly whitelisted.
* 🛑 **Escalate** to human when: credentials missing • refactor > 1000 LOC • risk of data loss.

---

## 1 Mind‑set & Principles

1. **Fail fast, fix fast** – execute code/tests early, patch immediately on failure.
2. **Reflect** – after major steps add a *“## Retrospective”* note to the PR summarising lessons & next steps.
3. **Respect safety rails** – prioritise security, privacy, and compliance at all times.

---

## 2 Default Tech Stack

| Area        | Default                                       | Override via                     |
| ----------- | --------------------------------------------- | -------------------------------- |
| Language    | Python 3.12, TypeScript 5.x                   | `runtime.md` or existing configs |
| Lint/Format | `ruff`, `black --line-length 120`, `prettier` | `.ruff.toml`, `.prettierrc`      |
| Tests       | `pytest`, coverage ≥ 90 %                     | `.github/workflows/tests.yml`    |
| CI          | GitHub Actions                                | any other CI config              |

> **Rule**: if the repo already defines its own config files, follow them over these defaults.

---

## 3 Workflow Expectations

1. **Branch naming**: `feat/<scope>`, `fix/<scope>`, `chore/<scope>`.
2. **Commit messages** use *Conventional Commits* format:

   ```
   type(scope): brief summary

   Longer description if required.
   Fixes #123
   ```
3. **Pull Requests** must include:

   * Checklist (tests, docs, lint) ✔️
   * Explanation of *why* rather than just *what*.
4. If CI fails, push follow‑up commits until it passes **before** requesting human review.

---

## 4 Coding Conventions

### Python

* Follow PEP 8; use type hints; Google‑style docstrings.
* Keep functions < 50 LOC when reasonable.

### JavaScript / TypeScript

* ESLint **airbnb‑base**; enable `strictNullChecks`.

### Databases

* Use Alembic (SQL) or Prisma (JS) for migrations; ensure they are reversible.

### Secrets

* Never commit credentials. Provide `.env.example` showing required keys.

### Documentation

* Public functions/classes need at least one usage example in docs or tests.

### Temporary / Experimental Scripts

* Store ad‑hoc or throw‑away scripts in a dedicated `scripts/tmp/` (or `_sandbox/`) directory **outside** production paths.
* Prefix filenames with `tmp_` or include the date, e.g. `tmp_2025‑07‑11_data_patch.py`, for easy grepping.
* Once the experiment is complete **delete** the script or convert it into a proper test/utility; never leave dead code in `main` or `src`.
* CI should fail if `scripts/tmp/` contains files older than 30 days (enforce via a lightweight check script).

---

## 5 Documentation & Knowledge Artefacts

1. Maintain **`CHANGELOG.md`** (Keep‑a‑Changelog spec).
2. Record major decisions in **`docs/ADR‑XXXX.md`** (Architecture Decision Record).
3. When architecture changes, generate/update diagrams in `docs/diagrams/` (PlantUML or `python -m diagrams`).

---

## 6 Testing Strategy

* Start with unit tests; add light integration tests.
* Include **regression tests** for every bug fix.
* Fail CI if performance degrades > 10 % vs previous baseline.

---

## 7 Security & Compliance

* Run `pip-audit` (Python) or `npm audit` (Node) weekly; open an Issue for any high‑severity vulnerability.
* Follow OWASP Top‑10; redact PII in logs; comply with GDPR where relevant.
* Validate or escape all user‑supplied strings used in shell or SQL contexts.

---

## 8 Deployment & Operations

* Provide a **Dockerfile** that builds via `docker build .` without cache.
* Offer `make deploy-staging` and `make deploy-prod` targets.
* Generate a software‑bill‑of‑materials (SBOM) using CycloneDX or Syft and attach it to releases.

---

## 9 Interaction Tone & Style (Chat)

* Friendly peer vibe (“やさしい同級生 + コンサルパートナー”).
* Lead with conclusions; use bullet points for reasons when asked.
* Apologise only for genuine mistakes.

---

## 10 Autonomy Escalation Matrix

| Trigger                 | Required Action                                            |
| ----------------------- | ---------------------------------------------------------- |
| **Missing credentials** | Ask user once; if unavailable, stub feature + TODO comment |
| **>1000 LOC refactor**  | Generate `docs/refactor_plan.md`, request approval         |
| **Potential data loss** | Pause and request explicit `CONFIRM: <action>` token       |

---

*End of CLAUDE\_BASE.md*
