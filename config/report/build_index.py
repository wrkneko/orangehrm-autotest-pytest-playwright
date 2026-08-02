#!/usr/bin/env python3
"""Rebuild the index page that lists every published test report.

Scans a directory laid out as ``<reports-dir>/<kind>/<label>/`` — each of which
holds the run's ``index.html`` and a ``status.txt`` — and writes a single
bento-grid page linking to all of them, newest first.

Run it locally to preview without going through CI:

    python3 config/report/build_index.py --reports-dir gh-pages/reports --output /tmp/index.html
"""

from __future__ import annotations

import argparse
import html
import os
from pathlib import Path

STATUS_CLASS = {"success": "ok", "failure": "fail"}
STATUS_LABEL = {"success": "passed", "failure": "failed"}


def collect_runs(reports_dir: Path) -> list[tuple[str, str, str]]:
    """Return (kind, label, status) for every published run, newest first."""
    runs: list[tuple[str, str, str]] = []
    if not reports_dir.is_dir():
        return runs

    for kind_dir in sorted(reports_dir.iterdir()):
        if not kind_dir.is_dir():
            continue
        for entry in kind_dir.iterdir():
            if not entry.is_dir():
                continue
            status_file = entry / "status.txt"
            status = "unknown"
            if status_file.exists():
                status = status_file.read_text(encoding="utf-8").strip() or "unknown"
            runs.append((kind_dir.name, entry.name, status))

    # Labels start with an ISO date, so a plain string sort is chronological.
    runs.sort(key=lambda run: run[1], reverse=True)
    return runs


def split_label(label: str) -> tuple[str, str, str]:
    """'2026-08-02_14-30-run57' -> ('2026-08-02', '14:30', '57')."""
    head, _, run = label.partition("-run")
    date, _, hhmm = head.partition("_")
    return date, hhmm.replace("-", ":"), run


def status_class(status: str) -> str:
    return STATUS_CLASS.get(status, "unknown")


def status_label(status: str) -> str:
    return STATUS_LABEL.get(status, status)


def render_card(kind: str, label: str, status: str, *, featured: bool) -> str:
    date, time, run = split_label(label)
    meta = " · ".join(part for part in (time, f"run {run}" if run else "") if part)
    classes = "tile card card--featured" if featured else "tile card"
    pin = '<span class="pin">latest</span>' if featured else ""
    return (
        f'<a class="{classes}" href="reports/{html.escape(kind)}/{html.escape(label)}/index.html">'
        f'<div class="card__top"><span class="tag tag--{html.escape(kind)}">{html.escape(kind)}</span>{pin}</div>'
        f'<div class="card__date">{html.escape(date)}</div>'
        f'<div class="card__meta">{html.escape(meta)}</div>'
        f'<div class="card__status s--{status_class(status)}">'
        f'<i class="dot"></i>{html.escape(status_label(status))}</div>'
        "</a>"
    )


def render_hero(title: str, runs: list[tuple[str, str, str]]) -> str:
    if runs:
        kind, label, status = runs[0]
        date, time, _ = split_label(label)
        state = (
            f'<div class="hero__state s--{status_class(status)}"><i class="dot"></i>'
            f"{html.escape(kind)} · {html.escape(status_label(status))}</div>"
            f'<div class="hero__when">{html.escape(date)}{" " + html.escape(time) if time else ""}</div>'
        )
        sub = "Every published run, newest first. Open a tile for the full HTML report."
    else:
        state = (
            '<div class="hero__state s--unknown"><i class="dot"></i>no runs yet</div>'
            '<div class="hero__when">Reports appear here after the first workflow run.</div>'
        )
        sub = "Nothing published yet."

    return (
        '<section class="tile hero">'
        f"<div><h1>{html.escape(title)}</h1>"
        f'<p class="sub">{sub}</p></div>'
        f"{state}</section>"
    )


def render_page(title: str, runs: list[tuple[str, str, str]], css: str) -> str:
    total = len(runs)
    passed = sum(1 for run in runs if run[2] == "success")
    failed = sum(1 for run in runs if run[2] == "failure")
    nightly = sum(1 for run in runs if run[0] == "regression")

    stats = "".join(
        f'<div class="{" ".join(filter(None, ("tile", "stat", modifier)))}">'
        f'<div class="stat__num">{value}</div>'
        f'<div class="stat__key">{key}</div></div>'
        for value, key, modifier in (
            (total, "runs", ""),
            (passed, "passed", "stat--pass"),
            (failed, "failed", "stat--fail"),
            (nightly, "regression", ""),
        )
    )

    if runs:
        cards = "\n".join(
            render_card(kind, label, status, featured=(index == 0))
            for index, (kind, label, status) in enumerate(runs)
        )
    else:
        cards = (
            '<div class="tile empty">Nothing published yet. Trigger the UI Tests '
            "workflow to generate the first report.</div>"
        )

    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>\n{css}\n</style>\n"
        "</head>\n<body>\n"
        f'<div class="wrap">\n<div class="bento">\n'
        f"{render_hero(title, runs)}\n{stats}\n{cards}\n"
        "</div>\n</div>\n</body>\n</html>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports-dir", type=Path, default=Path("gh-pages/reports"))
    parser.add_argument("--output", type=Path, default=Path("gh-pages/index.html"))
    # Defaults to the stylesheet sitting next to this script, so the working
    # directory does not matter.
    parser.add_argument("--css", type=Path, default=Path(__file__).with_name("index.css"))
    parser.add_argument("--title", default="OrangeHRM Autotest Reports")
    args = parser.parse_args()

    if not args.css.is_file():
        raise SystemExit(f"Stylesheet not found: {args.css}")

    runs = collect_runs(args.reports_dir)
    page = render_page(args.title, runs, args.css.read_text(encoding="utf-8"))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page, encoding="utf-8")
    print(f"Wrote {args.output} — {len(runs)} run(s) listed.")


if __name__ == "__main__":
    main()
