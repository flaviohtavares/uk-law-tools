---
name: uk-law
description: Find and read UK legislation (Acts of Parliament, statutory instruments and regulations, Scottish, Welsh and Northern Ireland law, retained EU law) from the uk-law repository, and answer questions about what the law says with the exact section and a link to the official text. Use when the user asks about a UK Act, regulation, section or schedule, or about UK law on a subject such as employment, housing, tax, benefits, immigration, data protection, driving or family law.
---

# UK law

The text of UK legislation, converted from legislation.gov.uk and updated daily, is in the
GitHub repository `flaviohtavares/uk-law`. This skill reads it with `scripts/uk_law.py`, in this
skill's folder. The script needs only Python 3 and works without cloning anything.

Run it as `python3 <this skill's folder>/scripts/uk_law.py <command>`.

## How to answer a question

1. **Find the law.** Search titles: `find <words>`. Add `--in-force` to leave out repealed laws,
   `--type ukpga` for UK Acts only (`uksi` regulations, `asp` / `ssi` Scotland, `asc` / `anaw` /
   `wsi` Wales, `nia` / `nisr` Northern Ireland), `--extent S` for laws that reach Scotland. An id
   such as `ukpga/1996/18` finds that law directly. If you do not know the title, browse by subject:
   `topics <word>` then `topic <name>`.
2. **Read it.** `show <id>` prints a short law in full. A long law prints its front matter and a
   **Contents** list: then open only what you need with `show <id> "section 94"`,
   `show <id> "schedule 1"` or `show <id> "part 2"` (lists the sections of that part).
3. **Answer** from the text you read, never from memory alone:
   - name the law and the section, regulation or schedule, and quote the key words;
   - give the official link (`Official:` at the end of the output);
   - say how current the text is: the front matter has `status` and `text_date`.
     - `revised`: up to date as of `text_date`.
     - `revised-with-pending-changes`: some changes are not yet in the text; say so.
     - `as-enacted`: the original text; later amendments are **not** applied; say so.
     - `repealed`: no longer in force.
   - say where it applies (`extent`: E England, W Wales, S Scotland, N.I. Northern Ireland);
   - end with a short note that this is not legal advice and the official text or a lawyer should
     be checked before relying on it.

Footnotes at the end of each file (`[^c-…]`, `[^M_…]`) record amendments and commencement; read
them when the user asks when or how a provision changed.

## Commands

| command | does |
|---|---|
| `find <words> [--in-force] [--type T] [--topic words] [--extent E] [--limit N] [--paths]` | laws whose title has all the words, Acts and in-force laws first |
| `show <id> [part]` | the law, or one section / regulation / schedule / part of a long law |
| `topics [words]` | topics (official subject headings) with counts |
| `topic <name>` | the Acts and regulations in force on one topic |
| `url <id>` | links to the file on GitHub, the raw file and the official page |
| `clone <dir> [folders...]` | partial clone for offline use; then pass `--repo <dir>` |

The first `find` downloads the index of all laws (about 40 MB) and caches it for a day in
`~/.cache/uk-law`. If `UK_LAW_DIR` is set, or `--repo DIR` is given before the command, the script
reads a local clone instead and downloads nothing.

## Tips

- Statutory instrument titles usually start with "The" and end with the year; search without them.
- Many regulations amend others. For the law as it stands, prefer the principal Act or regulations
  with status `revised`; amending instruments are often `as-enacted`.
- Do not list the repository's folders: there are over 400,000 files. Always go through `find`.
- If a result is cut ("cut at N characters"), show a smaller part instead of raising the limit.
