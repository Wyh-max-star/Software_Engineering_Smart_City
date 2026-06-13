"""Build ``test-reports/taxonomy-summary.md`` from persisted unit test results."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"
sys.path.insert(0, str(TESTS_DIR))

from test_catalog import MOCK_SCOPES, SUBJECTS, group_records_by_subject, subject_id_for  # noqa: E402
from test_markers import BLACK_BOX, BOX_LABELS, GRAY_BOX, WHITE_BOX  # noqa: E402


def _parse_unit_xml(path: Path) -> list[dict]:
    if not path.exists():
        return []
    root = ET.parse(path).getroot()
    records = []
    for case in root.findall("testcase"):
        status = "pass"
        if case.find("failure") is not None:
            status = "fail"
        elif case.find("error") is not None:
            status = "error"
        elif case.find("skipped") is not None:
            status = "skip"
        records.append(
            {
                "classname": case.get("classname", ""),
                "name": case.get("name", ""),
                "status": status,
                "box": case.get("classification", WHITE_BOX),
            }
        )
    return records


def _subject_rows(records: list[dict], box: str) -> list[str]:
    grouped = group_records_by_subject(records)
    subject_order = {sid: idx for idx, sid in enumerate(SUBJECTS)}
    rows = []
    for (record_box, sid), items in sorted(
        grouped.items(),
        key=lambda item: subject_order.get(item[0][1], 999),
    ):
        if record_box != box:
            continue
        subj = SUBJECTS.get(sid)
        if not subj:
            continue
        counts = Counter(r["status"] for r in items)
        ok = counts["fail"] == 0 and counts["error"] == 0
        icon = "✅" if ok else "❌"
        rows.append(
            f"| {subj['name']} | `{subj['product']}` | {subj['scope']} | "
            f"{len(items)} | {counts['pass']} | {icon} |"
        )
    return rows


def write_taxonomy_summary(reports_dir: Path) -> Path:
    unit_records = _parse_unit_xml(reports_dir / "unit-tests.xml")

    unit_by_box: dict[str, Counter] = {WHITE_BOX: Counter(), GRAY_BOX: Counter(), BLACK_BOX: Counter()}
    for record in unit_records:
        box = record.get("box", WHITE_BOX)
        if box not in unit_by_box:
            unit_by_box[box] = Counter()
        unit_by_box[box]["total"] += 1
        unit_by_box[box][record["status"]] += 1

    mock_stats: list[tuple[str, int, int]] = []
    for pattern, label in MOCK_SCOPES:
        matched = [r for r in unit_records if pattern in r["classname"]]
        if not matched:
            continue
        passed = sum(1 for r in matched if r["status"] == "pass")
        mock_stats.append((label, len(matched), passed))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 测试分类汇总（白盒 / 灰盒 / 黑盒）",
        "",
        f"- 更新时间：{timestamp}",
        "",
        "> 按**测试对象**（被测模块/功能）描述测什么；不列出测试代码文件或方法名。",
        "",
        "## 分类定义",
        "",
        "| 类型 | 说明 | 运行方式 |",
        "|---|---|---|",
        "| **白盒** | 知悉内部实现，测函数/分支/数据结构 | `python tools/run_tests.py --coverage` |",
        "| **灰盒** | 跨模块不变式、场景编排、前后端数据 | 同上 |",
        "| **黑盒** | 仅验证算子输入→`FINISHED`/`CANCELLED` 契约 | 同上（Mock 流水线） |",
        "",
        "> 自动化测试 100% 使用 `unittest.mock`；不依赖真实 Blender。",
        "",
        "## 总体统计",
        "",
        "| 分类 | 用例数 | 通过 | 失败 | 错误 | 跳过 |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for box in (WHITE_BOX, GRAY_BOX, BLACK_BOX):
        stats = unit_by_box.get(box, Counter())
        lines.append(
            f"| {BOX_LABELS[box]} | {stats.get('total', 0)} | {stats.get('pass', 0)} | "
            f"{stats.get('fail', 0)} | {stats.get('error', 0)} | {stats.get('skip', 0)} |"
        )

    for box in (WHITE_BOX, GRAY_BOX, BLACK_BOX):
        rows = _subject_rows(unit_records, box)
        if not rows:
            continue
        lines += [
            "",
            f"## {BOX_LABELS[box]} — 测试对象",
            "",
            "| 测试对象 | 被测模块/功能 | 测什么 | 用例数 | 通过 | 结果 |",
            "|---|---|---|---:|---:|---|",
            *rows,
        ]

    if mock_stats:
        lines += [
            "",
            "## Mock 隔离范围",
            "",
            "| 隔离对象 | 用例数 | 通过 |",
            "|---|---:|---:|",
        ]
        for label, total, passed in mock_stats:
            lines.append(f"| {label} | {total} | {passed} |")

    coverage_md = reports_dir / "coverage.md"
    if coverage_md.exists():
        lines += ["", "## 代码覆盖率", "", "详见 [`coverage.md`](coverage.md)。", ""]

    lines += [
        "## 可选：真实 Blender 冒烟",
        "",
        "可在本地 Blender 中额外验证算子与场景图效果；**不计入**上述 Mock 自动化统计。",
        "",
    ]
    out = reports_dir / "taxonomy-summary.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    reports_dir = REPO_ROOT / "test-reports"
    reports_dir.mkdir(exist_ok=True)
    path = write_taxonomy_summary(reports_dir)
    print(f"Updated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
