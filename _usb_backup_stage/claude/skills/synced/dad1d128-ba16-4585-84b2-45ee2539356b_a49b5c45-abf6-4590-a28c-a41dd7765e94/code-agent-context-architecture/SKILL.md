---
name: "code-agent-context-architecture"
description: "Use when setting up or reviewing Claude Code project memory (CLAUDE.md), custom skills, MCP connectors, or multi-agent handoff workflows."
---

# Claude Code context architecture

Source: a Reddit-sourced guide pasted by the user (8 Oct 2026). Corrections to the guide are marked (fix).

## 1. Memory hierarchy (progressive disclosure)
- Keep project `./CLAUDE.md` short (under about 80 lines): tech stack, build/dev/test/lint commands, and a pointer to deeper memory. Rules beyond roughly 100-150 lines get ignored.
- Put long-term detail in `./.claude/memory/`: `user_preferences.md` (style and workflow), `decisions.md` (architecture trade-offs, API choices), `feedback.md` (lessons from failed tests).
- (fix) Claude Code only auto-loads CLAUDE.md files; memory subfolders are read when CLAUDE.md tells Claude to read them, so keep the pointer explicit.

## 2. Custom skills
- Global skill path: `~/.claude/skills/<skill-name>/SKILL.md` (project-level: `./.claude/skills/`).
- A skill's full text loads only when its `description` matches the task, which saves tokens versus a bloated CLAUDE.md.
- (fix) The real frontmatter fields are `name` and `description`; a `triggers:` list is not a standard field, so put trigger phrases inside the description.
- Example pattern, a close-session skill: (1) retrospective scan, update `decisions.md` and append rules to `user_preferences.md`; (2) run lint and fix failures; (3) `git status --short`, draft a Conventional Commit message, ask for confirmation before committing.

## 3. MCP connectors
- A local MCP server (Node `@modelcontextprotocol/sdk`) exposes tools: `ListToolsRequestSchema` returns tool names, descriptions and JSON input schemas; `CallToolRequestSchema` executes them; connect over `StdioServerTransport`.
- (fix) In the pasted sample, the fetch URL `https://internal-service.local{endpoint}` is missing a slash; use `https://internal-service.local${endpoint}` with a template literal and validate the endpoint.
- (fix) Register servers with `claude mcp add <name> -- node /abs/path/index.js` or in `.mcp.json` (project) / `~/.claude.json`; do not invent `~/.claude/config.json`.
- Keep secrets in environment variables, never in committed files.

## 4. Multi-agent handoff
- Role agents communicate through files in `./handoff/`: Architect writes `brief.md`; Builder implements within strict scope, updates memory logs, runs tests; Reviewer checks output against the brief and approves or returns it.
- Benefits: less context pollution, lower token use, no scope creep.

## Usage
When asked to set up or audit this kind of context, propose the file layout above, keep CLAUDE.md compact, and ask about runtime/framework, global versus project skills, and which endpoints the connectors must reach.