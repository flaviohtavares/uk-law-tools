# UK Law tools

Let your AI assistant look up UK legislation and answer from the actual text.

[**uk-law**](https://github.com/flaviohtavares/uk-law) is the legislation of the United Kingdom
as plain text: about 130,000 Acts and regulations of the UK Parliament, Scotland, Wales and
Northern Ireland, the historic parliaments and EU-origin law, converted from legislation.gov.uk and
updated every day. This repository explains how to connect it to Claude, Claude Code, Codex and
ChatGPT, and has a **skill** that teaches agents how to search it and read it, so that you can ask:

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

The skill needs Python 3 (already on macOS and most Linux systems) and an internet connection; the
MCP server needs nothing at all. Neither downloads the 4 GB repository.

## Install: step by step

There are two ways to connect an assistant, and both are free:

- the **MCP server** (`https://uk-law-mcp.uk-law-mcp.workers.dev/mcp`), for Claude, ChatGPT, Claude Code and Codex. Nothing to install on your computer and no sign-in;
- the **skill** (a small Python script), for Claude Code and Codex. It reads GitHub directly and works without the server.

After installing, test it with a question such as:
*"What does section 86 of the Employment Rights Act 1996 say about notice periods?"*
The answer should quote the section and link legislation.gov.uk.

### Claude (claude.ai, Claude Desktop and the mobile apps)

Works on every plan; the Free plan allows one custom connector.

1. Open [Customize → Connectors](https://claude.ai/customize/connectors). The same connector then works in Claude Desktop and the mobile apps.
2. Click **+ Add**, then **Add custom connector**.
3. Name: `UK Law`. Remote MCP server URL: `https://uk-law-mcp.uk-law-mcp.workers.dev/mcp`. Click **Continue**.
4. Under **Authentication**, choose **No sign in**, then click **Add**.
5. In a chat, click **+** (bottom left) → **Connectors** and make sure **UK Law** is switched on. Then ask your question.

On Team and Enterprise plans an Owner adds the connector once in **Organization settings → Connectors**
(Add → Custom → Web, same URL, "No sign in"); members then switch it on in Customize → Connectors.

### Claude Code

**Option A, the plugin (recommended).** Type in Claude Code:

```
/plugin marketplace add flaviohtavares/uk-law-tools
/plugin install uk-law@uk-law-tools
```

Restart Claude Code if asked. Update later with `/plugin marketplace update uk-law-tools`.

**Option B, the MCP server.** In a terminal:

```sh
claude mcp add --transport http --scope user uk-law https://uk-law-mcp.uk-law-mcp.workers.dev/mcp
```

`--scope user` makes it available in every project. Check it with `/mcp` inside Claude Code.

### Codex (CLI, IDE extension and app)

**Option A, the MCP server.** In a terminal:

```sh
codex mcp add uk-law --url https://uk-law-mcp.uk-law-mcp.workers.dev/mcp
```

or add this to `~/.codex/config.toml`:

```toml
[mcp_servers.uk-law]
url = "https://uk-law-mcp.uk-law-mcp.workers.dev/mcp"
```

Check it with `codex mcp list`, then start a new Codex session.

**Option B, the skill.** In a terminal:

```sh
curl -fsSL https://raw.githubusercontent.com/flaviohtavares/uk-law-tools/main/install.sh | sh
```

It copies the skill to `~/.agents/skills/uk-law` (and `~/.codex/skills/uk-law`). Restart Codex.
Run the same command to update.

### ChatGPT

Custom MCP servers work on **chatgpt.com (web)** with a **Pro**, **Business** or **Enterprise/Edu**
plan. On Business, only workspace admins and owners can add them.

1. Open [Plugins](https://chatgpt.com/plugins).
2. Click **+**, then **Add custom MCP server**.
3. Name: `UK Law`. Under **Connection**, enter `https://uk-law-mcp.uk-law-mcp.workers.dev/mcp`.
4. Authentication: **None**.
5. Tick **I understand and want to continue**, then click **Create as a plugin** and install it.
6. In a new chat, type **@**, pick **UK Law**, and ask your question.

**Free and Plus plans:** paste this link into the chat and ask your question; ChatGPT reads the
instructions and opens the right file:

```
https://raw.githubusercontent.com/flaviohtavares/uk-law/main/llms.txt
```

### Other MCP clients

Add `https://uk-law-mcp.uk-law-mcp.workers.dev/mcp` as a remote server (Streamable HTTP transport,
no authentication).

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

## Who maintains this

Built and maintained by **[Tavlabs Ltd](https://www.tavlabs.uk/?utm_source=github&utm_medium=uk-law-tools)**,
a London software house for small and medium businesses. We build data pipelines like this one, and
custom software for operations, from food safety to logistics. Need something similar?
[contact@tavlabs.uk](mailto:contact@tavlabs.uk)

This is an independent project. It is not affiliated with or endorsed by The National Archives,
legislation.gov.uk or the UK Government.

## Licence

The code here is MIT licensed. The legislation texts are © Crown and database right, under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
