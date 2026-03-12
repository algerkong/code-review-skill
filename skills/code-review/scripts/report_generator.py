#!/usr/bin/env python3
"""
Report Generator for Code Review

Generates the final review report from structured findings data.
Also handles comparison with previous reports to identify resolved/new/recurring issues.

Usage:
    python report_generator.py generate --findings FINDINGS_JSON --meta META_JSON --output PATH
    python report_generator.py compare --current REPORT --previous REPORT
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def generate_report(findings_json: str, meta_json: str, output_path: str, template_path: str = None) -> str:
    """Generate a markdown review report from structured findings data."""

    findings = json.loads(findings_json) if isinstance(findings_json, str) else findings_json
    meta = json.loads(meta_json) if isinstance(meta_json, str) else meta_json

    # Read template if available
    if template_path and os.path.exists(template_path):
        with open(template_path) as f:
            template = f.read()
    else:
        template = None

    # Categorize findings by severity
    severity_order = ["critical", "high", "medium", "low", "info"]
    severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}
    categorized = {s: [] for s in severity_order}

    for finding in findings:
        sev = finding.get("severity", "info").lower()
        if sev in categorized:
            categorized[sev].append(finding)

    # Count stats
    counts = {s: len(categorized[s]) for s in severity_order}
    total = sum(counts.values())

    # Generate findings sections
    def format_finding(f, prefix, idx):
        lines = [f"#### [{prefix}-{idx:03d}] {f.get('title', 'Untitled Finding')}"]
        lines.append(f"- **File**: `{f.get('file', 'unknown')}`")
        lines.append(f"- **Dimension**: {f.get('dimension', 'General')}")
        if f.get("confidence"):
            lines.append(f"- **Confidence**: {f['confidence']}/100")
        lines.append(f"- **Description**: {f.get('description', '')}")
        if f.get("evidence"):
            lines.append(f"- **Evidence**:")
            lines.append(f"  ```")
            lines.append(f"  {f['evidence']}")
            lines.append(f"  ```")
        if f.get("suggested_fix"):
            lines.append(f"- **Suggested Fix**: {f['suggested_fix']}")
        if f.get("references"):
            lines.append(f"- **References**: {f['references']}")
        lines.append("")
        return "\n".join(lines)

    prefix_map = {"critical": "C", "high": "H", "medium": "M", "low": "L", "info": "I"}

    sections = {}
    for sev in severity_order:
        if categorized[sev]:
            section_lines = []
            for i, f in enumerate(categorized[sev], 1):
                section_lines.append(format_finding(f, prefix_map[sev], i))
            sections[sev] = "\n".join(section_lines)
        else:
            sections[sev] = "_No findings at this severity level._\n"

    # Build comparison section
    comparison = meta.get("comparison", {})
    resolved = comparison.get("resolved", [])
    new_issues = comparison.get("new", [])
    recurring = comparison.get("recurring", [])

    resolved_text = "\n".join([f"- ~~{r}~~" for r in resolved]) if resolved else "_No resolved issues (first review or no previous review)._"
    new_text = "\n".join([f"- {n}" for n in new_issues]) if new_issues else "_No new issues compared to previous review._"
    recurring_text = "\n".join([f"- {r}" for r in recurring]) if recurring else "_No recurring issues._"

    # Build the report
    now = datetime.now(timezone.utc)
    report = f"""# Code Review Report

## Meta

| Field | Value |
|-------|-------|
| **Date** | {now.strftime('%Y-%m-%d %H:%M UTC')} |
| **Reviewer** | Claude (AI-assisted review) |
| **Mode** | {meta.get('mode', 'unknown')} |
| **Scope** | {meta.get('scope', 'unknown')} |
| **Previous Review** | {meta.get('previous_review', 'First review')} |
| **Tech Stack** | {meta.get('tech_stack', 'Not detected')} |
| **Git Branch** | {meta.get('branch', 'N/A')} |
| **Git Commit** | {meta.get('commit', 'N/A')} |

---

## Executive Summary

{meta.get('executive_summary', 'Review completed. See findings below.')}

---

## Statistics

| Metric | Count |
|--------|-------|
| Files analyzed | {meta.get('files_analyzed', 0)} |
| Total findings | {total} |
| 🔴 Critical | {counts['critical']} |
| 🟠 High | {counts['high']} |
| 🟡 Medium | {counts['medium']} |
| 🔵 Low | {counts['low']} |
| ⚪ Info | {counts['info']} |

### Compared to Previous Review

| Status | Count |
|--------|-------|
| ✅ Resolved | {len(resolved)} |
| 🆕 New | {len(new_issues)} |
| 🔄 Recurring | {len(recurring)} |

---

## Findings

### 🔴 Critical

{sections['critical']}

### 🟠 High

{sections['high']}

### 🟡 Medium

{sections['medium']}

### 🔵 Low

{sections['low']}

### ⚪ Info (Observations & Praise)

{sections['info']}

---

## Comparison with Previous Review

### ✅ Resolved Issues

{resolved_text}

### 🆕 New Issues

{new_text}

### 🔄 Recurring Issues

{recurring_text}

---

## Recommendations

### Immediate Actions (this sprint)

{meta.get('recommendations', {}).get('immediate', '_No immediate actions required._')}

### Short-term Improvements (next 2 sprints)

{meta.get('recommendations', {}).get('short_term', '_No short-term improvements identified._')}

### Long-term Architecture Notes

{meta.get('recommendations', {}).get('long_term', '_No long-term notes._')}

---

## Appendix

### Files Reviewed

{meta.get('files_list', '_See scope above._')}

### Review Dimension Coverage

| Dimension | Depth | Notes |
|-----------|-------|-------|
| Logic & Correctness | {meta.get('coverage', {}).get('logic', 'Standard')} | |
| Security | {meta.get('coverage', {}).get('security', 'Standard')} | |
| Performance | {meta.get('coverage', {}).get('performance', 'Standard')} | |
| Architecture | {meta.get('coverage', {}).get('architecture', 'Standard')} | |
| Maintainability | {meta.get('coverage', {}).get('maintainability', 'Standard')} | |
"""

    # Write report
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)

    result = {
        "status": "generated",
        "output_path": output_path,
        "total_findings": total,
        "counts": counts
    }
    print(json.dumps(result))
    return output_path


def extract_findings_from_report(report_path: str) -> list[str]:
    """Extract finding titles from a previous report for comparison."""
    if not os.path.exists(report_path):
        return []

    with open(report_path) as f:
        content = f.read()

    # Extract finding titles (pattern: #### [X-NNN] Title)
    pattern = r'####\s+\[[A-Z]-\d+\]\s+(.+)'
    return re.findall(pattern, content)


def compare_reports(current_path: str, previous_path: str) -> dict:
    """Compare two reports and identify resolved/new/recurring issues."""
    current_findings = set(extract_findings_from_report(current_path))
    previous_findings = set(extract_findings_from_report(previous_path))

    resolved = previous_findings - current_findings
    new = current_findings - previous_findings
    recurring = current_findings & previous_findings

    result = {
        "resolved": sorted(list(resolved)),
        "new": sorted(list(new)),
        "recurring": sorted(list(recurring)),
        "previous_count": len(previous_findings),
        "current_count": len(current_findings)
    }
    print(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description="Report Generator for Code Review")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate
    gen_parser = subparsers.add_parser("generate")
    gen_parser.add_argument("--findings", required=True, help="JSON string or file path of findings")
    gen_parser.add_argument("--meta", required=True, help="JSON string or file path of meta info")
    gen_parser.add_argument("--output", required=True, help="Output report path")
    gen_parser.add_argument("--template", help="Optional template path")

    # compare
    cmp_parser = subparsers.add_parser("compare")
    cmp_parser.add_argument("--current", required=True, help="Current report path")
    cmp_parser.add_argument("--previous", required=True, help="Previous report path")

    args = parser.parse_args()

    if args.command == "generate":
        # Handle file path or inline JSON
        findings = args.findings
        meta = args.meta
        if os.path.exists(findings):
            with open(findings) as f:
                findings = f.read()
        if os.path.exists(meta):
            with open(meta) as f:
                meta = f.read()
        generate_report(findings, meta, args.output, args.template)
    elif args.command == "compare":
        compare_reports(args.current, args.previous)


if __name__ == "__main__":
    main()
