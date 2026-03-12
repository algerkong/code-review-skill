# Code Review Skill / 代码审查技能

A comprehensive, AI-powered code review skill for Claude that generates structured reports with persistent history tracking.

一个为 Claude 打造的全面 AI 代码审查技能，生成结构化报告并持久追踪审查历史。

---

## Features / 功能特性

### 5 Review Modes / 5 种审查模式

| Mode | Description | 模式 | 说明 |
|------|-------------|------|------|
| **project** | Full repository review — architecture, cross-cutting concerns, dependency health | **项目** | 全仓库审查 — 架构、横切关注点、依赖健康度 |
| **module** | Directory/package review — cohesion, API surface, boundaries | **模块** | 目录/包审查 — 内聚性、API 接口、模块边界 |
| **file** | Single file review — line-level detail, logic, style | **文件** | 单文件审查 — 行级细节、逻辑、风格 |
| **diff** | PR/branch diff review — focused on changes | **差异** | PR/分支差异审查 — 聚焦变更内容 |
| **issue** | Issue-targeted review — does the code solve the problem? | **问题** | 针对特定 Issue 审查 — 代码是否解决了问题？ |

### 6 Review Dimensions / 6 个审查维度

- **Logic & Correctness** / 逻辑正确性 — Edge cases, race conditions, error handling
- **Security (OWASP-Aligned)** / 安全性（OWASP 对齐）— Injection, auth, data exposure, secrets
- **Performance** / 性能 — N+1 queries, resource leaks, algorithmic complexity
- **Architecture & Design** / 架构设计 — Coupling, abstractions, SOLID principles
- **Maintainability** / 可维护性 — Naming, function size, test coverage, consistency
- **Project-Level Concerns** / 项目级关注 — Dependencies, CI/CD, configuration, documentation

### Report System / 报告系统

All reports are stored in the `.review/` directory at the project root:

所有报告存储在项目根目录的 `.review/` 文件夹中：

```
.review/
├── history.json                          # Review history index / 审查历史索引
├── reports/
│   ├── 2026-03-12_project_full.md       # Project review / 项目审查
│   ├── 2026-03-12_module_src-api.md     # Module review / 模块审查
│   ├── 2026-03-12_file_utils-py.md      # File review / 文件审查
│   ├── 2026-03-12_diff_feature-auth.md  # PR/Branch review / PR/分支审查
│   └── 2026-03-12_issue_42.md           # Issue review / Issue审查
└── snapshots/                            # Code snapshots / 代码快照
```

Key features of the report system / 报告系统核心特性:

- **History tracking** / 历史追踪: Every review is indexed in `history.json` with timestamps, scope, and finding summaries
- **Previous review comparison** / 前次审查对比: Before each new review, the system reads the last report for the same scope and compares findings — marking resolved, new, and recurring issues
- **Severity classification** / 严重级别分类: Critical (🔴), High (🟠), Medium (🟡), Low (🔵), Info (⚪)
- **Confidence scoring** / 置信度评分: Only findings with confidence ≥ 70 are included — reducing false positives

### Severity Levels / 严重级别

| Level | Icon | Meaning | Action |
|-------|------|---------|--------|
| Critical | 🔴 | Security vulnerability, data loss, production crash | Must fix before deploy / 部署前必须修复 |
| High | 🟠 | Significant bug, performance issue, auth gap | Fix soon / 尽快修复 |
| Medium | 🟡 | Logic smell, missing edge case, poor error message | Fix when convenient / 方便时修复 |
| Low | 🔵 | Style inconsistency, naming, minor refactor | Nice to have / 锦上添花 |
| Info | ⚪ | Observation, praise for good patterns | No action / 无需操作 |

---

## Project Structure / 项目结构

```
.
├── README.md
├── LICENSE
├── skills/
│   ├── code-review/              # English version / 英文版
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
│   └── code-review-zh/           # Chinese version / 中文版
│       ├── SKILL.md
│       ├── references/
│       │   ├── review-checklist.md
│       │   └── security-checklist.md
│       ├── scripts/
│       │   ├── review_history.py
│       │   ├── diff_analyzer.py
│       │   └── report_generator.py
│       └── assets/
│           └── report_template.md
```

---

## Installation / 安装

### As a Claude Skill / 作为 Claude 技能安装

Choose the language version you prefer / 选择你偏好的语言版本：

- **English**: Copy `skills/code-review/` to your Claude skills folder
- **中文**: 将 `skills/code-review-zh/` 复制到你的 Claude 技能文件夹

```bash
# English
cp -r skills/code-review/ ~/.claude/skills/code-review/

# 中文
cp -r skills/code-review-zh/ ~/.claude/skills/code-review/
```

### From .skill Package / 从 .skill 包安装

Download the `.skill` file from the [Releases](../../releases) page, then install it in Claude Desktop's Skills settings.

从 [Releases](../../releases) 页面下载 `.skill` 文件，在 Claude Desktop 技能设置中安装。

---

## Usage / 使用方法

Once installed, just tell Claude what you want to review / 安装后，直接告诉 Claude 你想审查什么：

```
# English
"Review my project"
"Review the auth module"
"Review src/utils/helpers.ts"
"Review the PR from feature-login branch"
"Review the fix for issue #42"

# 中文
"审查整个项目"
"审查 auth 模块"
"审查 src/utils/helpers.ts 这个文件"
"审查 feature-login 分支的 PR"
"审查 issue #42 的修复代码"
```

### Check Review History / 查看审查历史

```
"Show me the review history"
"What was flagged in the last review?"
"查看审查历史"
"上次审查发现了什么？"
```

---

## Helper Scripts / 辅助脚本

### review_history.py

Manages the `.review/` directory and `history.json` / 管理审查目录和历史记录：

```bash
python scripts/review_history.py init <project_root>           # Initialize / 初始化
python scripts/review_history.py latest <root> --mode project  # Get latest / 获取最近
python scripts/review_history.py add <root> --report-path ...  # Add entry / 添加记录
python scripts/review_history.py stats <root>                  # Show stats / 显示统计
```

### diff_analyzer.py

Analyzes git diffs for review / 分析 Git 差异用于审查：

```bash
python scripts/diff_analyzer.py branch main feature-login     # Branch diff / 分支对比
python scripts/diff_analyzer.py file-history src/auth.py       # File history / 文件历史
python scripts/diff_analyzer.py summary                        # Repo summary / 仓库概览
```

### report_generator.py

Generates structured Markdown reports / 生成结构化 Markdown 报告：

```bash
python scripts/report_generator.py generate --findings '...' --meta '...' --output report.md
python scripts/report_generator.py compare --current new.md --previous old.md
```

---

## Language Support / 语言支持

The review checklist includes language-specific security guidance for / 审查清单包含以下语言的安全指南：

JavaScript/TypeScript, Python, Java/Kotlin, Go, Rust, C/C++, Ruby, PHP

---

## License / 许可证

MIT License

---

## Contributing / 贡献

Issues and PRs are welcome! / 欢迎提交 Issue 和 PR！

If you find the review checklist missing important checks, or want to add support for more languages, feel free to contribute.

如果你发现审查清单缺少重要检查项，或想添加更多语言支持，欢迎贡献。
