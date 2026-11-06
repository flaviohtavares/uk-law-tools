#!/usr/bin/env python3
"""Search and read UK legislation from the uk-law repository (github.com/flaviohtavares/uk-law).

Works without cloning: files are read from GitHub and the index is cached for a day in
~/.cache/uk-law. With a local clone, pass --repo DIR or set UK_LAW_DIR and nothing is downloaded.
Standard library only.

  uk_law.py find data protection act             laws whose title has all the words
  uk_law.py find "minimum wage" --in-force --type uksi
  uk_law.py show ukpga/2018/12                    a law, or the contents of a long law
  uk_law.py show ukpga/2018/12 "section 5"        one section, part or schedule of a long law
  uk_law.py topics housing                        topics whose name has the word
  uk_law.py topic "landlord and tenant"           laws in force on one topic
  uk_law.py url ukpga/2018/12                     links to the file and the official page
  uk_law.py clone ~/uk-law index uk-parliament/acts   a partial clone, for working offline
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = "flaviohtavares/uk-law"
RAW = f"https://raw.githubusercontent.com/{REPO}/main"
WEB = f"https://github.com/{REPO}/blob/main"
OFFICIAL = "https://www.legislation.gov.uk"
INDEX = "index/laws.csv"
CACHE = Path(os.environ.get("UK_LAW_CACHE", Path.home() / ".cache" / "uk-law"))
MAX_AGE = 24 * 3600
ACT_TYPES = {"ukpga", "ukla", "apgb", "aep", "aosp", "aip", "apni", "mnia", "nisi", "nia", "asp", "mwa",
             "anaw", "asc", "ukcm"}
IN_FORCE = {"revised", "revised-with-pending-changes", "as-enacted"}
DISCLAIMER = ("Not an official source and not legal advice: check the official text at "
              "legislation.gov.uk before relying on it.")


class Source:
    """Files of the repository, from a local clone or from GitHub."""

    def __init__(self, repo: str | None):
        self.local = Path(repo).expanduser() if repo else None
        if self.local and not (self.local / INDEX).is_file():
            sys.exit(f"{self.local} has no {INDEX}: is it a clone of {REPO} with `index` checked out?")

    def read(self, rel: str) -> str:
        if self.local:
            path = self.local / rel
            if not path.is_file():
                raise FileNotFoundError(rel)
            return path.read_text(encoding="utf-8")
        return _get(f"{RAW}/{urllib.request.quote(rel)}")

    def index(self) -> list[dict]:
        if self.local:
            text = (self.local / INDEX).read_text(encoding="utf-8")
        else:
            cached = CACHE / "laws.csv"
            if not cached.is_file() or time.time() - cached.stat().st_mtime > MAX_AGE:
                print("Downloading the index of all laws (about 40 MB, once a day)...", file=sys.stderr)
                text = _get(f"{RAW}/{INDEX}")
                CACHE.mkdir(parents=True, exist_ok=True)
                tmp = cached.with_suffix(".tmp")
                tmp.write_text(text, encoding="utf-8")
                tmp.replace(cached)
            text = cached.read_text(encoding="utf-8")
        return list(csv.DictReader(io.StringIO(text)))


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "uk-law-tools"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise FileNotFoundError(url) from None
        raise


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower().replace("’", "'").replace("'", ""))


# ----------------------------------------------------------------------- find


def search(rows: list[dict], query: str, types: list[str] | None = None, in_force: bool = False,
           topic: str | None = None, extent: str | None = None) -> list[dict]:
    q = query.strip()
    exact = [r for r in rows if r["id"].lower() == q.lower()]
    if exact:
        return exact
    words = _words(q)
    topic_words = _words(topic or "")
    found = []
    for r in rows:
        if types and r["type"] not in types:
            continue
        if in_force and r["status"] not in IN_FORCE:
            continue
        if extent and extent.upper() not in r["extent"].upper().split("+"):
            continue
        if topic_words and not all(w in _words(r["topics"]) for w in topic_words):
            continue
        title = _words(r["title"])
        if all(w in title for w in words):
            found.append(r)
    joined = " ".join(words)

    def rank(r: dict) -> tuple:
        title = " ".join(_words(r["title"]))
        return (title != joined and title != "the " + joined,       # exact title first
                f" {joined} " not in f" {title} ",                  # then titles with the words in order
                r["type"] not in ACT_TYPES,                         # then Acts before regulations
                r["status"] not in IN_FORCE,                        # in force before repealed
                -int(r["year"]) if r["year"].isdigit() else 0,      # newest first
                len(title))
    return sorted(found, key=rank)


def cmd_find(src: Source, a) -> int:
    rows = search(src.index(), " ".join(a.words), a.type, a.in_force, a.topic, a.extent)
    if not rows:
        print("No law found. Try fewer or different words, or `topics` to browse by subject.")
        return 1
    for r in rows[: a.limit]:
        tags = [r["status"]] + ([f"extent {r['extent']}"] if r["extent"] else [])
        print(f"{r['id']}  {r['title']}  [{', '.join(tags)}]")
        if a.paths:
            print(f"    {r['path']}")
    if len(rows) > a.limit:
        print(f"... and {len(rows) - a.limit} more (use --limit, or add words / --type / --in-force).")
    return 0


# ----------------------------------------------------------------------- show


def _law(rows: list[dict], law_id: str) -> dict:
    for r in rows:
        if r["id"].lower() == law_id.strip("/").lower():
            return r
    sys.exit(f"No law with id {law_id!r} in the index. Use `find` to look it up.")


def _part_file(contents: str, part: str) -> str | None:
    """The file of `part` ("section 5", "s.5", "schedule 1", "part 2", "regulation 3") in a README."""
    p = part.lower().strip()
    p = re.sub(r"^(s|ss|sec)\.?\s*(?=\d)", "section ", p)
    p = re.sub(r"^(reg|r)\.?\s*(?=\d)", "regulation ", p)
    p = re.sub(r"^(sch|sched)\.?\s*(?=\d)", "schedule ", p)
    slug = re.sub(r"[^a-z0-9]+", "-", p).strip("-")
    links = re.findall(r"\]\(([^)]+\.md)\)", contents)
    for link in links:
        if Path(link).stem == slug:
            return link
    for link in links:  # "part 2" is a folder of sections: give its first file's folder listing
        if link.split("/")[0] == slug:
            return link.split("/")[0]
    return None


def cmd_show(src: Source, a) -> int:
    law = _law(src.index(), a.id)
    path = law["path"]
    text = src.read(path)
    if a.part:
        if not path.endswith("/README.md"):
            print(f"{law['title']} is a single file; showing all of it.\n", file=sys.stderr)
        else:
            target = _part_file(text, a.part)
            if target is None:
                sys.exit(f"No {a.part!r} in the contents of {law['title']}. Run `show {law['id']}` to see them.")
            base = path.rsplit("/", 1)[0]
            if not target.endswith(".md"):  # a whole part: list its files
                files = [l for l in re.findall(r"\]\(([^)]+\.md)\)", text) if l.startswith(target + "/")]
                print(f"{law['title']}, {a.part}: {len(files)} files. Show one with `show {law['id']} \"<name>\"`:")
                for f in files:
                    print(f"  {Path(f).stem}")
                return 0
            path = f"{base}/{target}"
            text = src.read(path)
    if len(text) > a.max_chars:
        text = text[: a.max_chars] + f"\n\n[... cut at {a.max_chars} characters; raise --max-chars to see more]"
    print(text)
    print(f"\nFile: {WEB}/{path}\nOfficial: {OFFICIAL}/{law['id']}\n{DISCLAIMER}")
    return 0


# --------------------------------------------------------------------- topics


def _topic_table(src: Source) -> list[tuple[str, str, str, str]]:
    text = src.read("topics/README.md")
    return re.findall(r"^\| \[([^\]]+)\]\(([^)]+)\) \| (\d+) \| (\d+) \|$", text, re.M)


def cmd_topics(src: Source, a) -> int:
    words = _words(" ".join(a.words))
    rows = [t for t in _topic_table(src) if all(w in _words(t[0]) for w in words)]
    if not rows:
        print("No topic with those words. Run `topics` with no words to list them all.")
        return 1
    for name, _, acts, regs in rows:
        print(f"{name}  ({acts} Acts, {regs} regulations in force)")
    return 0


def cmd_topic(src: Source, a) -> int:
    words = _words(" ".join(a.words))
    rows = _topic_table(src)
    match = [t for t in rows if _words(t[0]) == words] or [t for t in rows if all(w in _words(t[0]) for w in words)]
    if not match:
        sys.exit("No such topic. Use `topics <word>` to find its name.")
    if len(match) > 1:
        print("Several topics match: " + "; ".join(t[0] for t in match))
        return 1
    rel = "topics/" + match[0][1]
    text = src.read(rel)
    if len(text) > a.max_chars:
        text = text[: a.max_chars] + f"\n\n[... cut at {a.max_chars} characters; raise --max-chars to see more]"
    print(text)
    print(f"\nPage: {WEB}/{rel}")
    return 0


# ----------------------------------------------------------------- url, clone


def cmd_url(src: Source, a) -> int:
    law = _law(src.index(), a.id)
    print(f"{law['title']}\nGitHub:   {WEB}/{law['path']}\nRaw file: {RAW}/{law['path']}\n"
          f"Official: {OFFICIAL}/{law['id']}")
    return 0


def cmd_clone(src: Source, a) -> int:
    target = Path(a.dir).expanduser()
    if target.exists():
        sys.exit(f"{target} already exists.")
    folders = a.folders or ["index", "topics", "nations"]
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                    f"https://github.com/{REPO}", str(target)], check=True)
    subprocess.run(["git", "-C", str(target), "sparse-checkout", "set", *folders], check=True)
    print(f"Cloned into {target} with: {', '.join(folders)}.\n"
          f"Add folders later with: git -C {target} sparse-checkout add <folder>\n"
          f"Update with: git -C {target} pull\n"
          f"Use it offline with: --repo {target}  (or export UK_LAW_DIR={target})")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="uk_law.py", description="Search and read UK legislation (github.com/flaviohtavares/uk-law).")
    p.add_argument("--repo", default=os.environ.get("UK_LAW_DIR"), help="a local clone to read from instead of GitHub")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find", help="find laws by words of their title, or by id")
    f.add_argument("words", nargs="+")
    f.add_argument("--type", action="append", help="id prefix such as ukpga, uksi, asp, ssi, wsi, nisr; repeatable")
    f.add_argument("--in-force", action="store_true", help="leave out repealed laws")
    f.add_argument("--topic", help="only laws under a topic whose name has these words")
    f.add_argument("--extent", help="only laws that extend to E, W, S or N.I.")
    f.add_argument("--limit", type=int, default=20)
    f.add_argument("--paths", action="store_true", help="also print each law's file path")
    s = sub.add_parser("show", help="print a law, or one section, part or schedule of a long law")
    s.add_argument("id")
    s.add_argument("part", nargs="?", help='e.g. "section 5", "schedule 1", "part 2", "regulation 3"')
    s.add_argument("--max-chars", type=int, default=80000)
    t = sub.add_parser("topics", help="list topics, optionally only those whose name has these words")
    t.add_argument("words", nargs="*")
    tp = sub.add_parser("topic", help="print the page of one topic")
    tp.add_argument("words", nargs="+")
    tp.add_argument("--max-chars", type=int, default=80000)
    u = sub.add_parser("url", help="links to a law's file and its official page")
    u.add_argument("id")
    c = sub.add_parser("clone", help="clone only some folders of the repository")
    c.add_argument("dir")
    c.add_argument("folders", nargs="*", help="default: index topics nations")
    a = p.parse_args(argv)
    src = Source(a.repo if a.cmd != "clone" else None)
    try:
        return {"find": cmd_find, "show": cmd_show, "topics": cmd_topics, "topic": cmd_topic,
                "url": cmd_url, "clone": cmd_clone}[a.cmd](src, a)
    except FileNotFoundError as exc:
        sys.exit(f"Not found: {exc}. If you use a partial clone, check out its folder with "
                 f"`git sparse-checkout add <folder>`, or run without --repo.")
    except urllib.error.URLError as exc:
        sys.exit(f"Could not reach GitHub ({exc}). Check the connection, or use a local clone with --repo.")


if __name__ == "__main__":
    sys.exit(main())
