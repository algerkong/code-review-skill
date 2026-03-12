# 代码审查技能

**[English](./README.md)**

一个全面的 AI 代码审查技能，生成结构化报告并持久追踪审查历史。兼容所有支持技能格式的 AI 开发工具（如 Claude、Cursor、Windsurf、Cline 等）。

---

## 功能特性

### 5 种审查模式

| 模式 | 说明 |
|------|------|
| **项目** | 全仓库审查 — 架构、横切关注点、依赖健康度 |
| **模块** | 目录/包审查 — 内聚性、API 接口、模块边界 |
| **文件** | 单文件审查 — 行级细节、逻辑正确性、风格 |
| **差异** | PR/分支差异审查 — 聚焦变更内容 |
| **Issue** | 针对特定 Issue 审查 — 代码是否真正解决了问题？ |

### 6 个审查维度

- **逻辑正确性** — 边界情况、竞态条件、错误处理、状态管理
- **安全性（OWASP 对齐）** — 注入、认证授权、数据泄露、密钥、CSRF/SSRF
- **性能** — N+1 查询、资源泄漏、算法复杂度、缓存
- **架构设计** — 耦合性、抽象层次、SOLID 原则、API 设计
- **可维护性** — 命名、函数大小、测试覆盖、一致性
- **项目级关注** — 依赖项、CI/CD、配置、文档

### 报告系统

所有报告存储在项目根目录的 `.review/` 文件夹中：

```
.review/
├── history.json                          # 审查历史索引
├── reports/
│   ├── 2026-03-12_project_full.md       # 项目审查
│   ├── 2026-03-12_module_src-api.md     # 模块审查
│   ├── 2026-03-12_file_utils-py.md      # 文件审查
│   ├── 2026-03-12_diff_feature-auth.md  # PR/分支审查
│   └── 2026-03-12_issue_42.md           # Issue 审查
└── snapshots/                            # 用于差异追踪的代码快照
```

核心特性：

- **历史追踪**：每次审查都在 `history.json` 中编入索引，包含时间戳、范围和发现摘要
- **前次审查对比**：每次新审查前，系统读取同一范围的上次报告 — 标记已解决、新增和持续存在的问题
- **严重级别分类**：严重（🔴）、高（🟠）、中（🟡）、低（🔵）、信息（⚪）
- **置信度评分**：仅纳入置信度 ≥ 70 的发现，减少误报

### 严重级别

| 级别 | 图标 | 含义 | 所需操作 |
|------|------|------|----------|
| 严重 | 🔴 | 安全漏洞、数据丢失、生产环境崩溃 | 部署前必须修复 |
| 高 | 🟠 | 重要 bug、性能问题、认证缺口 | 尽快修复 |
| 中 | 🟡 | 逻辑异味、缺少边界处理、糟糕的错误信息 | 方便时修复 |
| 低 | 🔵 | 风格不一致、命名改进、小型重构 | 锦上添花 |
| 信息 | ⚪ | 观察、对良好模式的表扬 | 无需操作 |

---

## 项目结构

```
.
├── README.md                     # 英文文档
├── README_ZH.md                  # 中文文档（本文件）
├── LICENSE
├── skills/
│   ├── code-review/              # 英文版
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
│   └── code-review-zh/           # 中文版
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── assets/
```

---

## 安装

选择你偏好的语言版本，复制到你的工具技能目录中：

```bash
# 英文版
cp -r skills/code-review/ <你的工具技能目录>/code-review/

# 中文版
cp -r skills/code-review-zh/ <你的工具技能目录>/code-review/
```

常见技能目录位置：

| 工具 | 技能目录 |
|------|---------|
| Claude Code | `~/.claude/skills/` |
| Claude Desktop | 在技能设置中通过 `.skill` 包安装 |
| Cursor | 项目中的 `.cursor/skills/` |
| Windsurf | 项目中的 `.windsurf/skills/` |
| 其他 | 请参考你的工具文档 |

也可以从 [Releases](../../releases) 页面下载 `.skill` 包（如果你的工具支持）。

---

## 使用方法

安装后，用自然语言描述你想审查的内容：

```
"审查整个项目"
"审查 auth 模块"
"审查 src/utils/helpers.ts 这个文件"
"审查 feature-login 分支的 PR"
"审查 issue #42 的修复代码"
"查看审查历史"
"上次审查发现了什么？"
```

---

## 辅助脚本

### review_history.py

管理 `.review/` 目录和 `history.json` 历史记录：

```bash
python scripts/review_history.py init <项目根目录>               # 初始化
python scripts/review_history.py latest <根目录> --mode project  # 获取最近审查
python scripts/review_history.py add <根目录> --report-path ...  # 添加记录
python scripts/review_history.py stats <根目录>                  # 显示统计
```

### diff_analyzer.py

分析 Git 差异用于审查：

```bash
python scripts/diff_analyzer.py branch main feature-login     # 分支对比
python scripts/diff_analyzer.py file-history src/auth.py       # 文件历史
python scripts/diff_analyzer.py summary                        # 仓库概览
```

### report_generator.py

生成结构化 Markdown 报告：

```bash
python scripts/report_generator.py generate --findings '...' --meta '...' --output report.md
python scripts/report_generator.py compare --current new.md --previous old.md
```

---

## 语言支持

审查清单包含以下编程语言的安全陷阱指南：

JavaScript/TypeScript、Python、Java/Kotlin、Go、Rust、C/C++、Ruby、PHP

---

## 推荐：使用 Superpowers 修复问题

在运行代码审查并发现问题后，推荐使用 [Superpowers](https://github.com/obra/superpowers) 来系统性地修复和优化发现的问题。

1. **运行代码审查** — 通过严重级别和置信度评分识别问题
2. **使用 Superpowers** — 利用其结构化工作流有条不紊地修复问题

```
Code Review Skill          Superpowers
┌──────────────┐          ┌──────────────────┐
│  扫描代码     │  ──────> │  结构化修复问题   │
│  发现问题     │          │  - 系统性调试     │
│  生成报告     │          │  - 重构优化       │
│              │          │  - TDD           │
└──────────────┘          └──────────────────┘
```

---

## 兼容性

本技能遵循标准 SKILL.md 格式，可与任何支持技能的 AI 开发工具配合使用。只要你的工具能读取 `SKILL.md` 文件并执行辅助脚本，即可开箱即用。

---

## 许可证

MIT 许可证

---

## 贡献

欢迎提交 Issue 和 PR！如果你发现审查清单缺少重要检查项，或想添加更多语言支持，欢迎贡献。
