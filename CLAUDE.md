# Friends of Nature

A modern website project. The agent tooling in `.claude/` is a curated subset of
[everything-claude-code (ECC)](https://github.com/affaan-m/everything-claude-code),
selected specifically for building and maintaining a Next.js / React + TypeScript website.

## Stack

- **Framework:** Next.js (App Router) + React
- **Language:** TypeScript
- **Focus areas:** design quality, accessibility (WCAG 2.2 AA), motion, SEO, performance, content

## Rules

Follow the project rules under `.claude/rules/` when writing or reviewing code:

- `rules/common/` — shared standards: code review, coding style, git workflow, performance, security, testing
- `rules/web/` — web coding style, **design-quality**, patterns, performance, security, testing
- `rules/react/` — React coding style, hooks, patterns, security, testing
- `rules/typescript/` — TypeScript coding style, patterns, security, testing

## Installed tooling (curated from ECC)

**Skills (25)** (`.claude/skills/`) — model-invoked when relevant:
design-system, frontend-design-direction, make-interfaces-feel-better, accessibility,
frontend-a11y, frontend-patterns, react-patterns, react-performance, react-testing,
nextjs-turbopack, motion-foundations, motion-patterns, motion-ui, seo, content-engine,
brand-voice, brand-discovery, e2e-testing, error-handling, deployment-patterns,
docker-patterns, api-design, backend-patterns, coding-standards, tdd-workflow.

**Agents (15)** (`.claude/agents/`): a11y-architect, react-reviewer, react-build-resolver,
typescript-reviewer, seo-specialist, code-reviewer, code-simplifier, refactor-cleaner,
performance-optimizer, security-reviewer, silent-failure-hunter, e2e-runner, architect,
planner, doc-updater.

**Commands (8)** (`.claude/commands/`): /feature-dev, /plan, /react-review,
/react-build, /react-test, /security-scan, /test-coverage, /pr.
(General code review uses Claude Code's built-in `/code-review` and `/review`.)

**MCP** (`.mcp.json`): `chrome-devtools` — for inspecting/debugging the running site.
Note: project MCP servers load only in a **local Claude Code** session (after approval/restart)
and require a Chrome/Chromium browser. It is **not active in Claude Code on the web**.

## Deliberately excluded from ECC

Other-language stacks (Swift/Kotlin/Rust/Go/Java/PHP/C++/Perl/.NET), non-React frameworks
(Django/Laravel/Spring/Quarkus/Vue), and unrelated domains (crypto/DeFi, prediction markets,
logistics/supply-chain, healthcare/HIPAA, scientific databases, media generation,
homelab/networking), plus the multi-agent orchestration/"epic" command suite, translated
docs, the ECC hook runtime, and the Python dashboard. None are relevant to this website.

> Source: ECC v2.0.0 (MIT, © Affaan Mustafa). Components copied as-is under their original license.
