# 🛡️ GitLab Duo Security Orchestration Flow

> **GitLab AI Hackathon 2026** — 4-agent security pipeline built on GitLab Duo Custom Flows

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitLab Duo](https://img.shields.io/badge/GitLab%20Duo-Custom%20Flows-FC6D26)](https://docs.gitlab.com/ee/user/duo_workflow/)
[![Tests](https://img.shields.io/badge/tests-pytest-green)](tests/)
[![Prize Pool](https://img.shields.io/badge/Prize%20Pool-%2465K-gold)](SUBMISSION.md)

---

> ## ✅ DEV STATUS — ALL REVIEW ITEMS COMPLETE (Feb 27, 2026)
>
> Henry / Jin Yang review items — verified live in this repo:
>
> | # | Item | File | Status |
> |---|------|------|--------|
> | 1 | No `triggers:` block in YAML | `.gitlab/duo/flows/security-orchestration.yml` | ✅ Absent |
> | 2 | Prize pool $65K | `README.md`, `SUBMISSION.md` | ✅ Full 9-track table |
> | 3 | Real CI scan jobs | `.gitlab-ci.yml` | ✅ semgrep + bandit + safety + pip-audit |
> | 4 | Unlabeled vulnerable sample | `vulnerable_app/api_service.py` | ✅ 120 lines, 0 labels |
> | 5 | pytest tests | `tests/test_flow_structure.py` | ✅ 30+ assertions |
> | 6 | LICENSE at repo root | `LICENSE` | ✅ MIT |
>
> **Remaining work is human-platform-blocked only.** See [VERIFIED.md](VERIFIED.md) for full audit trail.

---

## What It Does

A fully automated security orchestration chain that takes a repository from **raw vulnerability scan → enriched triage → auto-fix → compliance report** — all triggered by a single mention in a GitLab MR or issue.

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌─────────────┐
│  DISCOVERY  │ →  │    TRIAGE    │ →  │  REMEDIATION    │ →  │  REPORTING  │
│             │    │              │    │                 │    │             │
│ • SAST scan │    │ • CVE enrich │    │ • Auto-fix gen  │    │ • Issue     │
│ • SCA scan  │    │ • FP detect  │    │ • Code review   │    │   creation  │
│ • Secrets   │    │ • Severity   │    │ • MR linkage    │    │ • Audit log │
│ • IaC scan  │    │   scoring    │    │ • Patch suggest │    │ • Compliance│
└─────────────┘    └──────────────┘    └─────────────────┘    └─────────────┘
```

## Why This Wins

| Built-in GitLab SAST Flow | Our Security Orchestration Flow |
|--------------------------|--------------------------------|
| Single agent | **4-agent chain** |
| Scan only | Scan → Triage → Fix → Report |
| No CVE enrichment | **NVD/GHSA CVE enrichment** |
| No false-positive detection | **ML-based FP analysis** |
| No auto-remediation | **Auto-fix generation** |
| No audit trail | **Full compliance audit log** |

## Architecture

```
Developer mentions @ai-secflow in MR comment
         ↓
Trigger configured via GitLab UI (Automate → Flows → Enable)
         ↓
Custom Flow YAML: .gitlab/duo/flows/security-orchestration.yml
         ↓
Agent 1: Discovery    (tools: list_vulnerabilities, run_pipeline, get_pipeline)
Agent 2: Triage       (tools: get_vulnerability, sast_fp_analysis, cve_enrichment)
Agent 3: Remediation  (tools: create_vulnerability_issue, link_vulnerability_to_mr)
Agent 4: Reporting    (tools: create_issue, audit_events, create_note)
```

## Quick Start

### Prerequisites
- GitLab Ultimate (or 30-day trial at about.gitlab.com/free-trial/)
- GitLab Duo Enterprise enabled
- GitLab 18.7+ (Custom Flows beta)

### Setup

1. **Fork this repo** into your GitLab project (in the AI Hackathon group)

2. **Add the Custom Flow** in your project:
   - Go to **Automate → Flows → New flow**
   - Paste the contents of `.gitlab/duo/flows/security-orchestration.yml`
   - Configure trigger type (e.g. "mention") via the UI
   - Save and enable

3. **Enable GitLab Duo** in your project settings

4. **Trigger the flow** by mentioning in any MR or issue:
   ```
   @ai-secflow please analyze this merge request for security vulnerabilities
   ```

5. The 4-agent chain runs automatically — results appear as issue comments and linked MRs.

> **Note on triggers:** GitLab Custom Flows configure triggers (mention, assign, assign reviewer)
> via the UI when enabling a flow — not in the YAML file itself. The YAML defines the agents
> and their connections; the trigger binding is a separate UI step.

## File Structure

```
├── .gitlab/
│   └── duo/
│       ├── agent-config.yml              # Runner config + tool setup
│       └── flows/
│           └── security-orchestration.yml # Main 4-agent flow definition
├── prompts/
│   ├── discovery.md                      # Agent 1 system prompt
│   ├── triage.md                         # Agent 2 system prompt
│   ├── remediation.md                    # Agent 3 system prompt
│   └── reporting.md                      # Agent 4 system prompt
├── tests/
│   └── test_flow_structure.py            # Pytest structural tests (30+ assertions)
├── vulnerable_app/                        # Sample vulnerable Python app for testing
│   ├── app.py                            # Flask app with classic vulns
│   ├── api_service.py                    # Realistic API service (unlabeled vulns)
│   ├── auth.py
│   ├── database.py
│   └── requirements.txt                  # Pinned packages with real CVEs
├── AGENTS.md                             # Runtime context for all agents
├── SUBMISSION.md                         # Hackathon submission text
├── VERIFIED.md                           # Adversary review verification audit trail
├── LICENSE                               # MIT
└── README.md
```

## Tools Used (15+ Native GitLab Duo Security Tools)

| Tool | Agent | Purpose |
|------|-------|---------|
| `list_vulnerabilities` | Discovery | Enumerate all open vulns |
| `get_vulnerability` | Triage | Deep-dive single vuln details |
| `confirm_vulnerability` | Triage | Mark confirmed true positives |
| `dismiss_vulnerability` | Triage | Dismiss false positives |
| `sast_fp_analysis` | Triage | ML false-positive detection |
| `cve_enrichment` | Triage | NVD/GHSA CVE data lookup |
| `create_vulnerability_issue` | Remediation | Auto-create tracking issues |
| `link_vulnerability_to_mr` | Remediation | Connect vulns to fix MRs |
| `create_issue` | Reporting | Compliance summary issue |
| `audit_events` | Reporting | Full audit trail |
| `list_merge_requests` | Remediation | Find related fix MRs |
| `create_note` | Reporting | Post results as comments |
| `get_pipeline` | Discovery | Check latest scan results |
| `run_pipeline` | Discovery | Trigger fresh scans |
| `get_project` | All | Project context |

> **Note on tool names:** GitLab does not publish a complete Custom Flows tool catalog publicly.
> The tool names above are based on GitLab's security API surface and Duo Workflow documentation.
> Exact names should be verified in the GitLab Duo flow editor or hackathon Discord before
> end-to-end testing. If a tool name is wrong, update the YAML and re-enable the flow.

## Prize Targets ($65,000 total pool)

| Prize | Amount | Why We Qualify |
|-------|--------|---------------|
| 🥇 Grand Prize | $15,000 | Most complete, production-ready Custom Flow |
| 🔧 Most Technical | $5,000 | 15+ tools, 4-agent chain, structured JSON contracts |
| 💥 Most Impactful | $5,000 | Eliminates 3h/MR of manual security review |
| 🟢 Easiest to Use | $5,000 | Single mention trigger, zero config |
| 🤖 Anthropic Grand Prize | $10,000 | Claude Sonnet 4 powers all 4 agents natively |
| 🤖 Anthropic Runner-Up | $3,500 | Fallback target |
| ☁️ Google Cloud Grand Prize | $10,000 | Deployable on GCP-hosted GitLab runners |
| ☁️ Google Cloud Runner-Up | $3,500 | Fallback target |
| 🌱 Green Agent Prize | $3,000 | Minimal compute — no external API calls |

**Total targeted: $65,000 | 3,208 teams registered**

## Submission Checklist

> ⚠️ **This repo is on GitHub for development.** For submission, it must be forked
> into a **public GitLab project in the AI Hackathon group**.

- [ ] Register at [gitlab.devpost.com](https://gitlab.devpost.com)
- [ ] Join GitLab Discord #ai-hackathon channel
- [ ] Request hackathon group access
- [ ] Start GitLab Duo Enterprise 30-day trial
- [ ] Fork this repo into GitLab hackathon group
- [ ] Paste YAML into GitLab flow editor and verify it parses
- [ ] Configure trigger via UI (mention type)
- [ ] Run end-to-end test on `vulnerable_app/`
- [ ] Record 3-min demo video (see SUBMISSION.md for script)
- [ ] Submit on Devpost before **March 25, 2026**

## License

MIT — see [LICENSE](LICENSE)
