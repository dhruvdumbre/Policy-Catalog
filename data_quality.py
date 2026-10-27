
import csv
import io
import math
from collections import Counter

from database import get_all_policies

ALLOWED_CATEGORIES = {
    "Motor", "Health", "Life", "Travel", "Home", "Other"
}

FIELDS = [
    "policy_type_id",
    "name",
    "category",
    "min_premium",
    "max_premium",
    "coverage_amount"
]


def run_quality_audit():
    """Audit database policies without changing stored records."""

    policies = get_all_policies()
    records = [dict(zip(FIELDS, policy)) for policy in policies]

    issues = []

    def add_issue(record, field, issue, severity="High"):
        issues.append({
            "policy_id": record.get("policy_type_id"),
            "policy_name": str(record.get("name") or ""),
            "field": field,
            "issue": issue,
            "severity": severity
        })

    # Detect duplicates ignoring capitalization and surrounding spaces.
    name_counts = Counter(
        (
            str(record.get("name") or "").strip().casefold(),
            str(record.get("category") or "").strip().casefold()
        )
        for record in records
        if str(record.get("name") or "").strip()
    )

    for record in records:
        name = record.get("name")
        category = record.get("category")

        if name is None or not str(name).strip():
            add_issue(record, "name", "Missing policy name")

        if category is None or not str(category).strip():
            add_issue(record, "category", "Missing category")
        elif str(category).strip().title() not in ALLOWED_CATEGORIES:
            add_issue(record, "category", "Invalid category")

        for field in (
            "min_premium",
            "max_premium",
            "coverage_amount"
        ):
            value = record.get(field)

            try:
                number = float(value)
                if not math.isfinite(number):
                    raise ValueError
            except (ValueError, TypeError):
                add_issue(record, field, "Missing or invalid number")
                continue

            if number <= 0:
                add_issue(record, field, "Value must be positive")

        try:
            minimum = float(record["min_premium"])
            maximum = float(record["max_premium"])

            if (
                math.isfinite(minimum)
                and math.isfinite(maximum)
                and minimum > 0
                and maximum > 0
                and minimum >= maximum
            ):
                add_issue(
                    record,
                    "min_premium / max_premium",
                    "Minimum premium must be less than maximum premium"
                )
        except (ValueError, TypeError, KeyError):
            pass

        try:
            maximum = float(record["max_premium"])
            coverage = float(record["coverage_amount"])

            if (
                math.isfinite(maximum)
                and math.isfinite(coverage)
                and maximum > 0
                and coverage > 0
                and coverage < maximum
            ):
                add_issue(
                    record,
                    "coverage_amount",
                    "Coverage is less than maximum premium"
                )
        except (ValueError, TypeError, KeyError):
            pass

        key = (
            str(name or "").strip().casefold(),
            str(category or "").strip().casefold()
        )

        if key[0] and name_counts[key] > 1:
            add_issue(
                record,
                "name / category",
                "Duplicate policy name within category"
            )

    affected_ids = {
        item["policy_id"] for item in issues
        if item["policy_id"] is not None
    }

    total = len(records)
    affected = len(affected_ids)

    return {
        "total_records": total,
        "issue_count": len(issues),
        "affected_records": affected,
        "clean_records": total - affected,
        "quality_score": (
            round((total - affected) / total * 100, 2)
            if total else 100.0
        ),
        "issues": issues
    }


def issues_to_csv(report):
    """Create a downloadable CSV report of quality issues."""

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "policy_id",
            "policy_name",
            "field",
            "issue",
            "severity"
        ]
    )

    writer.writeheader()
    writer.writerows(report["issues"])

    return output.getvalue()
