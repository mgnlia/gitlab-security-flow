# 🛡️ GitLab Duo Security Orchestration Flow

> **GitLab AI Hackathon 2026** — 4-agent security pipeline built on GitLab Duo Custom Flows

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitLab Duo](https://img.shields.io/badge/GitLab%20Duo-Custom%20Flows-FC6D26)](https://docs.gitlab.com/ee/user/duo_workflow/)

## What It Does

A fully automated security orchestration chain that takes a repository from **raw vulnerability scan → enriched triage → auto-fix → compliance report** — all triggered by a single `@ai-secflow` mention in a GitLab MR or issue.

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
Developer mentions @ai-secflow-<group> in MR
         ↓
GitLab CI/CD Runner (docker, tagged: gitlab--duo)
         ↓
@gitlab/duo-cli → WebSocket → Duo Workflow Service
         ↓
Custom Flow YAML: security-orchestration-flow.yml
         ↓
Agent 1: Discovery    (tools: ListVulnerabilities, RunSAST, RunSCA)
Agent 2: Triage       (tools: GetVulnerability, CVEEnrich, SastFPAnalysis)
Agent 3: Remediation  (tools: CreateVulnerabilityIssue, LinkVulnToMR)
Agent 4: Reporting    (tools: CreateIssue, AuditEvents, ComplianceSummary)
```

## Quick Start

### Prerequisites
- GitLab Ultimate (or 30-day trial at about.gitlab.com/free-trial/)
- GitLab Duo Enterprise enabled
- GitLab 18.7+ (Custom Flows beta)

### Setup

1. **Fork this repo** into your GitLab project (in the AI Hackathon group)

2. **Enable GitLab Duo** in your project settings

3. **Trigger the flow** by mentioning in any MR or issue:
   ```
   @ai-secflow please analyze this merge request for security vulnerabilities
   ```

4. The 4-agent chain runs automatically — results appear as issue comments and linked MRs.

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
├── vulnerable_app/                        # Sample vulnerable Python app for testing
│   ├── app.py
│   ├── auth.py
│   ├── database.py
│   └── requirements.txt
├── AGENTS.md                             # Runtime context for all agents
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

## Prize Targets

- 🥇 Grand Prize: $15,000
- 🔧 Most Technical: $5,000
- 💥 Most Impactful: $5,000
- 🤖 Anthropic Grand Prize: $10,000 *(platform uses Claude Sonnet 4 natively)*
- ☁️ Google Cloud Prize: $10,000

**Total potential: $45,000**

## License

MIT — see [LICENSE](LICENSE)
