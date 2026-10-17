from __future__ import annotations

import unittest

from scenario_benchmark import run_scenarios


class ScenarioBenchmarkTests(unittest.TestCase):
    def test_all_six_safety_scenarios(self) -> None:
        result = run_scenarios()
        self.assertEqual(result["execution_status"], "MOCKED")
        self.assertEqual(result["summary"], {"scenario_count": 6, "verified": 6})
        self.assertTrue(all(item["status"] == "VERIFIED" for item in result["scenarios"]))


if __name__ == "__main__":
    unittest.main()
