
import csv
import io
import math

from database import get_all_policies, create_policy

ALLOWED_CATEGORIES = {
    "Motor", "Health", "Life", "Travel", "Home", "Other"
}

REQUIRED_COLUMNS = {
    "name",
    "category",
    "min_premium",
    "max_premium",
    "coverage_amount"
}

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_ROWS = 5000


def parse_csv(file_bytes):
    """Extract CSV rows and normalize their column names."""

    if not file_bytes:
        raise ValueError("The uploaded CSV file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError("CSV file must not exceed 2 MB.")

    try:
        content = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("Please upload a UTF-8 encoded CSV file.")

    reader = csv.DictReader(io.StringIO(content))

    if not reader.fieldnames:
        raise ValueError("CSV headers are missing.")

    headers = [
        header.strip().lower() if header else ""
        for header in reader.fieldnames
    ]

    if len(headers) != len(set(headers)):
        raise ValueError("CSV contains duplicate column headers.")

    missing = REQUIRED_COLUMNS - set(headers)

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(sorted(missing))
        )

    rows = []

    for row_number, values in enumerate(reader, start=2):
        if row_number > MAX_ROWS + 1:
            raise ValueError(
                f"CSV exceeds the maximum of {MAX_ROWS} data rows."
            )

        # Skip completely blank lines.
        if not any(
            str(value or "").strip()
            for value in values.values()
        ):
            continue

        normalized = {
            (key.strip().lower() if key else ""): (
                value.strip() if value else ""
            )
            for key, value in values.items()
        }

        rows.append({
            "row_number": row_number,
            "data": normalized
        })

    return rows


def transform_and_validate(row):
    """Clean and validate one CSV record."""

    data = row["data"]
    errors = []

    name = data.get("name", "").strip()
    category = data.get("category", "").strip().title()

    if not name:
        errors.append("Policy name is required.")

    if category not in ALLOWED_CATEGORIES:
        errors.append(
            "Category must be Motor, Health, Life, Travel, Home, or Other."
        )

    numeric_values = {}

    for field in (
        "min_premium",
        "max_premium",
        "coverage_amount"
    ):
        try:
            value = float(data.get(field, ""))

            if not math.isfinite(value):
                raise ValueError

            numeric_values[field] = value

        except (ValueError, TypeError):
            errors.append(f"{field} must be a valid finite number.")

    if len(numeric_values) == 3:
        minimum = numeric_values["min_premium"]
        maximum = numeric_values["max_premium"]
        coverage = numeric_values["coverage_amount"]

        if minimum <= 0:
            errors.append("Minimum premium must be positive.")

        if maximum <= 0:
            errors.append("Maximum premium must be positive.")

        if minimum >= maximum:
            errors.append(
                "Minimum premium must be less than maximum premium."
            )

        if coverage <= 0:
            errors.append("Coverage amount must be positive.")

        if coverage < maximum:
            errors.append(
                "Coverage must be at least the maximum premium."
            )

    cleaned = {
        "name": name,
        "category": category,
        **numeric_values
    }

    return {
        "row_number": row["row_number"],
        "data": cleaned,
        "valid": not errors,
        "errors": errors
    }


def preview_csv(file_bytes):
    """Extract, transform, validate, and return a preview."""

    extracted = parse_csv(file_bytes)
    results = [
        transform_and_validate(row)
        for row in extracted
    ]

    # Detect duplicate policy names within this uploaded file.
    seen = set()

    for result in results:
        if not result["valid"]:
            continue

        data = result["data"]
        key = (data["name"].casefold(), data["category"])

        if key in seen:
            result["valid"] = False
            result["errors"].append(
                "Duplicate policy name and category in this CSV."
            )
        else:
            seen.add(key)

    # Detect policies that already exist in the database.
    existing = {
        (str(policy[1]).casefold(), policy[2])
        for policy in get_all_policies()
    }

    for result in results:
        if not result["valid"]:
            continue

        data = result["data"]
        key = (data["name"].casefold(), data["category"])

        if key in existing:
            result["valid"] = False
            result["errors"].append(
                "This policy name already exists in the database."
            )

    return {
        "total_rows": len(results),
        "valid_rows": sum(r["valid"] for r in results),
        "rejected_rows": sum(not r["valid"] for r in results),
        "rows": results
    }


def import_valid_rows(rows):
    """Revalidate and insert records; reject duplicate records safely."""

    if not isinstance(rows, list):
        raise ValueError("A list of previewed rows is required.")

    if len(rows) > MAX_ROWS:
        raise ValueError(f"Maximum {MAX_ROWS} rows can be imported.")

    inserted = 0
    rejected = []

    # Recheck the database because it may have changed since preview.
    existing = {
        (str(policy[1]).casefold(), policy[2])
        for policy in get_all_policies()
    }

    # Use a fresh connection for an atomic import.
    from database import get_connection

    connection = get_connection()

    try:
        connection.execute("BEGIN")

        for index, item in enumerate(rows, start=1):
            if not isinstance(item, dict):
                rejected.append({
                    "row_number": index,
                    "reason": "Invalid row format."
                })
                continue

            result = transform_and_validate({
                "row_number": index,
                "data": item
            })

            if not result["valid"]:
                rejected.append({
                    "row_number": index,
                    "reason": "; ".join(result["errors"])
                })
                continue

            data = result["data"]
            key = (data["name"].casefold(), data["category"])

            if key in existing:
                rejected.append({
                    "row_number": index,
                    "reason": "Policy already exists."
                })
                continue

            try:
                connection.execute(
                    """
                    INSERT INTO policy_types
                    (name, category, min_premium,
                     max_premium, coverage_amount)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        data["name"],
                        data["category"],
                        data["min_premium"],
                        data["max_premium"],
                        data["coverage_amount"]
                    )
                )

                existing.add(key)
                inserted += 1

            except Exception:
                rejected.append({
                    "row_number": index,
                    "reason": "Database rejected this policy."
                })

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "imported": inserted,
        "rejected": len(rejected),
        "errors": rejected
    }
