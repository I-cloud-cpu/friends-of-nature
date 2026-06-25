---
description: Security review of agent, hook, MCP, permission, and secret surfaces (optional AgentShield scanner).
agent: security-reviewer
subtask: true
---

# Security Scan Command

Review the current project (or a target path) for security issues across agent, hook, MCP,
permission, and secret surfaces, then turn findings into a prioritized remediation plan.

> **Availability:** The deterministic AgentShield scanner below is an *optional external* npm
> package (`ecc-agentshield`), network-fetched via `npx` — it is **not bundled** with this repo.
> If it is unavailable (offline, or Claude Code on the web), skip the scanner and run the
> **Review Checklist** manually via the `security-reviewer` agent. The checklist needs no
> external tooling and becomes the source of truth in that case.

## Usage

`/security-scan [path] [--format text|json|markdown|html] [--min-severity low|medium|high|critical] [--fix]`

- `path` (optional): defaults to the current project. Use a `.claude/` path, a repo root, or a checked-in template directory.
- `--format`: output format. Use `json` for CI, `markdown` for handoffs, and `html` for standalone review reports.
- `--min-severity`: filters lower-priority findings.
- `--fix`: applies only AgentShield fixes explicitly marked as safe and auto-fixable.

## Deterministic Engine

Prefer the packaged scanner:

```bash
npx ecc-agentshield scan --path "${TARGET_PATH:-.}" --format text
```

For local AgentShield development, run from the AgentShield checkout:

```bash
npm run scan -- --path "${TARGET_PATH:-.}" --format text
```

Do not invent findings. Use AgentShield output as the source of truth and separate scanner facts from follow-up judgment.

## Review Checklist

1. Identify active runtime findings first:
   - hardcoded secrets
   - broad permissions
   - executable hooks
   - MCP servers with shell, filesystem, remote transport, or unpinned `npx`
   - agent prompts that handle untrusted content without defenses
2. Separate lower-confidence inventory:
   - docs examples
   - template examples
   - plugin manifests
   - project-local optional settings
3. For each critical or high finding, return:
   - file path
   - severity
   - runtime confidence
   - why it matters
   - exact remediation
   - whether it is safe to auto-fix
4. If `--fix` is requested, state the planned edits before applying fixes.
5. Re-run the scan after fixes and report the before/after score.

## Output Contract

Return:

1. Security grade and score.
2. Counts by severity and runtime confidence.
3. Critical/high findings with exact paths.
4. Lower-confidence findings grouped separately.
5. A remediation order.
6. Commands run and whether the scan was local, CI, or npx-backed.

## CI Pattern

Use AgentShield in GitHub Actions for enforced gates:

```yaml
- uses: affaan-m/agentshield@v1
  with:
    path: "."
    min-severity: "medium"
    fail-on-findings: true
```

## Links

- Agent: `.claude/agents/security-reviewer.md` (installed)
- Rules: `.claude/rules/common/security.md`, `.claude/rules/web/security.md`, `.claude/rules/react/security.md`, `.claude/rules/typescript/security.md`
- Optional external scanner: <https://github.com/affaan-m/agentshield> (not bundled; network-fetched via `npx ecc-agentshield`)

## Arguments

$ARGUMENTS:
- optional target path
- optional AgentShield flags
