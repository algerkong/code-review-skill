# Code Review Skill

**[中文文档](./README_ZH.md)**

A comprehensive, AI-powered code review skill that generates structured reports with persistent history tracking. Compatible with any AI development tool that supports the skill format (e.g., Claude, Cursor, Windsurf, Cline, etc.).

---

## Features

### 5 Review Modes

| Mode | Description |
|------|-------------|
| **project** | Full repository review — architecture, cross-cutting concerns, dependency health |
| **module** | Directory/package review — cohesion, API surface, boundaries |
| **file** | Single file review — line-level detail, logic, style |
| **diff** | PR/branch diff review — focused on changes |
| **issue** | Issue-targeted review — does the code solve the problem? |

### 6 Review Dimensions

- **Logic & Correctness** — Edge cases, race conditions, error handling, state management
- **Security (OWASP-Aligned)** — Injection, auth, data exposure, secrets, CSRF/SSRF
- **Performance** — N+1 queries, resource leaks, algorithmic complexity, caching
- **Architecture & Design** — Coupling, abstractions, SOLID principles, API design
- **Maintainability** — Naming, function size, test coverage, consistency
- **Project-Level Concerns** — Dependencies, CI/CD, configuration, documentation

### Report System

All reports are stored in the `.review/` directory at the project root:

```
.review/
├── history.json                          # Review history index
├── reports/
│   ├── 2026-03-12_project_full.md       # Project review
│   ├── 2026-03-12_module_src-api.md     # Module review
│   ├── 2026-03-12_file_utils-py.md      # File review
│   ├── 2026-03-12_diff_feature-auth.md  # PR/Branch review
│   └── 2026-03-12_issue_42.md           # Issue review
└── snapshots/                            # Code snapshots for diff tracking
```

Key features:

- **History tracking**: Every review is indexed in `history.json` with timestamps, scope, and finding summaries
- **Previous review comparison**: Before each new review, the system reads the last report for the same scope and compares findings — marking resolved, new, and recurring issues
- **Severity classification**: Critical (🔴), High (🟠), Medium (🟡), Low (🔵), Info (⚪)
- **Confidence scoring**: Only findings with confidence ≥ 70 are included, reducing false positives

### Severity Levels

| Level | Icon | Meaning | Action |
|-------|------|---------|--------|
| Critical | 🔴 | Security vulnerability, data loss, production crash | Must fix before deploy |
| High | 🟠 | Significant bug, performance issue, auth gap | Fix soon |
| Medium | 🟡 | Logic smell, missing edge case, poor error message | Fix when convenient |
| Low | 🔵 | Style inconsistency, naming, minor refactor | Nice to have |
| Info | ⚪ | Observation, praise for good patterns | No action needed |

---

## Project Structure

```
.
├── README.md                     # English documentation (this file)
├── README_ZH.md                  # Chinese documentation
├── LICENSE
├── skills/
│   ├── code-review/              # English version
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── review-checklist.md
│   │   │   └── security-checklist.md
│   │   ├── scripts/
│   │   │   ├── review_history.py
│   │   │   ├── diff_analyzer.py
│   │   │   └── report_generator.py
│   │   └── assets/
│   │       └── report_template.md
│   └── code-review-zh/           # Chinese version
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── assets/
```

---

## Installation

Choose your preferred language version and copy it into your tool's skill directory:

```bash
# English
cp -r skills/code-review/ <your-tool-skills-directory>/code-review/

# Chinese
cp -r skills/code-review-zh/ <your-tool-skills-directory>/code-review/
```

Common skill directory locations:

| Tool | Skill Directory |
|------|----------------|
| Claude Code | `~/.claude/skills/` |
| Claude Desktop | Install via `.skill` package in Skills settings |
| Cursor | `.cursor/skills/` in your project |
| Windsurf | `.windsurf/skills/` in your project |
| Other | Refer to your tool's documentation |

You can also download the `.skill` package from the [Releases](../../releases) page if your tool supports it.

---

## Usage

Once installed, just describe what you want to review in natural language:

```
"Review my project"
"Review the auth module"
"Review src/utils/helpers.ts"
"Review the PR from feature-login branch"
"Review the fix for issue #42"
"Show me the review history"
"What was flagged in the last review?"
```

---

## Helper Scripts

### review_history.py

Manages the `.review/` directory and `history.json`:

```bash
python scripts/review_history.py init <project_root>           # Initialize
python scripts/review_history.py latest <root> --mode project  # Get latest
python scripts/review_history.py add <root> --report-path ...  # Add entry
python scripts/review_history.py stats <root>                  # Show stats
```

### diff_analyzer.py

Analyzes git diffs for review:

```bash
python scripts/diff_analyzer.py branch main feature-login     # Branch diff
python scripts/diff_analyzer.py file-history src/auth.py       # File history
python scripts/diff_analyzer.py summary                        # Repo summary
```

### report_generator.py

Generates structured Markdown reports:

```bash
python scripts/report_generator.py generate --findings '...' --meta '...' --output report.md
python scripts/report_generator.py compare --current new.md --previous old.md
```

---

## Language Support

The review checklist includes language-specific security guidance for:

JavaScript/TypeScript, Python, Java/Kotlin, Go, Rust, C/C++, Ruby, PHP

---

## Recommended: Fix Issues with Superpowers

After running a code review and identifying issues, we recommend using [Superpowers](https://github.com/obra/superpowers) to systematically fix and optimize the problems found.

Superpowers is a markdown-driven AI development methodology framework that includes battle-tested skills like systematic debugging, TDD, and structured refactoring. It pairs perfectly with this code review skill:

1. **Run code review** — identify issues with severity and confidence scoring
2. **Use Superpowers** — leverage its structured workflows to fix issues methodically

```
Code Review Skill          Superpowers
┌──────────────┐          ┌──────────────────┐
│  Scan code   │  ──────> │  Fix issues with │
│  Find issues │          │  structured flow  │
│  Generate    │          │  - Debugging      │
│  report      │          │  - Refactoring    │
└──────────────┘          │  - TDD            │
                          └──────────────────┘
```

---

## Compatibility

This skill follows the standard SKILL.md format and works with any AI-powered development tool that supports skills. If your tool can read a `SKILL.md` file and execute helper scripts, this skill will work out of the box.

---

## License

MIT License

---

## Contributing

Issues and PRs are welcome! If you find the review checklist missing important checks, or want to add support for more languages, feel free to contribute.
