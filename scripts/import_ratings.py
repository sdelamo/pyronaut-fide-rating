#!/usr/bin/env python3
"""Import FIDE rating lists through POST /api/v1/fide/ratings.

Download the lists from https://ratings.fide.com/download_lists.phtml (unzipped) and lay them
out as <folder>/<year>/<month>/<file>, for example:

    fide/2026/10/standard_rating_list.txt
    fide/2026/10/rapid_rating_list.txt
    fide/2026/10/blitz_rating_list.txt

The year and month of each file come from its subfolders. Only .txt files are read (the XML
downloads hold the same data). A file whose name contains "standard", "rapid" or "blitz" is read
as that rating list; the combined players_list_foa.txt is recognised from its header. The files
of one month are merged by FIDE ID and sent as one entry per player.

The server requires an API key (the FIDE_API_KEY it was started with) in the X-API-KEY header.

Example:
    FIDE_API_KEY=... python3 scripts/import_ratings.py fide
"""
import argparse
import http.client
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from urllib.parse import urlparse

# Header label -> (entry field, "int" or "text")
COLUMNS = {
    "ID Number": ("fide_id", "int"), "Name": ("name", "text"), "Fed": ("fed", "text"),
    "Sex": ("sex", "text"), "Tit": ("title", "text"), "WTit": ("w_title", "text"),
    "OTit": ("o_title", "text"), "FOA": ("foa", "text"),
    "SRtng": ("standard_rating", "int"), "SGm": ("standard_games", "int"), "SK": ("standard_k", "int"),
    "RRtng": ("rapid_rating", "int"), "RGm": ("rapid_games", "int"), "Rk": ("rapid_k", "int"),
    "BRtng": ("blitz_rating", "int"), "BGm": ("blitz_games", "int"), "BK": ("blitz_k", "int"),
    "B-day": ("birth_year", "int"), "Flag": ("flag", "text"),
}
CATEGORIES = ("standard", "rapid", "blitz")
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
NUMBER_DEFAULT_ZERO = {
    "standard_rating", "standard_games", "standard_k", "rapid_rating", "rapid_games", "rapid_k",
    "blitz_rating", "blitz_games", "blitz_k",
}


def category_of(path: str) -> str | None:
    name = os.path.basename(path).lower()
    return next((category for category in CATEGORIES if category in name), None)


def parse_header(header: str, category: str | None) -> tuple:
    """Return (columns, period) where columns is [(field, kind, start, end)].

    A split FIDE list has one rating block headed by the period (e.g. "OCT26 Gms K"); its
    category comes from the file name. The combined list names each block (SRtng, RRtng, ...).
    """
    labels = [(m.group(), m.start()) for m in re.finditer(r"\S+", header)]
    if len(labels) > 1 and labels[0][0] == "ID" and labels[1][0] == "Number":
        labels[:2] = [("ID Number", labels[0][1])]
    columns = []
    period = None
    for index, (label, start) in enumerate(labels):
        end = labels[index + 1][1] if index + 1 < len(labels) else None
        if label in COLUMNS:
            field, kind = COLUMNS[label]
        elif re.fullmatch(r"[A-Z]{3}\d{2}", label) and category:
            field, kind, period = f"{category}_rating", "int", label
        elif label == "Gms" and category:
            field, kind = f"{category}_games", "int"
        elif label == "K" and category:
            field, kind = f"{category}_k", "int"
        else:
            continue
        columns.append((field, kind, start, end))
    fields = {field for field, *_ in columns}
    if "fide_id" not in fields:
        raise ValueError(f"not a FIDE rating list, unexpected header: {header[:80]!r}")
    if not any(field.endswith("_rating") for field in fields):
        raise ValueError("no rating column found and the file name has no standard/rapid/blitz in it")
    return columns, period


def parse_line(line: str, columns: list) -> dict:
    # A long "other titles" value (e.g. FA,NI,IA,IO,FI,FT) overflows its column and pushes every
    # later column of that line to the right. The first digit after the titles is the rating, so
    # its distance from where the header puts it is the shift.
    other = next((c for c in columns if c[0] == "o_title"), None)
    first_rating = min((c[2] for c in columns if c[0].endswith("_rating")), default=None)
    shift = 0
    if other and first_rating is not None:
        digit = re.search(r"\d", line[other[2]:])
        if digit:
            shift = max(0, other[2] + digit.start() - first_rating)
    row = {}
    for field, kind, start, end in columns:
        if shift and field == "o_title":
            end = first_rating + shift  # the overflowing text takes over the FOA column too
        elif shift and field == "foa":
            continue
        elif shift and start >= first_rating:
            start, end = start + shift, None if end is None else end + shift
        value = line[start:end].strip()
        if kind == "int":
            if value:
                row[field] = int(value)
        elif value:
            row[field] = value
    return row


def find_rating_files(folder: str) -> dict:
    """Return {(year, month): [paths]} for every file under <folder>/<year>/<month>/."""
    periods: dict = {}
    for root, _, names in os.walk(folder):
        parts = os.path.relpath(root, folder).split(os.sep)
        if len(parts) != 2 or not (parts[0].isdigit() and parts[1].isdigit()):
            continue
        year, month = int(parts[0]), int(parts[1])
        if not 1 <= month <= 12:
            sys.stderr.write(f"Skipping {root}: {parts[1]!r} is not a month\n")
            continue
        paths = [os.path.join(root, name) for name in sorted(names) if name.lower().endswith(".txt")]
        periods.setdefault((year, month), []).extend(paths)
    return dict(sorted(periods.items()))


def progress(label: str, fraction: float, count: int, started: float) -> None:
    elapsed = max(time.monotonic() - started, 1e-9)
    eta = elapsed * (1 - fraction) / fraction if fraction else 0
    sys.stderr.write(
        f"\r{label}  {fraction:6.1%}  {count:>9,} entries  {count / elapsed:>8,.0f}/s  "
        f"ETA {int(eta // 60)}m{int(eta % 60):02d}s "
    )
    sys.stderr.flush()


def read_period(paths: list, label: str, year: int, month: int) -> dict:
    """Merge all files of one month into {fide_id: entry}."""
    players: dict = {}
    total_bytes = sum(os.path.getsize(path) for path in paths)
    read_bytes = 0
    started = time.monotonic()
    last_report = 0.0
    for path in paths:
        with open(path, encoding="ascii", errors="replace", newline="") as lines:
            header = next(lines)
            read_bytes += len(header)
            try:
                columns, period = parse_header(header, category_of(path))
            except ValueError as error:
                sys.exit(f"\n{path}: {error}")
            if period and period != f"{MONTHS[month - 1]}{year % 100:02d}":
                sys.exit(f"\n{path}: header says {period} but the folder is {year}/{month:02d}")
            for number, line in enumerate(lines, start=2):
                read_bytes += len(line)
                if not line.strip():
                    continue
                try:
                    row = parse_line(line, columns)
                except ValueError as error:
                    sys.exit(f"\n{path}:{number}: {error}")
                entry = players.setdefault(row["fide_id"], {})
                for field, value in row.items():
                    entry.setdefault(field, value)
                if time.monotonic() - last_report > 0.2:
                    progress(f"{label} read ", read_bytes / total_bytes, len(players), started)
                    last_report = time.monotonic()
        sys.stderr.write(f"\n{label} read {path}\n")
    return players


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", nargs="?", default="fide", help="folder laid out as <year>/<month>/<file> (default: fide)")
    parser.add_argument("--url", default="http://localhost:8080/api/v1/fide/ratings")
    parser.add_argument("--api-key", default=os.environ.get("FIDE_API_KEY"),
                        help="value for the X-API-KEY header (default: the FIDE_API_KEY environment variable)")
    parser.add_argument("--batch-size", type=int, default=1000, help="entries per request (1 = one request per entry)")
    parser.add_argument("--workers", type=int, default=min(os.cpu_count() or 1, 8),
                        help="parallel requests (default: min(CPU cores, 8); the server has 8 Python contexts "
                             "and SQLite allows one writer, so more workers only queue)")
    parser.add_argument("--from", dest="start", metavar="YYYY-MM",
                        help="skip months before this one, e.g. to resume after a failure")
    parser.add_argument("--dry-run", action="store_true", help="read and merge without sending")
    args = parser.parse_args()

    if not args.api_key and not args.dry_run:
        sys.stderr.write("An API key is required: set FIDE_API_KEY or pass --api-key\n")
        return 1

    periods = find_rating_files(args.folder)
    if args.start:
        start_year, start_month = (int(part) for part in args.start.split("-"))
        periods = {key: paths for key, paths in periods.items() if key >= (start_year, start_month)}
    if not periods:
        sys.stderr.write(f"No files found under {args.folder}/<year>/<month>/\n")
        return 1

    target = urlparse(args.url)
    local = threading.local()

    def send(batch: list) -> tuple:
        """POST one batch; return (saved, skipped) as reported by the server."""
        if args.dry_run:
            return len(batch), 0
        if not hasattr(local, "connection"):  # one keep-alive connection per worker thread
            connection_type = http.client.HTTPSConnection if target.scheme == "https" else http.client.HTTPConnection
            local.connection = connection_type(target.netloc)
        local.connection.request("POST", target.path, json.dumps(batch), {"Content-Type": "application/json", "X-API-KEY": args.api_key})
        response = local.connection.getresponse()
        body = response.read().decode()
        if response.status != 201:
            raise RuntimeError(f"HTTP {response.status} {body[:500]}")
        result = json.loads(body)
        return result["saved"], result["skipped"]

    def batches(players: dict, year: int, month: int):
        batch: list = []
        for entry in players.values():
            for field in NUMBER_DEFAULT_ZERO:
                entry.setdefault(field, 0)
            entry.setdefault("name", "")  # a few players have no name in the lists
            entry["rating_year"] = year
            entry["rating_month"] = month
            batch.append(entry)
            if len(batch) >= args.batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    overall = time.monotonic()
    total = skipped_total = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for (year, month), paths in periods.items():
            label = f"[{year}-{month:02d}]"
            players = read_period(paths, label, year, month)
            started = time.monotonic()
            sent = skipped = 0
            last_report = 0.0
            pending: set = set()

            def collect(done_futures) -> None:
                nonlocal sent, skipped, last_report
                for future in done_futures:
                    try:
                        saved_now, skipped_now = future.result()
                        sent += saved_now + skipped_now
                        skipped += skipped_now
                    except (RuntimeError, OSError, http.client.HTTPException) as error:
                        sys.stderr.write(
                            f"\nRequest failed: {error!r}\n"
                            f"{label}: {sent:,} of {len(players):,} entries confirmed. Entries already imported are "
                            f"skipped, so fix the problem and re-run (--from {year}-{month:02d} to resume here).\n"
                        )
                        os._exit(1)
                if time.monotonic() - last_report > 0.2:
                    progress(f"{label} send ", sent / len(players), sent, started)
                    last_report = time.monotonic()

            for batch in batches(players, year, month):
                pending.add(pool.submit(send, batch))
                if len(pending) >= args.workers * 2:  # keep the queue short
                    done_futures, pending = wait(pending, return_when=FIRST_COMPLETED)
                    collect(done_futures)
            while pending:
                done_futures, pending = wait(pending, return_when=FIRST_COMPLETED)
                collect(done_futures)
            progress(f"{label} send ", 1.0, sent, started)
            sys.stderr.write(
                f"\n{label} {'merged' if args.dry_run else 'imported'} {sent - skipped:,} players "
                f"({skipped:,} already imported) from {len(paths)} file(s)\n"
            )
            total += sent
            skipped_total += skipped
    sys.stderr.write(f"Done: {total:,} entries ({skipped_total:,} already imported) from {len(periods)} month(s) in {time.monotonic() - overall:.1f}s\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
