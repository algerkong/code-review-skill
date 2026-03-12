#!/usr/bin/env python3
"""
Diff Analyzer for Code Review

Analyzes git diffs and provides structured information for review.
Supports branch comparison, PR analysis, and commit range analysis.

Usage:
    python diff_analyzer.py branch <base> <head> [--repo PATH]
    python diff_analyzer.py commits <range> [--repo PATH]
    python diff_analyzer.py file-history <file_path> [--repo PATH] [--limit N]
    python diff_analyzer.py summary [--repo PATH]
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def run_git(args: list, repo: str = ".") -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["git"] + args,
        cwd=repo,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def get_branch_diff(base: str, head: str, repo: str = ".") -> dict:
    """Analyze diff between two branches."""
    # Get the merge base
    rc, merge_base, _ = run_git(["merge-base", base, head], repo)
    if rc != 0:
        return {"error": f"Could not find merge base between {base} and {head}"}

    merge_base = merge_base.strip()

    # Get diff stats
    rc, stat_output, _ = run_git(["diff", "--stat", f"{merge_base}..{head}"], repo)
    rc, numstat_output, _ = run_git(["diff", "--numstat", f"{merge_base}..{head}"], repo)

    # Get changed files with status
    rc, name_status, _ = run_git(["diff", "--name-status", f"{merge_base}..{head}"], repo)

    # Get commit log
    rc, log_output, _ = run_git([
        "log", "--oneline", "--no-merges",
        f"{merge_base}..{head}"
    ], repo)

    # Parse changed files
    files = []
    for line in name_status.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            status_code = parts[0][0]
            status_map = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed", "C": "copied"}
            files.append({
                "status": status_map.get(status_code, status_code),
                "path": parts[-1],
                "old_path": parts[1] if status_code in ("R", "C") and len(parts) > 2 else None
            })

    # Parse numstat for line changes
    line_changes = {}
    for line in numstat_output.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            added = int(parts[0]) if parts[0] != "-" else 0
            deleted = int(parts[1]) if parts[1] != "-" else 0
            line_changes[parts[2]] = {"added": added, "deleted": deleted}

    # Enrich file info with line changes
    for f in files:
        changes = line_changes.get(f["path"], {})
        f["lines_added"] = changes.get("added", 0)
        f["lines_deleted"] = changes.get("deleted", 0)

    # Categorize files by extension
    extensions = {}
    for f in files:
        ext = Path(f["path"]).suffix or "(no extension)"
        extensions.setdefault(ext, []).append(f["path"])

    # Parse commits
    commits = []
    for line in log_output.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split(" ", 1)
        commits.append({"hash": parts[0], "message": parts[1] if len(parts) > 1 else ""})

    total_added = sum(f.get("lines_added", 0) for f in files)
    total_deleted = sum(f.get("lines_deleted", 0) for f in files)

    result = {
        "base": base,
        "head": head,
        "merge_base": merge_base,
        "summary": {
            "files_changed": len(files),
            "lines_added": total_added,
            "lines_deleted": total_deleted,
            "net_change": total_added - total_deleted,
            "commits": len(commits)
        },
        "files": files,
        "file_types": {k: len(v) for k, v in extensions.items()},
        "commits": commits[:50],  # Limit to 50 most recent
        "stat_output": stat_output[-2000:] if len(stat_output) > 2000 else stat_output
    }

    # Risk assessment based on heuristics
    risk_factors = []
    high_risk_patterns = [
        "auth", "login", "password", "token", "secret", "key",
        "payment", "billing", "transaction",
        "migration", "schema", "database",
        "config", "env", ".yml", ".yaml",
        "security", "crypto", "encrypt"
    ]
    for f in files:
        for pattern in high_risk_patterns:
            if pattern in f["path"].lower():
                risk_factors.append(f"High-risk file changed: {f['path']} (matches '{pattern}')")
                break

    if total_added + total_deleted > 1000:
        risk_factors.append(f"Large changeset: {total_added + total_deleted} lines changed")
    if len(files) > 20:
        risk_factors.append(f"Many files changed: {len(files)} files")

    result["risk_factors"] = risk_factors
    result["risk_level"] = "high" if len(risk_factors) > 2 else "medium" if risk_factors else "low"

    print(json.dumps(result, indent=2))
    return result


def get_file_history(file_path: str, repo: str = ".", limit: int = 10) -> dict:
    """Get the change history for a specific file."""
    rc, log_output, _ = run_git([
        "log", f"-{limit}", "--format=%H|%ai|%an|%s",
        "--follow", "--", file_path
    ], repo)

    if rc != 0:
        return {"error": f"Could not get history for {file_path}"}

    commits = []
    for line in log_output.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|", 3)
        if len(parts) == 4:
            commits.append({
                "hash": parts[0],
                "date": parts[1],
                "author": parts[2],
                "message": parts[3]
            })

    result = {
        "file": file_path,
        "total_commits": len(commits),
        "commits": commits
    }
    print(json.dumps(result, indent=2))
    return result


def get_repo_summary(repo: str = ".") -> dict:
    """Get a summary of the repository state."""
    # Current branch
    rc, branch, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo)
    branch = branch.strip() if rc == 0 else "unknown"

    # Recent commits
    rc, log_output, _ = run_git(["log", "--oneline", "-10"], repo)

    # Status
    rc, status, _ = run_git(["status", "--short"], repo)

    # Remote branches
    rc, branches, _ = run_git(["branch", "-a", "--format=%(refname:short)"], repo)

    # Tags
    rc, tags, _ = run_git(["tag", "-l", "--sort=-version:refname"], repo)

    result = {
        "current_branch": branch,
        "recent_commits": [
            {"hash": l.split(" ", 1)[0], "message": l.split(" ", 1)[1] if " " in l else ""}
            for l in log_output.strip().split("\n") if l.strip()
        ][:10],
        "working_tree_status": status.strip() if status.strip() else "clean",
        "branches": [b.strip() for b in branches.strip().split("\n") if b.strip()][:30],
        "tags": [t.strip() for t in tags.strip().split("\n") if t.strip()][:10]
    }
    print(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description="Diff Analyzer for Code Review")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # branch diff
    branch_parser = subparsers.add_parser("branch")
    branch_parser.add_argument("base", help="Base branch (e.g., main)")
    branch_parser.add_argument("head", help="Head branch (e.g., feature-xyz)")
    branch_parser.add_argument("--repo", default=".", help="Repository path")

    # commit range
    commits_parser = subparsers.add_parser("commits")
    commits_parser.add_argument("range", help="Commit range (e.g., HEAD~5..HEAD)")
    commits_parser.add_argument("--repo", default=".", help="Repository path")

    # file history
    file_parser = subparsers.add_parser("file-history")
    file_parser.add_argument("file_path", help="Path to file")
    file_parser.add_argument("--repo", default=".", help="Repository path")
    file_parser.add_argument("--limit", type=int, default=10, help="Number of commits")

    # summary
    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("--repo", default=".", help="Repository path")

    args = parser.parse_args()

    if args.command == "branch":
        get_branch_diff(args.base, args.head, args.repo)
    elif args.command == "commits":
        # For commit range, use it as base..head
        get_branch_diff(args.range.split("..")[0], args.range.split("..")[-1], args.repo)
    elif args.command == "file-history":
        get_file_history(args.file_path, args.repo, args.limit)
    elif args.command == "summary":
        get_repo_summary(args.repo)


if __name__ == "__main__":
    main()
