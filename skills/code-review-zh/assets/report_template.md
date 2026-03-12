# Code Review Report

## Meta

| Field | Value |
|-------|-------|
| **Date** | {{DATE}} |
| **Reviewer** | Claude (AI-assisted review) |
| **Mode** | {{MODE}} |
| **Scope** | {{SCOPE}} |
| **Previous Review** | {{PREVIOUS_REVIEW}} |
| **Tech Stack** | {{TECH_STACK}} |
| **Git Branch** | {{BRANCH}} |
| **Git Commit** | {{COMMIT}} |

---

## Executive Summary

{{EXECUTIVE_SUMMARY}}

---

## Statistics

| Metric | Count |
|--------|-------|
| Files analyzed | {{FILES_ANALYZED}} |
| Total findings | {{TOTAL_FINDINGS}} |
| 🔴 Critical | {{CRITICAL_COUNT}} |
| 🟠 High | {{HIGH_COUNT}} |
| 🟡 Medium | {{MEDIUM_COUNT}} |
| 🔵 Low | {{LOW_COUNT}} |
| ⚪ Info | {{INFO_COUNT}} |

### Compared to Previous Review

| Status | Count |
|--------|-------|
| ✅ Resolved | {{RESOLVED_COUNT}} |
| 🆕 New | {{NEW_COUNT}} |
| 🔄 Recurring | {{RECURRING_COUNT}} |

---

## Findings

### 🔴 Critical

<!--
For each finding, use this format:

#### [C-001] Finding Title
- **File**: `path/to/file.ext:line_number`
- **Dimension**: Security | Logic | Performance | Architecture | Maintainability
- **Confidence**: N/100
- **Description**: What the issue is and why it matters
- **Evidence**: The specific code or pattern that triggered this finding
- **Suggested Fix**: How to resolve it, with code example if helpful
- **References**: Links to relevant documentation, CWE, OWASP, etc.
-->

{{CRITICAL_FINDINGS}}

### 🟠 High

{{HIGH_FINDINGS}}

### 🟡 Medium

{{MEDIUM_FINDINGS}}

### 🔵 Low

{{LOW_FINDINGS}}

### ⚪ Info (Observations & Praise)

{{INFO_FINDINGS}}

---

## Comparison with Previous Review

### ✅ Resolved Issues

{{RESOLVED_ISSUES}}

### 🆕 New Issues

{{NEW_ISSUES}}

### 🔄 Recurring Issues

{{RECURRING_ISSUES}}

---

## Recommendations

### Immediate Actions (this sprint)

{{IMMEDIATE_ACTIONS}}

### Short-term Improvements (next 2 sprints)

{{SHORT_TERM}}

### Long-term Architecture Notes

{{LONG_TERM}}

---

## Appendix

### Files Reviewed

{{FILES_LIST}}

### Review Dimension Coverage

| Dimension | Depth | Notes |
|-----------|-------|-------|
| Logic & Correctness | {{LOGIC_DEPTH}} | {{LOGIC_NOTES}} |
| Security | {{SECURITY_DEPTH}} | {{SECURITY_NOTES}} |
| Performance | {{PERFORMANCE_DEPTH}} | {{PERFORMANCE_NOTES}} |
| Architecture | {{ARCH_DEPTH}} | {{ARCH_NOTES}} |
| Maintainability | {{MAINT_DEPTH}} | {{MAINT_NOTES}} |

### Methodology Notes

{{METHODOLOGY_NOTES}}
