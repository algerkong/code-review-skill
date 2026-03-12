---
name: code-review
description: "**Comprehensive Code Review System**: Multi-dimensional code review with persistent report history, supporting project-wide, module-level, single-file, PR/branch diff, and issue-targeted reviews. Generates structured Markdown reports in `.review/` with severity-rated findings, tracks review history, and compares against previous reviews to surface regressions and improvements. MANDATORY TRIGGERS: code review, review code, review project, review module, review file, PR review, pull request review, branch review, diff review, code audit, code quality check, security review, review my code, 审查代码, 代码审查, review this, check code quality. Use this skill whenever the user wants any form of code analysis, code quality assessment, security audit, or review — even if they don't say 'review' explicitly but describe wanting to 'check', 'audit', 'inspect', or 'analyze' their codebase for issues."
---

# Code Review System

A comprehensive, multi-dimensional code review skill that produces structured reports, tracks review history, and supports multiple review scopes — from a single file to an entire project.

## Core Principles

This skill is built on the methodology used by production-grade review systems (multi-agent parallel analysis, confidence-based filtering, OWASP-aligned security checks). The goal is to give the developer a thorough, actionable report — not a wall of nitpicks. Every finding should earn its place in the report by being genuinely useful.

Focus on **substance over ceremony**: a critical logic bug matters more than a missing trailing newline. When in doubt, ask "would a senior engineer care about this?"

## Review Modes

This skill supports five review modes. Determine the mode from the user's request:

| Mode | Trigger | Scope |
|------|---------|-------|
| **project** | "review my project", "review the codebase" | Entire repository — architecture, cross-cutting concerns, dependency health |
| **module** | "review the auth module", "review src/api/" | A directory/package — internal cohesion, API surface, module boundaries |
| **file** | "review this file", "review utils.py" | Single file — line-level detail, logic correctness, style |
| **diff** | "review my PR", "review this branch", "review changes" | Git diff between branches/commits — focused on what changed |
| **issue** | "review issue #42", "review the fix for the login bug" | Targeted review around a specific issue — does the code actually solve it? |

If the user doesn't specify a mode, infer from context. If ambiguous, ask.

## Workflow

Every review follows this pipeline:

### Step 1: Preparation — Know the Territory

Before reading a single line of code, gather context:

1. **Check for previous reports**: Read `.review/history.json` (if it exists) and the most recent report for this scope. This is essential — it tells you what was flagged before, what was resolved, and what's regressed.

2. **Understand the project**: Look at the project structure, `README`, config files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.) to understand the tech stack, frameworks, and conventions.

3. **For diff mode**: Run `git log` and `git diff` to understand what changed and why. Read PR description or commit messages if available.

4. **For issue mode**: Understand the issue context first — what's the bug/feature, what's the expected behavior, then trace the relevant code paths.

### Step 2: Multi-Dimensional Analysis

Review the code across these dimensions (adjust depth based on review mode):

#### Dimension 1: Logic & Correctness
- Does the code do what it claims to do?
- Edge cases: null/undefined, empty collections, boundary values, overflow
- Race conditions in concurrent code
- Error handling: are failures caught, propagated correctly, and recoverable?
- State management: can the system reach invalid states?

#### Dimension 2: Security (OWASP-Aligned)
- **Injection**: SQL, XSS, command injection, path traversal — are inputs validated?
- **Auth**: Authentication and authorization checked on every path?
- **Data exposure**: Sensitive data logged, leaked in errors, or sent unencrypted?
- **Dependencies**: Known vulnerabilities in third-party packages?
- **Secrets**: Hardcoded credentials, API keys, tokens?
- **CSRF/SSRF**: State-changing requests protected?

#### Dimension 3: Performance
- N+1 queries, unbounded loops, unnecessary allocations in hot paths
- Resource leaks: unclosed connections, file handles, streams
- Algorithmic complexity vs. expected data volume
- Caching opportunities, unnecessary recomputation
- Blocking calls that should be async

#### Dimension 4: Architecture & Design
- Does the change fit the existing architecture or fight it?
- Coupling: does this create hidden dependencies across modules?
- Abstractions: are they at the right level, or leaky?
- SOLID principles: single responsibility, dependency inversion
- API design: is the public interface clear and minimal?

#### Dimension 5: Maintainability & Readability
- Naming: do names reveal intent?
- Functions: small, single-purpose, one abstraction level?
- Comments: explain "why" not "what"? Dead code removed?
- Test coverage: are behavior-critical paths tested?
- Consistency with project conventions

#### Dimension 6: Project-Level Concerns (project mode only)
- Dependency health: outdated packages, license conflicts
- Configuration hygiene: env vars, secrets management
- CI/CD: are pipelines configured correctly?
- Documentation: README accuracy, API docs
- Code organization: is the project structure logical and navigable?

### Step 3: Severity Classification

Every finding gets a severity level. Be honest and calibrated — inflation of severity destroys trust.

| Level | Icon | Meaning | Action Required |
|-------|------|---------|-----------------|
| **CRITICAL** | 🔴 | Security vulnerability, data loss risk, crash in production | Must fix before merge/deploy |
| **HIGH** | 🟠 | Significant bug, performance issue under real load, auth gap | Should fix soon |
| **MEDIUM** | 🟡 | Logic smell, missing edge case handling, poor error message | Fix when convenient |
| **LOW** | 🔵 | Style inconsistency, naming improvement, minor refactor opportunity | Nice to have |
| **INFO** | ⚪ | Observation, praise for good patterns, architecture note | No action needed |

**Confidence scoring**: For each finding, internally assess your confidence (0-100). Only include findings where confidence ≥ 70. If you're guessing, say so. False positives erode trust faster than missed bugs.

### Step 4: Generate Report

Reports go in the `.review/` directory at the project root. Create it if it doesn't exist.

**Report naming convention**:
```
.review/
├── history.json                          # Review history index
├── reports/
│   ├── 2026-03-12_project_full.md       # Project review
│   ├── 2026-03-12_module_src-api.md     # Module review (path encoded)
│   ├── 2026-03-12_file_utils-py.md      # File review
│   ├── 2026-03-12_diff_feature-auth.md  # Diff/PR review (branch name)
│   └── 2026-03-12_issue_42.md           # Issue review
└── snapshots/                            # (optional) Code snapshots for diff tracking
```

**Report format** — use the template in `assets/report_template.md`. Key sections:

```markdown
# Code Review Report

## Meta
- **Date**: YYYY-MM-DD HH:MM
- **Reviewer**: Claude (AI-assisted review)
- **Mode**: project | module | file | diff | issue
- **Scope**: [what was reviewed — path, branch, issue number]
- **Previous Review**: [link to previous report if exists, or "First review"]
- **Tech Stack**: [detected languages, frameworks]

## Executive Summary
[2-3 sentences: overall health assessment, most critical finding, key recommendation]

## Statistics
- Files analyzed: N
- Total findings: N (Critical: N, High: N, Medium: N, Low: N, Info: N)
- Compared to previous review: +N new / -N resolved / N recurring

## Critical & High Findings
[Detailed findings with file, line, description, suggested fix]

## Medium Findings
[...]

## Low & Info Findings
[...]

## Comparison with Previous Review
### Resolved Issues (from previous report)
### New Issues (not in previous report)
### Recurring Issues (still present)

## Recommendations
### Immediate Actions (this sprint)
### Short-term Improvements (next 2 sprints)
### Long-term Architecture Notes

## Appendix
### Files Reviewed
### Review Checklist Coverage
```

### Step 5: Update History

After generating the report, update `.review/history.json`:

```json
{
  "project": "project-name",
  "reviews": [
    {
      "id": "review-2026-03-12-001",
      "date": "2026-03-12T14:30:00Z",
      "mode": "project",
      "scope": "full project",
      "report_path": "reports/2026-03-12_project_full.md",
      "summary": {
        "total_findings": 15,
        "critical": 1,
        "high": 3,
        "medium": 6,
        "low": 4,
        "info": 1
      },
      "resolved_from_previous": 3,
      "new_findings": 5,
      "recurring_findings": 7
    }
  ]
}
```

## Mode-Specific Instructions

### Project Review
1. Start with a high-level scan: `find` for file types, check directory structure, read config files
2. Identify the most critical modules (auth, payment, data access) — review those deeply
3. Sample other modules — you don't need to read every file, but cover enough to spot patterns
4. Check cross-cutting concerns: logging, error handling patterns, configuration management
5. Review dependency manifests for outdated/vulnerable packages
6. Use subagents if available: spawn parallel reviewers for different dimensions

### Module Review
1. Map the module boundary: what's the public API, what's internal?
2. Review all files in the module
3. Check internal cohesion — do all files belong here?
4. Check coupling — what does this module depend on, and what depends on it?
5. Evaluate the module's test coverage

### File Review
1. Read the entire file
2. Understand its role in the broader codebase (read imports, find callers)
3. Line-by-line analysis with all dimensions
4. This is the most detailed mode — include LOW findings

### Diff Review (PR/Branch)
1. Get the diff: `git diff <base>...<head>` or `git diff <base> <head>`
2. Read the PR description / commit messages for intent
3. For each changed file, understand the context around the change (not just the diff lines)
4. Focus review on: does this change do what it says? Does it break anything? Does it introduce risk?
5. Check: are there tests for the new behavior?
6. Compare against `.review/` history for the affected files

### Issue Review
1. Understand the issue (read the issue description, comments, linked PRs)
2. Identify the code paths relevant to the issue
3. Review those specific paths deeply
4. Assess: does the current code (or proposed fix) actually address the root cause?
5. Check for similar patterns elsewhere that might have the same issue

## Handling Different Languages

The review checklist applies universally, but adjust emphasis:

- **JavaScript/TypeScript**: Focus on async/await pitfalls, type safety (TS), prototype pollution, XSS
- **Python**: Focus on type hints usage, import organization, Django/Flask security, resource management
- **Java/Kotlin**: Focus on null safety, concurrency, Spring security config, memory leaks
- **Go**: Focus on error handling patterns, goroutine leaks, interface design
- **Rust**: Focus on unsafe blocks, lifetime issues, error handling with Result
- **C/C++**: Focus on memory safety, buffer overflows, RAII patterns, undefined behavior
- **Ruby**: Focus on Rails security, metaprogramming complexity, SQL injection via ActiveRecord
- **PHP**: Focus on injection vulnerabilities, type juggling, authentication patterns

## Working with Git

Common git commands for review context:

```bash
# Branch diff
git diff main...feature-branch
git log main..feature-branch --oneline

# Recent changes
git log --oneline -20
git diff HEAD~5..HEAD

# File history
git log --follow -p -- path/to/file

# Find related changes
git log --all --grep="issue-keyword"

# Check for merge conflicts
git merge-tree $(git merge-base main feature) main feature
```

## Quality Standards for the Report Itself

The report is a deliverable — it should be professional and useful:

- Every finding has: location (file:line), description, severity, and a suggested fix or direction
- The executive summary is genuinely useful to a busy tech lead (can they decide "merge or not?" from it?)
- Comparisons with previous reports are specific ("Issue #3 from the March 5th review is now resolved")
- Recommendations are prioritized and actionable, not vague ("improve code quality" is useless)
- When you're not sure about something, say so — "This pattern *might* cause issues under high concurrency, but I'd need to see the actual load profile to be certain"

## Reference Files

For detailed checklists, read:
- `references/review-checklist.md` — Full 40-point review checklist organized by dimension
- `references/security-checklist.md` — OWASP-aligned security review checklist

## Important Reminders

- **Always check previous reports first**. This is what makes the review system valuable over time — it creates institutional memory. Skipping this step means you'll re-report resolved issues and miss regressions.
- **Calibrate severity honestly**. If everything is CRITICAL, nothing is. A review that correctly identifies 3 real issues is worth more than one that flags 30 false alarms.
- **Be constructive**. Every criticism should come with a suggested path forward. "This is wrong" is not helpful. "This is vulnerable to SQL injection — use parameterized queries like this: [example]" is.
- **Praise good patterns**. Use INFO-level findings to call out well-written code. This makes the review feel balanced and encourages good practices.
