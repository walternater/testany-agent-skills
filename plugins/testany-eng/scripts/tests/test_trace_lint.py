from __future__ import annotations

import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "trace_lint.py"


def build_markdown(metadata_yaml: str) -> str:
    return textwrap.dedent(
        f"""\
        # PRD: 示例

        <!-- TRACEABILITY-METADATA:BEGIN -->
        ```yaml
        {metadata_yaml.rstrip()}
        ```
        <!-- TRACEABILITY-METADATA:END -->
        """
    )


VALID_METADATA = """
schema:
  name: testany-traceability
  version: "1.0.0"
  profile: prd-profile-v1
artifact:
  id: PRD-CHECKOUT-001
  type: PRD
  title: 优惠券结算能力
  status: draft
  owners:
    - product.checkout
  created_at: 2026-03-08
  updated_at: 2026-03-08
  source_documents:
    - BRD-CHECKOUT-001
entities:
  requirements:
    - id: REQ-CHECKOUT-001
      class: functional
      title: 支持在结算页应用优惠券
      statement: 系统必须允许用户在结算页输入有效优惠券并应用折扣。
      priority: P0
      status: proposed
      scope: in
      acceptance_criteria:
        - 用户输入有效优惠券后，必须展示折后金额。
      source_refs:
        - artifact_id: BRD-CHECKOUT-001
          section: 3.1
  risks: []
  must_not_regress: []
  external_behaviors: []
  decisions: []
  flows: []
  test_cases: []
relations:
  - id: REL-CHECKOUT-001
    type: derived_from
    from: REQ-CHECKOUT-001
    to: BRD-CHECKOUT-001
    status: active
waivers: []
"""


WARNING_METADATA = """
schema:
  name: testany-traceability
  version: "1.0.0"
  profile: prd-profile-v1
artifact:
  id: PRD-CHECKOUT-001
  type: PRD
  title: 优惠券结算能力
  status: draft
  created_at: 2026-03-08
  updated_at: 2026-03-08
  source_documents:
    - BRD-CHECKOUT-001
entities:
  requirements:
    - id: REQ-CHECKOUT-001
      class: functional
      title: 支持在结算页应用优惠券
      statement: 系统必须允许用户在结算页输入有效优惠券并应用折扣。
      priority: P0
      status: proposed
      scope: in
      acceptance_criteria:
        - 用户输入有效优惠券后，必须展示折后金额。
  risks: []
  must_not_regress: []
  external_behaviors: []
  decisions: []
  flows: []
  test_cases: []
relations:
  - id: REL-CHECKOUT-001
    type: derived_from
    from: REQ-CHECKOUT-001
    to: BRD-CHECKOUT-001
    status: active
waivers: []
"""


EXTERNAL_TARGET_METADATA = """
schema:
  name: testany-traceability
  version: "1.0.0"
  profile: test-spec-profile-v1
artifact:
  id: TSPEC-CHECKOUT-001
  type: TEST_SPEC
  title: 优惠券结算测试包
  status: draft
  created_at: 2026-03-08
  updated_at: 2026-03-08
  source_documents:
    - PRD-CHECKOUT-001
entities:
  requirements: []
  risks: []
  must_not_regress: []
  external_behaviors: []
  decisions: []
  flows: []
  test_cases:
    - id: CASE-CHECKOUT-001
      title: 优惠券主流程
      statement: 验证用户在结算页成功应用优惠券。
      status: proposed
      scope: in
      layer: e2e
      priority: P0
      source_refs:
        - artifact_id: PRD-CHECKOUT-001
          section: 3.1
relations:
  - id: REL-CHECKOUT-001
    type: verifies
    from: CASE-CHECKOUT-001
    to: REQ-CHECKOUT-001
    status: active
waivers: []
"""


VALID_TEST_STRATEGY_METADATA = """
schema:
  name: testany-traceability
  version: "1.0.0"
  profile: test-strategy-profile-v1
artifact:
  id: TSTRAT-CHECKOUT-001
  type: TEST_STRATEGY
  title: 优惠券结算测试策略
  status: draft
  created_at: 2026-03-08
  updated_at: 2026-03-08
  source_documents:
    - PRD-CHECKOUT-001
entities:
  requirements: []
  risks:
    - id: RISK-CHECKOUT-001
      title: 折扣展示金额与实际入单金额不一致
      statement: 结算页展示金额与订单最终成交金额可能不一致。
      status: proposed
      scope: in
      level: high
      source_refs:
        - artifact_id: PRD-CHECKOUT-001
          section: 2.3
  must_not_regress:
    - id: MR-CHECKOUT-001
      title: 原价下单流程不能退化
      statement: 用户不使用优惠券时的原价下单流程必须保持稳定。
      status: proposed
      scope: in
      priority: P0
      source_refs:
        - artifact_id: PRD-CHECKOUT-001
          section: 3.2
  external_behaviors:
    - id: BEH-CHECKOUT-001
      title: 结算页展示折后金额
      statement: 用户输入有效优惠券后，结算页必须展示折后金额。
      status: proposed
      scope: in
      source_refs:
        - artifact_id: PRD-CHECKOUT-001
          section: 3.1
  decisions: []
  flows: []
  test_cases: []
relations:
  - id: REL-TSTRAT-001
    type: derived_from
    from: RISK-CHECKOUT-001
    to: REQ-CHECKOUT-001
    status: active
  - id: REL-TSTRAT-002
    type: derived_from
    from: MR-CHECKOUT-001
    to: REQ-CHECKOUT-001
    status: active
  - id: REL-TSTRAT-003
    type: derived_from
    from: BEH-CHECKOUT-001
    to: REQ-CHECKOUT-001
    status: active
waivers: []
"""


VALID_TEST_SPEC_METADATA = """
schema:
  name: testany-traceability
  version: "1.0.0"
  profile: test-spec-profile-v1
artifact:
  id: TSPEC-CHECKOUT-001
  type: TEST_SPEC
  title: 优惠券结算测试包
  status: draft
  created_at: 2026-03-08
  updated_at: 2026-03-08
  source_documents:
    - PRD-CHECKOUT-001
    - TSTRAT-CHECKOUT-001
entities:
  requirements: []
  risks: []
  must_not_regress: []
  external_behaviors: []
  decisions: []
  flows: []
  test_cases:
    - id: CASE-CHECKOUT-001
      title: 有效优惠券成功应用
      statement: 验证用户在结算页成功应用优惠券。
      status: proposed
      scope: in
      layer: e2e
      priority: P0
      automation: must
      source_refs:
        - artifact_id: PRD-CHECKOUT-001
          section: 3.1
relations:
  - id: REL-TSPEC-001
    type: verifies
    from: CASE-CHECKOUT-001
    to: REQ-CHECKOUT-001
    status: active
waivers: []
"""


INVALID_TEST_SPEC_METADATA = """
schema:
  name: testany-traceability
  version: "1.0.0"
  profile: test-spec-profile-v1
artifact:
  id: TSPEC-CHECKOUT-001
  type: TEST_SPEC
  title: 优惠券结算测试包
  status: draft
  created_at: 2026-03-08
  updated_at: 2026-03-08
  source_documents:
    - PRD-CHECKOUT-001
entities:
  requirements: []
  risks: []
  must_not_regress: []
  external_behaviors: []
  decisions: []
  flows: []
  test_cases:
    - id: CASE-CHECKOUT-001
      title: 有效优惠券成功应用
      statement: 验证用户在结算页成功应用优惠券。
      status: proposed
      scope: in
      layer: e2e
      priority: P0
      source_refs:
        - artifact_id: PRD-CHECKOUT-001
          section: 3.1
relations: []
waivers: []
"""


class TraceLintCliTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT_PATH), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_markdown_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "prd.md"
            path.write_text(build_markdown(VALID_METADATA), encoding="utf-8")

            result = self.run_cli(str(path))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TRACE-LINT RESULT: PASS", result.stdout)
        self.assertIn("Errors: 0", result.stdout)
        self.assertIn("Warnings: 0", result.stdout)

    def test_json_output_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "prd.yaml"
            path.write_text(textwrap.dedent(VALID_METADATA).strip() + "\n", encoding="utf-8")

            result = self.run_cli("--format", "json", str(path))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["tool"], "trace-lint")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["summary"]["passed"], 1)
        self.assertEqual(payload["artifacts"][0]["artifact_id"], "PRD-CHECKOUT-001")
        self.assertEqual(payload["artifacts"][0]["profile"], "prd-profile-v1")

    def test_missing_metadata_block_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "prd.md"
            path.write_text("# PRD: Missing Metadata\n", encoding="utf-8")

            result = self.run_cli(str(path))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("TRACE001", result.stdout)
        self.assertIn("TRACE-LINT RESULT: FAIL", result.stdout)

    def test_warning_is_non_blocking_unless_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "prd.md"
            path.write_text(build_markdown(WARNING_METADATA), encoding="utf-8")

            non_strict = self.run_cli(str(path))
            strict = self.run_cli("--strict", str(path))

        self.assertEqual(non_strict.returncode, 0, non_strict.stdout + non_strict.stderr)
        self.assertIn("TRACE303", non_strict.stdout)
        self.assertIn("Warnings: 1", non_strict.stdout)

        self.assertEqual(strict.returncode, 1, strict.stdout + strict.stderr)
        self.assertIn("TRACE303", strict.stdout)
        self.assertIn("TRACE-LINT RESULT: FAIL", strict.stdout)

    def test_missing_input_path_returns_exit_2(self) -> None:
        result = self.run_cli("/tmp/definitely-not-existing-trace-lint-file.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("input file does not exist", result.stderr)

    def test_external_entity_target_is_allowed_as_info(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test-spec.yaml"
            path.write_text(textwrap.dedent(EXTERNAL_TARGET_METADATA).strip() + "\n", encoding="utf-8")

            result = self.run_cli(str(path))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TRACE404", result.stdout)
        self.assertIn("Infos: 1", result.stdout)

    def test_valid_test_strategy_profile_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test-strategy.yaml"
            path.write_text(textwrap.dedent(VALID_TEST_STRATEGY_METADATA).strip() + "\n", encoding="utf-8")

            result = self.run_cli(str(path))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TRACE-LINT RESULT: PASS", result.stdout)

    def test_valid_test_spec_profile_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test-spec.yaml"
            path.write_text(textwrap.dedent(VALID_TEST_SPEC_METADATA).strip() + "\n", encoding="utf-8")

            result = self.run_cli(str(path))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TRACE-LINT RESULT: PASS", result.stdout)

    def test_test_spec_requires_traceability_relations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test-spec.yaml"
            path.write_text(textwrap.dedent(INVALID_TEST_SPEC_METADATA).strip() + "\n", encoding="utf-8")

            result = self.run_cli(str(path))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("TRACE604", result.stdout)


if __name__ == "__main__":
    unittest.main()
