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
    return render_template("index.html")

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
    