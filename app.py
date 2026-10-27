from flask import Flask, jsonify, request, render_template
from flask import render_template
from flask import Flask, jsonify, request
from database import (
    initialize_database,
    create_policy,
    get_all_policies,
    get_policies_by_category,
    get_policy_by_id,
    update_policy,
    delete_policy
)

from analytics import get_analytics
from etl import preview_csv, import_valid_rows
from data_quality import run_quality_audit, issues_to_csv

app = Flask(__name__)

ALLOWED_CATEGORIES = [
    "Motor", "Health", "Life", "Travel", "Home", "Other"
]

POLICY_FIELDS = [
    "policy_type_id",
    "name",
    "category",
    "min_premium",
    "max_premium",
    "coverage_amount"
]


def policy_to_dict(policy):
    """Convert a database tuple into a JSON-friendly dictionary."""
    return dict(zip(POLICY_FIELDS, policy))


def validate_policy(data):
    """Validate incoming policy details."""

    if not isinstance(data, dict):
        raise ValueError("A JSON object is required.")

    name = data.get("name", "")
    category = data.get("category", "")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Policy name cannot be empty.")

    if not isinstance(category, str):
        raise ValueError("Invalid category.")

    name = name.strip()
    category = category.strip().title()

    if category not in ALLOWED_CATEGORIES:
        raise ValueError("Invalid category.")

    try:
        min_premium = float(data["min_premium"])
        max_premium = float(data["max_premium"])
        coverage = float(data["coverage_amount"])
    except (KeyError, ValueError, TypeError):
        raise ValueError("Enter valid premium and coverage amounts.")

    import math

    if not all(math.isfinite(value) for value in
               (min_premium, max_premium, coverage)):
        raise ValueError("Amounts must be finite numbers.")

    if min_premium <= 0 or max_premium <= 0:
        raise ValueError("Premium amounts must be positive.")

    if min_premium >= max_premium:
        raise ValueError(
            "Minimum premium must be less than maximum premium."
        )

    if coverage <= 0:
        raise ValueError("Coverage amount must be positive.")

    if coverage < max_premium:
        raise ValueError(
            "Coverage must be at least the maximum premium."
        )

    return name, category, min_premium, max_premium, coverage


@app.route("/api/policies", methods=["GET"])
def list_policies():
    """Return all policies or filter by category."""

    category = request.args.get("category", "").strip()

    if category:
        category = category.title()

        if category not in ALLOWED_CATEGORIES:
            return jsonify({"error": "Invalid category."}), 400

        policies = get_policies_by_category(category)
    else:
        policies = get_all_policies()

    return jsonify([policy_to_dict(p) for p in policies])


@app.route("/api/policies/<int:policy_id>", methods=["GET"])
def get_policy(policy_id):
    """Return a single policy by ID."""

    policy = get_policy_by_id(policy_id)

    if policy is None:
        return jsonify({"error": "Policy not found."}), 404

    return jsonify(policy_to_dict(policy))


@app.route("/api/policies", methods=["POST"])
def add_policy():
    """Create a new policy."""

    try:
        values = validate_policy(request.get_json(silent=True))
        policy_id = create_policy(*values)

        return jsonify({
            "message": "Policy created successfully.",
            "policy_type_id": policy_id
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/policies/<int:policy_id>", methods=["PUT"])
def edit_policy(policy_id):
    """Update an existing policy."""

    if get_policy_by_id(policy_id) is None:
        return jsonify({"error": "Policy not found."}), 404

    try:
        values = validate_policy(request.get_json(silent=True))
        updated = update_policy(policy_id, *values)

        if not updated:
            return jsonify({"error": "Policy not found."}), 404

        return jsonify({"message": "Policy updated successfully."})

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/policies/<int:policy_id>", methods=["DELETE"])
def remove_policy(policy_id):
    """Delete a policy by ID."""

    deleted = delete_policy(policy_id)

    if not deleted:
        return jsonify({"error": "Policy not found."}), 404

    return jsonify({"message": "Policy deleted successfully."})

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/policies")
def policies_page():
    return render_template("index.html")

@app.route("/api/analytics", methods=["GET"])
def analytics_data():
    try:
        return jsonify(get_analytics())
    except Exception:
        app.logger.exception("Failed to calculate analytics")
        return jsonify({
            "error": "Unable to calculate analytics."
        }), 500
        
@app.route("/analytics")
def analytics_page():
    return render_template("analytics.html")

@app.route("/import")
def import_page():
    return render_template("import.html")


@app.route("/api/import/preview", methods=["POST"])
def preview_import():
    if "file" not in request.files:
        return jsonify({"error": "Please select a CSV file."}), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:
        return jsonify({"error": "No file selected."}), 400

    if not uploaded_file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are allowed."}), 400

    try:
        result = preview_csv(uploaded_file.read())
        return jsonify(result)

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("CSV preview failed")
        return jsonify({"error": "Unable to process this CSV file."}), 500


@app.route("/api/import/commit", methods=["POST"])
def commit_import():
    payload = request.get_json(silent=True) or {}

    try:
        result = import_valid_rows(payload.get("rows"))
        return jsonify(result)

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("CSV import failed")
        return jsonify({"error": "Unable to import CSV records."}), 500


@app.route("/quality")
def quality_page():
    return render_template("quality.html")


@app.route("/api/quality", methods=["GET"])
def quality_data():
    try:
        return jsonify(run_quality_audit())
    except Exception:
        app.logger.exception("Data quality audit failed")
        return jsonify({
            "error": "Unable to run the data quality audit."
        }), 500


@app.route("/api/quality/report.csv", methods=["GET"])
def download_quality_report():
    try:
        report = run_quality_audit()
        csv_content = issues_to_csv(report)

        from flask import Response

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                    "attachment; filename=data_quality_report.csv"
            }
        )
    except Exception:
        app.logger.exception("Quality report export failed")
        return jsonify({
            "error": "Unable to generate the quality report."
        }), 500

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
    