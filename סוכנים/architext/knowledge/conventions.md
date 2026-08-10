# Conventions — the expected structure

Last updated: 2026-08-10

The single source of truth for what "correct" looks like. Audit against this file, not against memory.

## 1. Every agent lives in `סוכנים/`

```
/Users/my/Downloads/הקלוד של מאיסה/סוכנים/<name>/
├── <name>.md          ← definition. filename MUST equal the frontmatter `name:`
└── knowledge/         ← optional. omit for agents with no knowledge base
    ├── index.md
    └── *.md
```

There is no other valid home for an agent definition. The older
`projects/<agent>/agents/<agent>.md` layout is **retired** — if you find it, flag it.

## 2. `~/.claude/agents/` contains symlinks and nothing else

```
~/.claude/agents/<name>.md  →  /Users/my/Downloads/הקלוד של מאיסה/סוכנים/<name>/<name>.md
```

Absolute target paths only. A relative link breaks the moment the directory moves.

**A real file in `~/.claude/agents/` is always a finding.** Someone bypassed the convention;
the definition is now invisible to git and will be lost on the next reinstall.

## 3. `claude global` is a symlink, not a copy

`/Users/my/Downloads/הקלוד של מאיסה/claude global → /Users/my/.claude`

It is gitignored. If it is ever a real directory, two divergent copies of the config exist.

## Checks to run

| # | Check | Finding |
|---|---|---|
| A | Every `סוכנים/<name>/<name>.md` has a `~/.claude/agents/<name>.md` symlink | agent without symlink, harness cannot load it |
| B | Every `~/.claude/agents/*.md` resolves (`[ -e ]`) | dangling link |
| C | Every entry in `~/.claude/agents/` is a symlink (`[ -L ]`) | real file, convention bypassed |
| D | Directory name == filename == frontmatter `name:` | naming drift |
| E | Every symlink target is an absolute path | fragile link |
| F | No leftover `projects/` directory at the workspace root | retired layout |
| G | Path strings inside agent/skill `.md` files resolve on disk | stale reference after a move |

Check G matters most after any restructure: paths live in prose, so a `mv` silently
breaks them and nothing errors until an agent tries to read.

## Known-good baseline (2026-08-10)

12 agents, all symlinked, zero real files in `~/.claude/agents/`:

| Group | Agents | Knowledge |
|---|---|---|
| Studio maisa | adi, dana, netta, rami | yes |
| General | architext, chief-of-staff, crazy-eva | yes |
| `/market` subagents | market-competitive, market-content, market-conversion, market-strategy, market-technical | no, by design |

Do not flag the five `market-*` agents for having no `knowledge/`. They are spawned by the
`/market` skill and read nothing.

## Standing exceptions

- `/Users/my/Desktop/premium-kit/` is a separate distributable product with its own git repo
  and its own `.claude/agents/`. It is NOT part of the fleet. Never flag it, and never expect
  its agents to have symlinks. Note that running its `install.sh` re-adds agents to `~/.claude`.
- `~/.claude/skills/skill-creator/agents/` belongs to that skill. Not fleet agents.
