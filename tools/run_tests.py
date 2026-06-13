"""Run the unit-test suite and persist the results to ``test-reports/``.

Besides the usual console output, this writes:

* ``test-reports/unit-tests.xml``  - JUnit XML (machine readable, for CI dashboards)
* ``test-reports/unit-report.md``  - human-readable Markdown summary
* ``test-reports/taxonomy-summary.md`` - results grouped by white / gray box
* ``test-reports/coverage.xml`` / ``coverage.md`` - when ``--coverage`` is passed
* ``test-reports/history/unit-report-<timestamp>.md`` - timestamped archive

Usage:
    python tools/run_tests.py
    python tools/run_tests.py --coverage
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
import time
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"
REPORTS_DIR = REPO_ROOT / "test-reports"
TOOLS_DIR = REPO_ROOT / "tools"

sys.path.insert(0, str(TESTS_DIR))
sys.path.insert(0, str(TOOLS_DIR))
from test_markers import BLACK_BOX, BOX_LABELS, GRAY_BOX, WHITE_BOX, classification_for  # noqa: E402
from test_catalog import (  # noqa: E402
    SUBJECTS,
    describe_failure,
    group_records_by_subject,
    subject_for,
)
from taxonomy_report import write_taxonomy_summary  # noqa: E402


class RecordingResult(unittest.TextTestResult):
    """Collects per-test outcome + timing so we can emit reports afterwards."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records: list[dict] = []
        self._start_times: dict = {}

    def startTest(self, test):
        self._start_times[test] = time.perf_counter()
        super().startTest(test)

    def _elapsed(self, test) -> float:
        return time.perf_counter() - self._start_times.get(test, time.perf_counter())

    def _record(self, test, status: str, message: str) -> dict:
        box = classification_for(test)
        return {
            "classname": f"{test.__class__.__module__}.{test.__class__.__qualname__}",
            "name": getattr(test, "_testMethodName", str(test)),
            "status": status,
            "time": self._elapsed(test),
            "message": message or "",
            "box": box,
            "box_label": BOX_LABELS[box],
        }

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append(self._record(test, "pass", ""))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append(self._record(test, "fail", self._exc_info_to_string(err, test)))

    def addError(self, test, err):
        super().addError(test, err)
        self.records.append(self._record(test, "error", self._exc_info_to_string(err, test)))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append(self._record(test, "skip", reason))

    def addSubTest(self, test, subtest, outcome):
        super().addSubTest(test, subtest, outcome)
        if outcome is not None:
            status = "fail" if issubclass(outcome[0], test.failureException) else "error"
            self.records.append(self._record(subtest, status, self._exc_info_to_string(outcome, test)))


def _counts(records):
    summary = {"pass": 0, "fail": 0, "error": 0, "skip": 0}
    for record in records:
        summary[record["status"]] = summary.get(record["status"], 0) + 1
    return summary


def write_junit_xml(records, total_time, path: Path):
    counts = _counts(records)
    suite = ET.Element(
        "testsuite",
        name="icity-unit-tests",
        tests=str(len(records)),
        failures=str(counts["fail"]),
        errors=str(counts["error"]),
        skipped=str(counts["skip"]),
        time=f"{total_time:.3f}",
        timestamp=_dt.datetime.now().isoformat(timespec="seconds"),
    )
    for record in records:
        case = ET.SubElement(
            suite,
            "testcase",
            classname=record["classname"],
            name=record["name"],
            time=f"{record['time']:.3f}",
        )
        case.set("classification", record["box"])
        if record["status"] == "fail":
            ET.SubElement(case, "failure", message="assertion failed").text = record["message"]
        elif record["status"] == "error":
            ET.SubElement(case, "error", message="unexpected error").text = record["message"]
        elif record["status"] == "skip":
            ET.SubElement(case, "skipped", message=record["message"])
    xml_bytes = ET.tostring(suite, encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="utf-8")
    path.write_bytes(pretty)


def _icon(status: str) -> str:
    return {"pass": "✅", "fail": "❌", "error": "💥", "skip": "⏭️"}.get(status, status)


def write_markdown(records, total_time, path: Path):
    counts = _counts(records)
    overall = "PASS" if counts["fail"] == 0 and counts["error"] == 0 else "FAIL"
    timestamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# 单元测试报告",
        "",
        f"- 运行时间：{timestamp}",
        f"- 总体结果：**{overall}**",
        f"- 用例统计：共 {len(records)}，通过 {counts['pass']}，"
        f"失败 {counts['fail']}，错误 {counts['error']}，跳过 {counts['skip']}",
        f"- 总耗时：{total_time:.3f}s",
        "",
        "> 本报告按**测试对象**（被测模块/功能）归类，不列出测试代码路径。",
        "> 盒模型汇总见 [`taxonomy-summary.md`](taxonomy-summary.md)。",
        "",
        "## 按测试对象汇总",
        "",
        "| 分类 | 测试对象 | 被测模块/功能 | 测什么 | 用例数 | 通过 | 结果 |",
        "|---|---|---|---|---:|---:|---|",
    ]

    grouped = group_records_by_subject(records)
    subject_order = {sid: idx for idx, sid in enumerate(SUBJECTS)}
    sorted_keys = sorted(
        grouped.keys(),
        key=lambda k: (
            (WHITE_BOX, GRAY_BOX, BLACK_BOX).index(k[0]),
            subject_order.get(k[1], 999),
        ),
    )
    for box, sid in sorted_keys:
        box_records = grouped[(box, sid)]
        box_counts = _counts(box_records)
        subj = SUBJECTS.get(sid, subject_for(box_records[0]["classname"]))
        ok = box_counts["fail"] == 0 and box_counts["error"] == 0
        icon = "✅" if ok else "❌"
        lines.append(
            f"| {BOX_LABELS[box]} | {subj['name']} | `{subj['product']}` | "
            f"{subj['scope']} | {len(box_records)} | {box_counts['pass']} | {icon} |"
        )

    lines.append("")

    failures = [r for r in records if r["status"] in ("fail", "error")]
    if failures:
        lines += ["## 失败 / 错误明细", ""]
        for record in failures:
            lines.append(
                f"### {_icon(record['status'])} [{record['box_label']}] "
                f"{describe_failure(record['classname'], record['name'])}"
            )
            lines += ["", "```", record["message"].strip(), "```", ""]

    for box in (WHITE_BOX, GRAY_BOX, BLACK_BOX):
        box_records = [r for r in records if r["box"] == box]
        if not box_records:
            continue
        box_counts = _counts(box_records)
        lines += [
            f"## {BOX_LABELS[box]} — 测试范围",
            "",
            f"共 **{len(box_records)}** 项：通过 {box_counts['pass']}，"
            f"失败 {box_counts['fail']}，错误 {box_counts['error']}，跳过 {box_counts['skip']}",
            "",
        ]
        seen: set[str] = set()
        for _, sid in sorted_keys:
            if sid in seen:
                continue
            if (box, sid) not in grouped:
                continue
            seen.add(sid)
            subj = SUBJECTS.get(sid, {"name": sid, "product": sid, "scope": ""})
            n = len(grouped[(box, sid)])
            lines.append(f"### {subj['name']}（{n} 项）")
            lines.append("")
            lines.append(f"- **被测对象**：`{subj['product']}`")
            lines.append(f"- **测试重点**：{subj['scope']}")
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_coverage_markdown(report_lines: list[str], path: Path):
    timestamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 代码覆盖率报告",
        "",
        f"- 运行时间：{timestamp}",
        f"- 范围：`iCity/smart_city/`（见仓库根目录 `.coveragerc`）",
        "",
        "```",
        *report_lines,
        "```",
        "",
        "HTML 详情：`test-reports/coverage-html/index.html`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def discover_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(TESTS_DIR), pattern="test_*.py", top_level_dir=str(TESTS_DIR))
    blender_only = ("blender.test_generate_ops",)
    filtered = unittest.TestSuite()
    for group in suite:
        for case in group:
            if case.__class__.__module__ in blender_only:
                continue
            filtered.addTest(case)
    return filtered


def main() -> int:
    parser = argparse.ArgumentParser(description="Run iCity Smart City unit tests.")
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Measure line/branch coverage for iCity/smart_city (requires coverage package).",
    )
    args = parser.parse_args()

    REPORTS_DIR.mkdir(exist_ok=True)
    history_dir = REPORTS_DIR / "history"
    history_dir.mkdir(exist_ok=True)

    cov = None
    if args.coverage:
        try:
            import coverage as coverage_lib
        except ImportError:
            print("ERROR: install coverage first: pip install -r requirements-dev.txt", file=sys.stderr)
            return 2
        cov = coverage_lib.Coverage(config_file=str(REPO_ROOT / ".coveragerc"))
        cov.start()

    suite = discover_suite()
    runner = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult)
    start = time.perf_counter()
    result = runner.run(suite)
    total_time = time.perf_counter() - start

    write_junit_xml(result.records, total_time, REPORTS_DIR / "unit-tests.xml")
    write_markdown(result.records, total_time, REPORTS_DIR / "unit-report.md")
    write_taxonomy_summary(REPORTS_DIR)
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    write_markdown(result.records, total_time, history_dir / f"unit-report-{stamp}.md")

    if cov is not None:
        import io

        cov.stop()
        cov.save()
        buffer = io.StringIO()
        cov.report(file=buffer, show_missing=True)
        report_text = buffer.getvalue()
        print("\n" + report_text)
        cov.xml_report(outfile=str(REPORTS_DIR / "coverage.xml"))
        cov.html_report(directory=str(REPORTS_DIR / "coverage-html"))
        write_coverage_markdown(report_text.splitlines(), REPORTS_DIR / "coverage.md")
        print(f"Coverage reports: {REPORTS_DIR / 'coverage.md'}")

    print(f"\nReports written to {REPORTS_DIR}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
