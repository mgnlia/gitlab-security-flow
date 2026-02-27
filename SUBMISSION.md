# GitLab AI Hackathon — Submission Description

## Project Name
**SecFlow: 4-Agent Security Orchestration for GitLab Duo**

## One-Line Description
A GitLab Duo Custom Flow that chains 4 AI agents (Discovery → Triage → Remediation → Reporting) to fully automate the vulnerability management lifecycle — from raw scan to compliance report — triggered by a single `@ai-secflow` mention.

## Problem Statement
GitLab's built-in SAST Flow uses a **single agent** that only scans. Security teams still manually:
1. Enrich CVE data from NVD/GHSA
2. Detect false positives in SAST output (typically 40-60% FP rate)
3. Create tracking issues for confirmed findings
4. Write compliance reports for SOC 2 / OWASP audits

This takes 2-4 hours per MR review cycle. SecFlow does it in under 5 minutes, automatically.

## Solution

### Architecture
```
Developer: @ai-secflow please review this MR
    ↓
GitLab Duo Custom Flow: security-orchestration.yml
    ↓
Agent 1: DISCOVERY
  - Runs SAST, dependency scanning, secrets detection
  - Uses: list_vulnerabilities, get_pipeline, run_pipeline
  - Output: 12 raw findings

Agent 2: TRIAGE
  - CVE enrichment via NVD/GHSA for each finding
  - ML false-positive detection (sast_fp_analysis)
  - CVSS v3 scoring + EPSS exploit prediction
  - Uses: get_vulnerability, sast_fp_analysis, cve_enrichment, confirm_vulnerability, dismiss_vulnerability
  - Output: 8 confirmed (2 P0, 3 P1, 3 P2), 4 dismissed as FP

Agent 3: REMEDIATION
  - Generates parameterized-query fixes for SQL injection
  - Creates GitLab issues for CVSS ≥ 7.0 findings
  - Links findings to existing fix MRs
  - Uses: create_vulnerability_issue, link_vulnerability_to_mr, create_note
  - Output: 5 issues created, 2 fix MRs linked, 5 code fixes generated

Agent 4: REPORTING
  - OWASP Top 10 + SOC 2 compliance mapping
  - Security posture score (0-100)
  - Full audit trail via audit_events
  - Posts compliance report as GitLab issue
  - Uses: create_issue, create_note, audit_events
  - Output: Issue #99 "[SecFlow] Security Report — Score: 72/100"
```

### Novel Contributions vs Built-in SAST Flow
| Feature | Built-in SAST | SecFlow |
|---------|--------------|---------|
| Agents | 1 | **4** |
| CVE enrichment | ❌ | **✅ NVD/GHSA** |
| False positive detection | ❌ | **✅ ML-based** |
| Auto-issue creation | ❌ | **✅ CVSS ≥ 7.0** |
| Code fix generation | ❌ | **✅ Python/JS/Go** |
| Compliance reporting | ❌ | **✅ OWASP + SOC 2** |
| Audit trail | ❌ | **✅ Full chain** |
| Tools used | ~3 | **15+** |

## Technical Details
- **Platform:** GitLab Duo Custom Flows (Beta 18.7+)
- **LLM:** Claude Sonnet 4 (automatic via Duo Enterprise)
- **Execution:** CI/CD runner (tagged `gitlab--duo`) → `@gitlab/duo-cli` → WebSocket → Duo Workflow Service
- **Agent chaining:** `previous:<agent>.output` in YAML inputs
- **Tools used:** 15+ native GitLab security tools

## Demo Script (3 minutes)

### Minute 1 — Setup (0:00-1:00)
- Show `security-orchestration.yml` — 4 agents, chained inputs
- Show `vulnerable_app/app.py` — SQL injection, hardcoded secrets, command injection
- Show `.gitlab/duo/agent-config.yml` — Python 3.11 + semgrep + bandit

### Minute 2 — Flow Execution (1:00-2:00)
- Open MR with vulnerable code changes
- Type: `@ai-secflow please analyze this MR`
- Watch Agent 1 (Discovery) run — shows 12 raw findings
- Watch Agent 2 (Triage) — CVE enrichment, 4 FPs dismissed, 8 confirmed
- Watch Agent 3 (Remediation) — 5 issues auto-created with fix suggestions
- Watch Agent 4 (Reporting) — compliance report issue posted

### Minute 3 — Results (2:00-3:00)
- Show auto-created issues with CVSS scores and fix code
- Show compliance report: OWASP Top 10 mapping, score 72/100
- Show audit trail — full chain of custody
- Highlight: "This replaced 3 hours of manual security review"

## Prize Tracks
- **Grand Prize ($15K):** Most complete, production-ready Custom Flow
- **Most Technical ($5K):** 15+ tools, 4-agent chain, structured JSON contracts
- **Most Impactful ($5K):** Eliminates 3h/MR of manual security review
- **Anthropic Grand Prize ($10K):** Claude Sonnet 4 powers all 4 agents natively
- **Google Cloud Prize ($10K):** Deployable on Google Cloud-hosted GitLab runners

## Open Source License
MIT — see LICENSE
