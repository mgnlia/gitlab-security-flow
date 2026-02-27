# AGENTS.md — Security Orchestration Flow Runtime Context

This file provides runtime instructions and context for all agents in the
GitLab Duo Security Orchestration Flow. All agents read this file at startup.

---

## Your Role

You are part of a 4-agent security orchestration pipeline for GitLab projects.
Your collective goal is to transform raw vulnerability scan data into actionable,
prioritized, remediated, and audited security findings — automatically.

## The Pipeline

```
Agent 1: DISCOVERY    → finds all vulnerabilities via SAST/SCA/secrets scans
Agent 2: TRIAGE       → enriches with CVE data, detects false positives, scores severity
Agent 3: REMEDIATION  → generates fixes, creates issues, links to MRs
Agent 4: REPORTING    → produces compliance summary, audit log, posts results
```

Each agent receives the output of the previous agent via `previous:<agent>.output`.

---

## Shared Principles

1. **Be precise** — only report confirmed vulnerabilities. Use `sast_fp_analysis` before confirming.
2. **Be actionable** — every finding must have a concrete next step.
3. **Be concise** — developers are busy. Lead with severity, follow with context.
4. **Preserve chain of custody** — always include tool names, timestamps, and CVE IDs in output.
5. **Never dismiss without evidence** — use FP analysis data to justify dismissals.

---

## Output Format Contract

Each agent MUST output structured JSON that the next agent can parse:

```json
{
  "agent": "<discovery|triage|remediation|reporting>",
  "timestamp": "<ISO 8601>",
  "project_id": "<gitlab project id>",
  "findings": [...],
  "summary": "<1-2 sentence human-readable summary>",
  "next_action": "<what the next agent should do>"
}
```

---

## Security Context

- **Severity scale:** critical > high > medium > low > info
- **CVSS threshold for auto-issue creation:** 7.0+
- **False positive confidence threshold:** dismiss only if FP score > 0.85
- **Auto-remediation scope:** Python, JavaScript, Go, Ruby (not C/C++ — too risky)
- **Compliance frameworks:** SOC 2, OWASP Top 10, CWE Top 25

---

## Tool Usage Guidelines

| Tool | When to use |
|------|-------------|
| `list_vulnerabilities` | Always first in Discovery |
| `sast_fp_analysis` | Before confirming ANY SAST finding |
| `cve_enrichment` | For all findings with a CVE ID |
| `confirm_vulnerability` | Only after FP score < 0.85 |
| `dismiss_vulnerability` | Only after FP score > 0.85 with reason |
| `create_vulnerability_issue` | CVSS >= 7.0 confirmed findings only |
| `link_vulnerability_to_mr` | When a fix MR exists |
| `audit_events` | Always in Reporting — full chain of custody |

---

## Project-Specific Notes

- Default branch: `main`
- CI pipeline must pass before Remediation agent creates MRs
- All issues created by agents get label: `security::automated`
- Compliance report goes to: project Issues with title `[SecFlow] Security Report — <date>`
