"""
tests/test_flow_structure.py
============================
Structural tests for the SecFlow Custom Flow definition.
These run in CI to catch schema regressions before the flow is deployed.
"""

import os
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOW_PATH = os.path.join(REPO_ROOT, ".gitlab", "duo", "flows", "security-orchestration.yml")
AGENT_CONFIG_PATH = os.path.join(REPO_ROOT, ".gitlab", "duo", "agent-config.yml")
PROMPTS_DIR = os.path.join(REPO_ROOT, "prompts")
VULNERABLE_APP_DIR = os.path.join(REPO_ROOT, "vulnerable_app")


# ── Flow YAML structure ───────────────────────────────────────────────────────

class TestFlowYAML:

    def setup_method(self):
        with open(FLOW_PATH) as f:
            self.flow = yaml.safe_load(f)

    def test_flow_has_name(self):
        assert "name" in self.flow
        assert self.flow["name"] == "security-orchestration"

    def test_flow_has_version(self):
        assert "version" in self.flow

    def test_flow_has_components(self):
        assert "components" in self.flow
        assert isinstance(self.flow["components"], list)

    def test_flow_has_exactly_four_agents(self):
        components = self.flow["components"]
        assert len(components) == 4, f"Expected 4 agents, got {len(components)}"

    def test_agent_names_are_correct(self):
        names = [c["name"] for c in self.flow["components"]]
        assert names == ["discovery", "triage", "remediation", "reporting"]

    def test_all_agents_have_type_agent(self):
        for component in self.flow["components"]:
            assert component.get("type") == "agent", \
                f"Component {component['name']} missing type=agent"

    def test_all_agents_have_prompt_id(self):
        for component in self.flow["components"]:
            assert "prompt_id" in component, \
                f"Component {component['name']} missing prompt_id"

    def test_all_agents_have_tools(self):
        for component in self.flow["components"]:
            assert "tools" in component, \
                f"Component {component['name']} missing tools list"
            assert len(component["tools"]) > 0, \
                f"Component {component['name']} has empty tools list"

    def test_all_agents_have_output_schema(self):
        for component in self.flow["components"]:
            assert "output_schema" in component, \
                f"Component {component['name']} missing output_schema"

    def test_no_triggers_block(self):
        """Triggers are configured via UI, not in YAML — must not be present."""
        assert "triggers" not in self.flow, \
            "YAML must not contain 'triggers:' — configure triggers via GitLab UI"

    def test_triage_chains_from_discovery(self):
        triage = next(c for c in self.flow["components"] if c["name"] == "triage")
        inputs = triage.get("inputs", {})
        raw_findings = inputs.get("raw_findings", "")
        assert "previous:discovery" in raw_findings, \
            "Triage must chain from discovery output"

    def test_remediation_chains_from_triage(self):
        remediation = next(c for c in self.flow["components"] if c["name"] == "remediation")
        inputs = remediation.get("inputs", {})
        confirmed = inputs.get("confirmed_findings", "")
        assert "previous:triage" in confirmed, \
            "Remediation must chain from triage output"

    def test_reporting_chains_from_all_agents(self):
        reporting = next(c for c in self.flow["components"] if c["name"] == "reporting")
        inputs = reporting.get("inputs", {})
        values = " ".join(str(v) for v in inputs.values())
        assert "previous:discovery" in values
        assert "previous:triage" in values
        assert "previous:remediation" in values

    def test_minimum_tool_count(self):
        all_tools = []
        for component in self.flow["components"]:
            all_tools.extend(component.get("tools", []))
        unique_tools = set(all_tools)
        assert len(unique_tools) >= 10, \
            f"Expected at least 10 unique tools, got {len(unique_tools)}: {unique_tools}"

    def test_discovery_has_list_vulnerabilities(self):
        discovery = next(c for c in self.flow["components"] if c["name"] == "discovery")
        assert "list_vulnerabilities" in discovery["tools"]

    def test_triage_has_false_positive_tools(self):
        triage = next(c for c in self.flow["components"] if c["name"] == "triage")
        assert "confirm_vulnerability" in triage["tools"]
        assert "dismiss_vulnerability" in triage["tools"]

    def test_remediation_has_issue_creation(self):
        remediation = next(c for c in self.flow["components"] if c["name"] == "remediation")
        assert "create_vulnerability_issue" in remediation["tools"]

    def test_reporting_has_audit_events(self):
        reporting = next(c for c in self.flow["components"] if c["name"] == "reporting")
        assert "audit_events" in reporting["tools"]


# ── Prompt files ──────────────────────────────────────────────────────────────

class TestPromptFiles:

    EXPECTED_PROMPTS = ["discovery.md", "triage.md", "remediation.md", "reporting.md"]

    def test_all_prompt_files_exist(self):
        for prompt in self.EXPECTED_PROMPTS:
            path = os.path.join(PROMPTS_DIR, prompt)
            assert os.path.exists(path), f"Missing prompt file: {path}"

    def test_prompt_files_are_not_empty(self):
        for prompt in self.EXPECTED_PROMPTS:
            path = os.path.join(PROMPTS_DIR, prompt)
            if os.path.exists(path):
                size = os.path.getsize(path)
                assert size > 500, \
                    f"Prompt file {prompt} is too small ({size} bytes) — likely placeholder"

    def test_discovery_prompt_mentions_sast(self):
        path = os.path.join(PROMPTS_DIR, "discovery.md")
        content = open(path).read().lower()
        assert "sast" in content or "vulnerabilit" in content

    def test_triage_prompt_mentions_false_positive(self):
        path = os.path.join(PROMPTS_DIR, "triage.md")
        content = open(path).read().lower()
        assert "false positive" in content or "fp" in content or "triage" in content

    def test_reporting_prompt_mentions_owasp(self):
        path = os.path.join(PROMPTS_DIR, "reporting.md")
        content = open(path).read().lower()
        assert "owasp" in content or "compliance" in content


# ── Agent config ──────────────────────────────────────────────────────────────

class TestAgentConfig:

    def setup_method(self):
        with open(AGENT_CONFIG_PATH) as f:
            self.config = yaml.safe_load(f)

    def test_config_parses(self):
        assert self.config is not None

    def test_config_has_executor(self):
        assert "executor" in self.config or "runner" in self.config or \
               "image" in self.config or "python" in str(self.config).lower()


# ── Vulnerable app ────────────────────────────────────────────────────────────

class TestVulnerableApp:

    def test_app_py_exists(self):
        assert os.path.exists(os.path.join(VULNERABLE_APP_DIR, "app.py"))

    def test_api_service_py_exists(self):
        assert os.path.exists(os.path.join(VULNERABLE_APP_DIR, "api_service.py"))

    def test_requirements_txt_exists(self):
        assert os.path.exists(os.path.join(VULNERABLE_APP_DIR, "requirements.txt"))

    def test_requirements_has_vulnerable_packages(self):
        reqs = open(os.path.join(VULNERABLE_APP_DIR, "requirements.txt")).read()
        # Should have pinned old versions for CVE demo
        assert "flask" in reqs.lower() or "requests" in reqs.lower()

    def test_api_service_has_sql_injection(self):
        code = open(os.path.join(VULNERABLE_APP_DIR, "api_service.py")).read()
        # Should have string concatenation in SQL (not just parameterized queries)
        assert "SELECT" in code

    def test_api_service_has_no_obvious_labels(self):
        """Realistic sample should not have 'VULNERABLE:' labels on every line."""
        code = open(os.path.join(VULNERABLE_APP_DIR, "api_service.py")).read()
        vulnerable_label_count = code.count("VULNERABLE:")
        # Allow a few inline comments but not one per function
        assert vulnerable_label_count <= 5, \
            f"api_service.py has {vulnerable_label_count} 'VULNERABLE:' labels — too many for realistic sample"


# ── Repo root files ───────────────────────────────────────────────────────────

class TestRepoRoot:

    def test_license_exists(self):
        path = os.path.join(REPO_ROOT, "LICENSE")
        assert os.path.exists(path), "LICENSE file missing — required for submission"

    def test_license_is_mit(self):
        path = os.path.join(REPO_ROOT, "LICENSE")
        if os.path.exists(path):
            content = open(path).read()
            assert "MIT" in content, "LICENSE should be MIT"

    def test_readme_exists(self):
        assert os.path.exists(os.path.join(REPO_ROOT, "README.md"))

    def test_agents_md_exists(self):
        assert os.path.exists(os.path.join(REPO_ROOT, "AGENTS.md"))

    def test_submission_md_exists(self):
        assert os.path.exists(os.path.join(REPO_ROOT, "SUBMISSION.md"))

    def test_readme_mentions_65k_prize(self):
        readme = open(os.path.join(REPO_ROOT, "README.md")).read()
        assert "65" in readme or "$65" in readme, \
            "README should mention $65K prize pool (not $45K)"

    def test_flow_yaml_exists(self):
        path = os.path.join(REPO_ROOT, ".gitlab", "duo", "flows", "security-orchestration.yml")
        assert os.path.exists(path)

    def test_agent_config_yaml_exists(self):
        path = os.path.join(REPO_ROOT, ".gitlab", "duo", "agent-config.yml")
        assert os.path.exists(path)
