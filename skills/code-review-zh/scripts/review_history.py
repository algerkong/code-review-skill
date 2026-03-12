#!/usr/bin/env python3
"""
Review History Manager

Manages the .review/ directory structure and history.json tracking.
Used by the code-review skill to initialize, query, and update review history.

Usage:
    python review_history.py init <project_root>
    python review_history.py latest <project_root> [--mode MODE] [--scope SCOPE]
    python review_history.py add <project_root> --report-path PATH --mode MODE --scope SCOPE --summary JSON
    python review_history.py stats <project_root>
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_review_dir(project_root: str) -> Path:
    return Path(project_root) / ".review"


def get_history_path(project_root: str) -> Path:
    return get_review_dir(project_root) / "history.json"


def init_review_dir(project_root: str) -> dict:
    """Initialize .review/ directory structure."""
    review_dir = get_review_dir(project_root)
    reports_dir = review_dir / "reports"
    snapshots_dir = review_dir / "snapshots"

    reports_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    history_path = get_history_path(project_root)
    if not history_path.exists():
        history = {
            "project": os.path.basename(os.path.abspath(project_root)),
            "created": datetime.now(timezone.utc).isoformat(),
            "reviews": []
        }
        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)
        print(json.dumps({"status": "created", "path": str(review_dir)}))
    else:
        with open(history_path) as f:
            history = json.load(f)
        print(json.dumps({"status": "exists", "path": str(review_dir), "review_count": len(history.get("reviews", []))}))

    return history


def get_latest_review(project_root: str, mode: str = None, scope: str = None) -> dict | None:
    """Get the most recent review, optionally filtered by mode and scope."""
    history_path = get_history_path(project_root)
    if not history_path.exists():
        print(json.dumps({"status": "no_history", "message": "No review history found. This is the first review."}))
        return None

    with open(history_path) as f:
        history = json.load(f)

    reviews = history.get("reviews", [])
    if not reviews:
        print(json.dumps({"status": "no_reviews", "message": "History exists but no reviews recorded yet."}))
        return None

    # Filter by mode and scope if specified
    filtered = reviews
    if mode:
        filtered = [r for r in filtered if r.get("mode") == mode]
    if scope:
        filtered = [r for r in filtered if r.get("scope") == scope]

    if not filtered:
        print(json.dumps({
            "status": "no_matching_reviews",
            "message": f"No previous reviews found for mode='{mode}', scope='{scope}'.",
            "total_reviews": len(reviews)
        }))
        return None

    # Sort by date descending and return the most recent
    filtered.sort(key=lambda r: r.get("date", ""), reverse=True)
    latest = filtered[0]

    # Try to read the report content
    report_path = get_review_dir(project_root) / latest.get("report_path", "")
    report_content = None
    if report_path.exists():
        report_content = report_path.read_text()

    result = {
        "status": "found",
        "review": latest,
        "report_content": report_content[:5000] if report_content else None,
        "report_path": str(report_path)
    }
    print(json.dumps(result, default=str))
    return latest


def add_review(project_root: str, report_path: str, mode: str, scope: str, summary: dict) -> None:
    """Add a new review entry to history."""
    history_path = get_history_path(project_root)

    # Ensure directory exists
    init_review_dir(project_root)

    with open(history_path) as f:
        history = json.load(f)

    # Generate review ID
    review_count = len(history.get("reviews", [])) + 1
    now = datetime.now(timezone.utc)
    review_id = f"review-{now.strftime('%Y-%m-%d')}-{review_count:03d}"

    # Make report_path relative to .review/
    rel_path = os.path.relpath(report_path, get_review_dir(project_root))

    entry = {
        "id": review_id,
        "date": now.isoformat(),
        "mode": mode,
        "scope": scope,
        "report_path": rel_path,
        "summary": summary
    }

    history.setdefault("reviews", []).append(entry)

    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    print(json.dumps({"status": "added", "review_id": review_id, "report_path": rel_path}))


def show_stats(project_root: str) -> None:
    """Show review statistics."""
    history_path = get_history_path(project_root)
    if not history_path.exists():
        print(json.dumps({"status": "no_history"}))
        return

    with open(history_path) as f:
        history = json.load(f)

    reviews = history.get("reviews", [])
    if not reviews:
        print(json.dumps({"status": "no_reviews"}))
        return

    # Aggregate stats
    total_findings = 0
    severity_totals = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    modes_count = {}

    for r in reviews:
        summary = r.get("summary", {})
        total_findings += summary.get("total_findings", 0)
        for sev in severity_totals:
            severity_totals[sev] += summary.get(sev, 0)
        mode = r.get("mode", "unknown")
        modes_count[mode] = modes_count.get(mode, 0) + 1

    dates = [r.get("date", "") for r in reviews if r.get("date")]
    dates.sort()

    stats = {
        "status": "ok",
        "total_reviews": len(reviews),
        "first_review": dates[0] if dates else None,
        "latest_review": dates[-1] if dates else None,
        "total_findings_all_time": total_findings,
        "severity_totals": severity_totals,
        "reviews_by_mode": modes_count
    }
    print(json.dumps(stats, default=str))


def main():
    parser = argparse.ArgumentParser(description="Review History Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("project_root")

    # latest
    latest_parser = subparsers.add_parser("latest")
    latest_parser.add_argument("project_root")
    latest_parser.add_argument("--mode", default=None)
    latest_parser.add_argument("--scope", default=None)

    # add
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("project_root")
    add_parser.add_argument("--report-path", required=True)
    add_parser.add_argument("--mode", required=True)
    add_parser.add_argument("--scope", required=True)
    add_parser.add_argument("--summary", required=True, help="JSON string with finding counts")

    # stats
    stats_parser = subparsers.add_parser("stats")
    stats_parser.add_argument("project_root")

    args = parser.parse_args()

    if args.command == "init":
        init_review_dir(args.project_root)
    elif args.command == "latest":
        get_latest_review(args.project_root, args.mode, args.scope)
    elif args.command == "add":
        summary = json.loads(args.summary)
        add_review(args.project_root, args.report_path, args.mode, args.scope, summary)
    elif args.command == "stats":
        show_stats(args.project_root)


if __name__ == "__main__":
    main()
