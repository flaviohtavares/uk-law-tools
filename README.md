# UK Law tools

Let your AI assistant look up UK legislation and answer from the actual text.

[**uk-law**](https://github.com/flaviohtavares/uk-law) is the legislation of the United Kingdom
as plain text: about 130,000 Acts and regulations of the UK Parliament, Scotland, Wales and
Northern Ireland, the historic parliaments and EU-origin law, converted from legislation.gov.uk and
updated every day. This repository has a **skill** that teaches Claude Code, Codex and other agents
how to search it and read it, so that you can ask:

> What does the Employment Rights Act say about notice periods?
>
> Is there a law in Scotland on short-term lets?
>
> Show me section 5 of the Data Protection Act 2018.

The assistant finds the law, opens the right section, quotes it, tells you how current the text is
and links the official page.

> **Not legal advice.** The texts are an unofficial copy and can be out of date or contain
> conversion errors. Always check the official text at
> [legislation.gov.uk](https://www.legislation.gov.uk), or ask a lawyer, before relying on it.

You need Python 3 (already on macOS and most Linux systems) and an internet connection. Nothing
else is installed, and you do not need to download the 4 GB repository.

## Claude Code

In Claude Code, run:

```
/plugin marketplace add flaviohtavares/uk-law-tools
/plugin install uk-law@uk-law-tools
```

Restart Claude Code if it asks. Then just ask about UK law in any session; Claude uses the skill
by itself. To call it on purpose, type `/uk-law` and pick the skill from the menu, followed by
your question.

To update: `/plugin marketplace update uk-law-tools`. To remove: `/plugin uninstall uk-law`.

## Codex and other agents

Install the skill with one command:

```sh
curl -fsSL https://raw.githubusercontent.com/flaviohtavares/uk-law-tools/main/install.sh | sh
```

It copies the skill to `~/.agents/skills/uk-law` and `~/.codex/skills/uk-law`, where Codex looks
for skills. Restart Codex, then ask about UK law. Run the same command again to update.

If you prefer to see what you install, do it by hand:

```sh
git clone --depth 1 https://github.com/flaviohtavares/uk-law-tools
mkdir -p ~/.agents/skills
cp -R uk-law-tools/plugins/uk-law/skills/uk-law ~/.agents/skills/
```

Any agent that reads `SKILL.md` folders (the Agent Skills format) can use the same folder: copy
`plugins/uk-law/skills/uk-law` to wherever that agent keeps its skills.

## ChatGPT, Claude.ai and other chat assistants

Chat assistants cannot run the skill, but they can read the repository from the web. Paste this
link into the chat and ask your question:

```
https://raw.githubusercontent.com/flaviohtavares/uk-law/main/llms.txt
```

It tells the assistant how to find a law and which file to open. Giving the link of one law's
file works too; every law is listed with its file in
[`index/laws.csv`](https://github.com/flaviohtavares/uk-law/blob/main/index/laws.csv).

## Using the script yourself

The skill is a small Python script that you can also run in a terminal:

```sh
S=~/.agents/skills/uk-law/scripts/uk_law.py          # or wherever the skill is installed

python3 $S find data protection act                  # laws whose title has all the words
python3 $S find minimum wage --in-force --type uksi  # only regulations still in force
python3 $S find rent --extent S                      # laws that apply in Scotland
python3 $S show ukpga/2018/12                        # a law, or the contents of a long one
python3 $S show ukpga/2018/12 "section 5"            # one section ("schedule 1", "part 2" ...)
python3 $S topics housing                            # subjects whose name has a word
python3 $S topic landlord and tenant                 # the laws in force on one subject
python3 $S url ukpga/2018/12                         # GitHub, raw and official links
```

Each law has an id, the same as on legislation.gov.uk: `ukpga/2018/12` is the Data Protection
Act 2018 (`ukpga` = UK Public General Act, 2018 = year, 12 = chapter number). The main prefixes:

| prefix | what |
|---|---|
| `ukpga` | Acts of the UK Parliament |
| `uksi` | UK statutory instruments: regulations, orders and rules |
| `asp` / `ssi` | Acts of the Scottish Parliament / Scottish statutory instruments |
| `asc`, `anaw` / `wsi` | Acts of the Senedd / Wales statutory instruments |
| `nia` / `nisr` | Acts of the Northern Ireland Assembly / Northern Ireland statutory rules |
| `eur` | EU-origin regulations kept in UK law |

The first search downloads the index of all laws (about 40 MB) and keeps it for a day in
`~/.cache/uk-law`. Laws are read one file at a time from GitHub.

## Working offline

Clone only the folders you need (the whole repository is about 4 GB):

```sh
python3 $S clone ~/uk-law index topics uk-parliament/acts
export UK_LAW_DIR=~/uk-law      # the script and the skill now read this clone
git -C ~/uk-law pull            # update it
```

Add folders later with `git -C ~/uk-law sparse-checkout add scotland`. Inside the clone,
`AGENTS.md` and `CLAUDE.md` explain the layout to any agent working there.

## How the texts are made

See the [uk-law README](https://github.com/flaviohtavares/uk-law) and its
[COVERAGE.md](https://github.com/flaviohtavares/uk-law/blob/main/COVERAGE.md): what is included,
what is missing, and the words the conversion is known to lose.

## Licence

The code here is MIT licensed. The legislation texts are © Crown and database right, under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
